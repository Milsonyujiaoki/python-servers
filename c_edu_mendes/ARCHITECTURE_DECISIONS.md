# REGISTRO DE DECISÕES ARQUITETURAIS

Este documento registra as decisões arquiteturais importantes tomadas durante o desenvolvimento do Barbearia SaaS, conforme recomendado por práticas de arquitetura de software (inspirado em Michael Nygard e outros).

## Formato de Registro

Cada decisão segue o formato:
- **ID**: Número sequencial único
- **Título**: Descrição concisa da decisão
- **Status**: Proposta | Aceita | Obsoleta | Supersedida
- **Contexto**: O problema ou oportunidade que levou à decisão
- **Decisão**: O que foi decidido
- **Consequências**: Impactos positivos e negativos (consequências diretas)
- **Implicações**: Como isso afeta outras decisões ou áreas

---

## ADR-001: Adoção de Arquitetura de Camadas Limpas (Clean Architecture)
- **Status**: Aceita
- **Data**: 2024-06-26
- **Contexto**: 
  - Precisamos garantir que as regras de negócio permaneçam independentes de frameworks técnicos
  - Queremos evitar o "framework lock-in" que dificultaria mudanças futuras (ex: trocar de FastAPI para Django, ou de PostgreSQL para MongoDB)
  - A equipe precisa de clareza sobre onde colocar diferentes tipos de código
- **Decisão**: 
  Adotar a arquitetura de camadas limpas com as seguintes divisões estritas em cada módulo:
  - **Presentation Layer**: Apenas翻译 HTTP requests/responses, validação de entrada, códigos de status HTTP
  - **Application Layer**: Casos de uso (use services), orquestração de fluxos de negócio, transações, publicação de eventos
  - **Domain Layer**: Entidades, value objects, serviços de domínio (regras de negócio puras), interfaces de repositório
  - **Infrastructure Layer**: Implementações de detalhes externos (ORM, gateways de APIs externas, cache, mensageria)
- **Consequências**:
  - Positivas: 
    - Regras de negócio podem ser testadas sem nenhum framework
    - Facilita a troca de tecnologias no futuro
    - Melhor separação de preocupações torna o código mais fácil de entender
    - Facilita o trabalho paralelo entre equipes (domínio vs infraestrutura)
  - Negativas:
    - Sobrecarga inicial de criar mais camadas e interfaces
    - Pode parecer excessivamente cerimonial para funcionalidades muito simples
- **Implicações**:
  - Afeta como escreveremos testes (mais foco em testes de unidade pura para domínio)
  - Influenciará nossa estratégia de evolução para microserviços (domínio pode ser compartilhado)
  - Exige disciplina da equipe para não vazar dependências de framework para o domínio

---

## ADR-002: Adoção de Vertical Slicing com Monolito Modular
- **Status**: Aceita
- **Data**: 2024-06-26
- **Contexto**:
  - Precisamos entregar valor de negócio rapidamente (mentalidade de startup)
  - Queremos evitar a complexidade prematura de microserviços
  - Ainda assim, precisamos de uma arquitetura que possa evoluir conforme o sistema cresce
  - Experiências passadas mostram que monolito sem limites claros torna-se difícil de manter
- **Decisão**:
  Adotar um monolito organizado em "vertical slices" (fatias verticais) onde cada funcionalidade de negócio é um módulo completo contendo todas as camadas necessárias (presentation, application, domain, infrastructure).
  - Cada módulo é responsável por um domínio de negócio completo (ex: agendamento, pagamentos, CRM)
  - Módulos comunicam-se apenas através de interfaces bem definidas (evitando compartilhamento direto de banco de dados)
  - Mantemos a capacidade de extrair módulos para serviços separados posteriormente quando necessário
- **Consequências**:
  - Positivas:
    - Entrega incremental de valor (cada módulo pode ser desenvolvido e deployado independentemente)
    - Isolamento de falhas (problemas em um módulo não afetam outros necessariamente)
    - Clareza de propriedade (equipes podem ter responsabilidade clara por módulos específicos)
    - Caminho claro para evolução (extrair para microserviços quando medida mostrar necessidade)
  - Negativas:
    - Possível duplicação de alguns códigos de infraestrutura entre módulos
    - Necessidade de disciplina para evitar acoplamento implícito entre módulos
- **Implicações**:
  - Afeta como organizamos nossas equipes (possível organização por domínio de negócio)
  - Determinará nossa estratégia de teste (testes podem ser focados por módulo)
  - Influenciará como lidamos com mudanças que afetam múltiplos domínios (precisaremos de coordenação)

---

## ADR-003: Uso de Value Objects para Conceitos de Domínio
- **Status**: Aceita
- **Data**: 2024-06-26
- **Contexto**:
  - Temos conceitos de domínio que são mais do que simples tipos de dado (ex: telefone, e-mail, preço)
  - Esses conceitos têm regras de validação e formatação específicas
  - Queremos evitar a "primitive obsession" onde usamos strings ou números básicos para representar conceitos complexos
- **Decisão**:
  Implementar Value Objects imutáveis para conceitos de domínio que possuem:
  - Validação de formato (ex: formato de telefone brasileiro)
  - Comportamento associado (ex: formatação para exibição)
  - Sem identidade própria (dois VOs com mesmos valores são considerados iguais)
  - Exemplos iniciais: PhoneNumber, Email, Money, ServicePrice, AppointmentId
- **Consequências**:
  - Positivas:
    - Encapsula validação e lógica relacionada ao conceito
    - Evita espalhamento de lógica de validação pelo código
    - Torna impossível criar objetos inválidos (estado sempre válido após criação)
    - Melhora a legibilidade do código de domínio
  - Negativas:
    - Mais verboso que usar tipos primitivos diretamente
    - Requer mais classes para conceitos simples
- **Implicações**:
  - Afeta como modelamos entidades (usaremos VOs como campos em vez de tipos primitivos)
  - Influenciará nossos testes (mais foco em testes de VOs)
  - Exige que seja claro quando algo é uma Entidade (identidade) vs Value Object (valor)

---

## ADR-004: Estratégia de Persistência com Repository Pattern
- **Status**: Aceita
- **Data**: 2024-06-26
- **Contexto**:
  - Precisamos isolar as regras de negócio dos detalhes de acesso a dados
  - Queremos ter a flexibilidade de mudar estratégias de persistência no futuro
  - Experiências passadas mostram que acesso direto a ORM em serviços de negócio cria acoplamento difícil de quebrar
- **Decisão**:
  Utilizar o padrão Repository em todas as camadas de domínio:
  - Definir interfaces de repositório na camada de `domain/repositories/`
  - Implementar essas interfaces na camada de `infrastructure/db/` ou `infrastructure/cache/`
  - Os repositórios lidam apenas com objetos de domínio (entidades, value objects)
  - Nenhum detalhe de ORM, SQL ou estrutura de tabela vaza para camadas de domínio ou aplicação
- **Consequências**:
  - Positivas:
    - Permite substituir implementações de persistência sem afetar domínio ou aplicação
    - Facilita testes de domínio e aplicação (podemos mockar repositórios facilmente)
    - Centraliza lógica de consulta em um local bem definido
    - Melhora a separação de preocupações
  - Negativas:
    - Adiciona uma camada de abstração que pode parecer desnecessária para consultas simples
    - Pode haver casos onde queremos expor recursos específicos do ORM (necessitaremos de estratégias de escape)
- **Implicações**:
  - Afeta como escrevemos serviços de domínio (dependem de interfaces de repositório)
  - Determinará nossa estratégia de teste (mocks de repositório para testes de aplicação)
  - Exige que seja claro o que pertence ao domínio vs infraestrutura em consultas complexas

---

## ADR-005: Uso de Application Services para Orquestração de Transações
- **Status**: Aceita
- **Data**: 2024-06-26
- **Contexto**:
  - Casos de uso frequentemente precisam coordenar múltiplas operações que devem ser atômicas
  - Precisamos de um local claro para gerenciar transações de banco de dados
  - Não queremos que casos de uso saibam de detalhes de transação (deveria ser responsabilidade da camada de aplicação)
- **Decisão**:
  Implementar Application Services na camada de `application/services/` que:
  - Orquestram a execução de um ou mais casos de uso
  - Gerenciam transações de banco de dados (abrir, commitar, rollback)
  - Publicam eventos de domínio após conclusão bem-sucedida
  - Lidem com preocupações transversais como logging, segurança, não relacionadas ao negócio específico
  - Casos de uso permanecem focados exclusivamente na lógica de negócio específica
- **Consequências**:
  - Positivas:
    - Separa claramente preocupações de transação da lógica de negócio pura
    - Facilita o reuso de casos de uso em diferentes contextos de transação
    - Centraliza tratamento de erros e logging relacionados à transação
    - Torna os casos de uso mais simples e focados
  - Negativas:
    - Adiciona outra camada que desenvolvedores precisam entender
    - Pode ser excessivamente detalhada para casos de uso muito simples
- **Implicações**:
  - Afeta como estruturamos nossos casos de uso (devem ser puros e focados)
  - Determinará onde colocaremos lógica de transação (nos application services)
  - Exige consistência na implementação de gerenciamento de transação

---

## ADR-006: Estratégia de Comunicação Síncrona Inicial com Evolução para Assíncrona
- **Status**: Aceita
- **Data**: 2024-06-26
- **Contexto**:
  - Precisamos lançar rapidamente um MVP funcional
  - Comunicação síncrona (REST/HTTP) é mais simples de implementar e depurar inicialmente
  - No entanto, antecipamos necessidade de comunicação assíncrona para escalabilidade e resiliência futuras
  - Experiências mostram que adicionar mensagem assíncrona tarde pode ser caro e arriscado
- **Decisão**:
  Começar com comunicação síncrona (REST) entre módulos dentro do monolito, mas projetar para futura evolução assíncrona:
  - Definir eventos de domínio claros no `shared/events/` (ex: AppointmentBooked, PaymentProcessed)
  - Camadas de aplicação publicam esses eventos após operações exitosas
  - Implementar um event publisher simples no início (pode ser síncrono/log-only)
  - Projetar para que o event publisher possa ser facilmente substituído por uma implementação assíncrona futura (Redis Pub/Sub, RabbitMQ, etc.)
  - Nunca permitir que casos de uso ou serviços de domínio dependam diretamente de mecanismos de comunicação específicos
- **Consequências**:
  - Positivas:
    - Permite início simples com comunicação síncrona direta
    - Caminho claro para evolução para arquitetura orientada a eventos
    - Desacoplamento lógico mesmo com implementação síncrona inicial
    - Preparado para resiliência e escalabilidade futura
  - Negativas:
    - Overhead mínimo de definição de eventos mesmo quando não usados inicialmente
    - Requer disciplina para não fazer chamadas diretas entre módulos contornando o mecanismo de eventos
- **Implicações**:
  - Afeta como projetamos nossos use cases (devem publicar eventos após sucesso)
  - Determinará onde colocaremos lógica de publicação de evento (application services)
  - Exige que eventos sejam imutáveis e contenham apenas dados necessários (não expor entidades internas)

---

## ADR-007: Adoção do Padrão Strategy para Pagamentos
- **Status**: Aceita
- **Data**: 2024-06-26
- **Contexto**:
  - Precisamos suportar múltiplos métodos de pagamento (Pix, cartão de crédito, boleto, dinheiro)
  - Cada método tem lógica de processamento diferente
  - Queremos poder adicionar novos métodos de pagamento sem modificar código existente
  - Experiências passadas mostram que condicionais grandes (if/else ou switch) para pagamento se tornam difíceis de manter
- **Decisão**:
  Implementar o padrão Strategy para processamento de pagamentos:
  - Definir uma interface `PaymentStrategy` no domínio de pagamentos
  - Criar implementações concretas para cada método (`PixStrategy`, `CreditCardStrategy`, `BoletoStrategy`, `CashStrategy`)
  - Usar um contexto (`PaymentProcessor`) que seleciona a estratégia apropriada em tempo de execução
  - Permitir que estratégias sejam configuradas ou injetadas (via dependency injection ou configuração)
  - Isolar detalhes de gateways específicos nas implementações de estratégia (adapter pattern dentro da strategy)
- **Consequências**:
  - Positivas:
    - Adicionar novos métodos de pagamento não requer alteração em código existente (aberto/fechado)
    - Isola complexidade de cada gateway de pagamento
    - Facilita testes (podemos mockar estratégias específicas)
    - Permite seleção dinâmica de estratégia baseado em contexto (valor, horário, preferência do cliente)
  - Negativas:
    - Mais classes para gerenciar inicialmente
    - Indireção adicional na chamada de pagamento
- **Implicações**:
  - Afeta como estruturamos o módulo de pagamentos
  - Determinará onde colocaremos lógica de seleção de estratégia
  - Exige que seja claro o que é parte da estratégia (algoritmo de pagamento) vs contexto (quando escolher cada estratégia)

---

## ADR-008: Estratégia de Tratamento de Erros com Exceções de Domínio
- **Status**: Aceita
- **Data**: 2024-06-26
- **Contexto**:
  - Precisamos distinguir entre erros de violação de regra de negócio (ex: horário indisponível) e falhas técnicas (ex: banco indisponível)
  - Queremos fornecer mensagens de erro significativas aos usuários finais
  - Experiências mostram que usar exceções genéricas ou códigos de erro torna difícil tratar diferentes tipos de falha de forma adequada
- **Decisão**:
  Implementar hierarquia de exceções de domínio:
  - Criar exceções base de domínio (`DomainException`)
  - Criar exceções específicas para tipos comuns de violação de regra de negócio:
    - `BusinessRuleViolationException` (para regras como horário indisponível)
    - `InvalidStateException` (para quando objeto está em estado inválido para operação)
    - `NotFoundException` (para entidades não encontradas)
    - `ValidationException` (para falhas de validação de entrada)
  - Camadas de aplicação e apresentação capturam essas exceções e mapeiam para respostas apropriadas:
    - Exceções de negócio → HTTP 400 (Bad Request) com mensagem amigável
    - Exceções de infraestrutura → HTTP 500 (Internal Server Error) com log detalhado
    - Exceções de não encontrado → HTTP 404 (Not Found)
- **Consequências**:
  - Positivas:
    - Permite tratamento diferenciado de tipos de falha
    - Fornece mensagens de erro significativas aos usuários
    - Evita vazamento de detalhes de infraestrutura para clientes (segurança)
    - Torna o código de tratamento de erro mais explícito e legível
  - Negativas:
    - Requer criação de várias classes de exceção
    - Desenvolvedores precisam aprender quando usar cada tipo
- **Implicações**:
  - Afeta como implementamos validação e verificações de regra de negócio
  - Determinará onde capturar e tratar exceções em cada camada
  - Exige consistência na hierarquia de exceções usadas em todo o sistema

---

## Próximas Decisões a Serem Tomadas

À medida que avançamos no desenvolvimento, esperamos tomar decisões adicionais em áreas como:

1. **Estratégia de Cache** (ADR-009): Quando e como usar Redis vs cache em memória vs sem cache
2. **Abordagem de Migração de Banco** (ADR-010): Ferramentas (Alembic, Flyway) e estratégias de versionamento
3. **Política de Logging e Monitoramento** (ADR-011): Estrutura de logs, níveis, integração com sistemas de observabilidade
4. **Estratégia de Versionamento de API** (ADR-012): Versionamento por URL, header ou outro mecanismo
5. **Abordagem de Documentação de API** (ADR-013): OpenAPI/Swagger, geração automática vs manual
6. **Estratégia de Testes de Performance/Carga** (ADR-014): Quando e como realizar testes de carga
7. **Política de Segurança** (ADR-015): Autenticação, autorização, proteção contra ataques comuns
8. **Estratégia de Deploy e Rollback** (ADR-016): Blue/green, canary, rollback automático

Cada decisão futura será registrada neste seguindo o mesmo formato estabelecido acima.

---
*Última atualização: 2024-06-26*
*Este documento é um artefato vivo que evolui conforme nosso entendimento do sistema e do domínio de negócio amadurece.*
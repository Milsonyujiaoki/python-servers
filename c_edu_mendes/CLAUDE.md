# Plano: Ajude a revisar e melhorar o projeto, além de buscar skills para ajudar ao desenvolvimento

## Contexto
O usuário solicita ajuda para revisar e melhorar seu projeto FastAPI (`c-edu-mendes`), além de buscar skills que possam auxiliar no desenvolvimento. Já foi criado um arquivo CLAUDE.md com orientações básicas para o Code Claude trabalhar neste repositório.

## Resumo da Análise

### Segurança (Agente 1)
- **Crítico**: SECRET_KEY hardcodeado e fraco ("mysecretkey") em app/security.py
- **Crítico**: Falta de variáveis de ambiente para configurações de segurança críticas
- **Alto**: Ausência de headers de segurança HTTP (X-Frame-Options, X-Content-Type-Options, etc.)
- **Alto**: Falta de rate limiting, especialmente em endpoints de autenticação
- **Alto**: Configuração CORS ausente (permite todas as origens por padrão)
- **Médio**: Docker executa como root sem usuário não-root
- **Médio**: NGINX lacks security headers
- **Baixo**: Tratamento de erros adequado mas poderia ser melhorado com logging estruturado

### Qualidade de Código (Agente 2)
- **Alto**: Estrutura geral organizada mas poderia beneficiar-se de camadas de serviço
- **Médio**: app/models.py usa SQLAlchemy 2.0 corretamente mas tem inconsistência de tipo em birth_date
- **Alto**: app/schemas.py tem bug na validação de CNPJ (variável indefinida) e validação de senha comentada
- **Baixo**: Boa aderência ao PEP 8 com configuracoes do Ruff/MyPy
- **Baixo**: Uso correto de injeção de dependência do FastAPI
- **Baixo**: Tratamento de erros adequado mas poderia ser padronizado
- **Médio**: Testes bons mas poderiam ser melhorados com cobertura e assertions mais detalhadas
- **Alto**: Documentação insuficiente (muitas funções sem docstrings)
- **Alto**: Oportunidades de refatoração: extrair validações para utilitários, padronizar respostas
- **Baixo**: Uso adequado de assíncrono/síncrono
- **Alto**: Falta de versionamento de API

### Arquitetura e Skills (Agente 3)
- **Alto**: Arquitetura camada básica mas falta camada de serviço e repositório
- **Alto**: Apenas um modelo de dados (User) - falta demonstração de relacionamentos
- **Alto**: Design de API REST básico - falta versionamento, padronização de respostas
- **Médio**: Implementações básicas de WebSocket e SSE - falta autenticação, gerenciamento de conexões
- **Alto**: Oportunidades de melhoria: adicionar camadas de serviço/repositório, melhorar modelos
- **Médio**: Configuração poderia se beneficiar de validação customizada e ambientes específicos
- **Alto**: Docker poderia ser melhorado com build multi-stage, usuário non-root, healthchecks
- **Skills úteis**: code-review, simplify, fewer-permission-prompts, update-config, verify
- **Oportunidades de performance**: caching, query optimization, response compression
- **Oportunidades de padronização**: respostas padronizadas, tratamento de erros, dependências comuns
- **Crítico**: CI/CD ausente - recomendado implementar GitHub Actions ou similar

## Plano de Ação Recomendado

### I. Correções Críticas (Semana 1)
1. **Corrigir SECRET_KEY**
   - Mover SECRET_KEY para variável de ambiente em app/settings.py
   - Atualizar .env.example com variável necessária
   - Remover valor hardcodeado de app/security.py

2. **Corrigir Validação de CNPJ**
   - Fixar referência a variável indefinida em app/schemas.py linha 210
   - Corrigir erro lógico no cálculo de digito_2

3. **Implementar Versionamento de API**
   - Adicionar prefixo /api/v1/ a todas as rotas em app/app.py

4. **Adicionar Headers de Segurança**
   - Adicionar X-Frame-Options, X-Content-Type-Options, Referrer-Policy, Content-Security-Policy

### II. Melhorias de Arquitetura (Semana 2-3)
5. **Implementar Camada de Serviço**
   - Criar diretório app/services/ e mover lógica de negócio

6. **Padronizar Respostas**
   - Criar formato consistente para respostas de sucesso e erro

7. **Implementar Rate Limiting**
   - Adicionar rate limiting especialmente em endpoints de autenticação

8. **Melhorar Configuração**
   - Adicionar validação customizada para campos sensíveis em app/settings.py

9. **Segurança do Docker**
   - Adicionar usuário non-root, build multi-stage, healthcheck

### III. Melhorias de Qualidade (Semana 3-4)
10. **Melhorar Documentação**
    - Adicionar docstrings abrangentes a todas as funções e classes públicas

11. **Refatorar Código**
    - Extrair funções de validação comuns para app/utils/validators.py

12. **Melhorar Testes**
    - Aumentar cobertura e adicionar assertions mais detalhadas

13. **Implementar CI/CD**
    - Adicionar workflow do GitHub Actions para testes automatizados

## Skills Recomendados para Desenvolvimento Contínuo

1. **`code-review`** (Altamente Recomendado)
   - Identificar problemas de qualidade, segurança e arquitetura
   - Aplicar antes de fazer commits

2. **`simplify`** (Altamente Recomendado)
   - Identificar oportunidades para simplificar código complexo
   - Aplicar periodicamente para melhorar legibilidade

3. **`fewer-permission-prompts`** (Altamente Recomendado)
   - Reduzir interrupções durante desenvolvimento
   - Configurar uma vez para melhorar experiência

4. **`update-config`** (Altamente Recomendado)
   - Gerenciar configurações de ferramentas e do projeto
   - Atualizar configurações conforme necessário

5. **`verify`** (Moderadamente Recomendado)
   - Validar que mudanças funcionam como esperado
   - Usar após implementar melhorias significativas

Este plano aborda os problemas mais críticos primeiro, seguindo uma abordagem de risco e impacto, e fornece um caminho claro para melhorar a segurança, qualidade e arquitetura do projeto.
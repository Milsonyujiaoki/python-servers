CREATE TABLE IF NOT EXISTS pessoas (
	id UUID PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
	birth_date DATE NOT NULL,
	cpf CHAR(11) NOT NULL,
	CONSTRAINT unique_cpf UNIQUE (cpf)
	 );
	                  

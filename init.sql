CREATE TABLE livros (
    isbn VARCHAR PRIMARY KEY,
    autor VARCHAR NOT NULL,
    titulo VARCHAR NOT NULL
);

INSERT INTO livros (isbn, autor, titulo) VALUES 
('12345', 'valente', 'Engenharia de Software Moderna'),
('67890', 'fowler', 'Patterns of Enterprise Application Architecture'),
('111213', 'gof', 'Design Patterns');

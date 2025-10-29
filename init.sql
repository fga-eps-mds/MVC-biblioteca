SET client_min_messages TO WARNING;

CREATE SCHEMA IF NOT EXISTS biblioteca;

CREATE EXTENSION IF NOT EXISTS pg_trgm WITH SCHEMA public;

DO $$
BEGIN
  EXECUTE format('ALTER DATABASE %I SET search_path TO biblioteca, public', current_database());
END$$;

CREATE TABLE IF NOT EXISTS biblioteca.livros (
    isbn   VARCHAR(20) PRIMARY KEY,
    titulo VARCHAR(255) NOT NULL,
    autor  VARCHAR(255) NOT NULL
);

INSERT INTO biblioteca.livros (isbn, titulo, autor) VALUES
('12345', 'Engenharia de Software Moderna', 'valente'),
('67890', 'Patterns of Enterprise Application Architecture', 'fowler'),
('111213', 'Design Patterns', 'gof') ON CONFLICT (isbn) DO NOTHING;


-- SELECT count(*) AS total_livros FROM biblioteca.livros;
-- SELECT * FROM biblioteca.livros WHERE autor ILIKE '%fowler%';

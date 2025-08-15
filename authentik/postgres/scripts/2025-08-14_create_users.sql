CREATE DATABASE authentik_db;

CREATE ROLE authentik WITH
    LOGIN
    ENCRYPTED PASSWORD 'md5c7bba660e19999bab7e32bb9ec317eb1';
GRANT ALL PRIVILEGES ON DATABASE authentik_db TO authentik;
\c authentik postgres
GRANT ALL ON SCHEMA public TO authentik;
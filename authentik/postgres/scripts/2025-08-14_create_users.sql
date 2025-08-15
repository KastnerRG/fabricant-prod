CREATE DATABASE authentik_db;

CREATE ROLE authentik WITH
    LOGIN
    ENCRYPTED PASSWORD 'SCRAM-SHA-256$4096:hTZDgCEdj6ygbNEgktVjcw==$ZHPpYXMxvX5RvsUUlu+RVWaSzlHl5gsxE0h4yBUsHL4=:KjW1TAQD0awpAF2XmwOWPBW8/Ea2EyDuFcUFdSsk2ME=';
GRANT ALL PRIVILEGES ON DATABASE authentik_db TO authentik;
\c authentik_db postgres
GRANT ALL ON SCHEMA public TO authentik;

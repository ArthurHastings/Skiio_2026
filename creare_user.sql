CREATE USER skiio_user WITH PASSWORD 'parola_skiio_123';
ALTER ROLE skiio_user SET client_encoding TO 'utf8';
ALTER ROLE skiio_user SET default_transaction_isolation TO 'read committed';
ALTER ROLE skiio_user SET timezone TO 'UTC';

CREATE DATABASE skiio_db OWNER skiio_user;
GRANT ALL PRIVILEGES ON DATABASE skiio_db TO skiio_user;
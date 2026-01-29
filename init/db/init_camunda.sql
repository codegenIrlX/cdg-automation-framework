DO
$$
BEGIN
  IF NOT EXISTS (SELECT 1 FROM pg_roles WHERE rolname = 'camunda') THEN
    CREATE ROLE camunda LOGIN PASSWORD 'camunda';
  END IF;
END
$$;

SELECT format('CREATE DATABASE %I OWNER %I', 'camunda', 'camunda')
WHERE NOT EXISTS (SELECT 1 FROM pg_database WHERE datname = 'camunda')
\gexec

ALTER DATABASE camunda OWNER TO camunda;
GRANT ALL PRIVILEGES ON DATABASE camunda TO camunda;

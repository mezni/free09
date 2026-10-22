-- Roles, schemas, and grants for the four domain services.
--
-- ADR-0001 gives each service its own role and schema inside one database.
-- D-01 fixes the four schemas and their owning services; D-04 forbids
-- cross-schema foreign keys; D-09 fixes the deletion rules.
--
-- Roles are cluster-level objects, so they live here rather than in the
-- migration set: a migration must never carry a credential. The passwords
-- are the repository's documented placeholder; a deployment replaces them
-- out of band, and the grant separation the placeholder protects is the
-- same either way.
--
-- The script is idempotent, so it can be applied to an existing cluster.
-- It is executed by the database owner (`current_user`), which is also the
-- role the migration set is applied by — the default privileges below
-- therefore cover every table the migrations create.

DO $$
DECLARE
    domain text;
    role_name text;
BEGIN
    FOREACH domain IN ARRAY ARRAY['auth', 'crm', 'inventory', 'billing'] LOOP
        role_name := 'telco_' || domain;

        IF NOT EXISTS (SELECT 1 FROM pg_roles WHERE rolname = role_name) THEN
            EXECUTE format(
                'CREATE ROLE %I LOGIN PASSWORD %L NOSUPERUSER NOCREATEDB '
                'NOCREATEROLE NOREPLICATION',
                role_name,
                'PLACEHOLDER_NO_REAL_CREDENTIAL'
            );
        END IF;

        IF NOT EXISTS (SELECT 1 FROM pg_namespace WHERE nspname = domain) THEN
            EXECUTE format('CREATE SCHEMA %I AUTHORIZATION %I', domain, role_name);
        END IF;

        -- The schema belongs to its service role and to nobody else.
        EXECUTE format('ALTER SCHEMA %I OWNER TO %I', domain, role_name);
        EXECUTE format('REVOKE ALL ON SCHEMA %I FROM PUBLIC', domain);
        EXECUTE format('GRANT USAGE ON SCHEMA %I TO %I', domain, role_name);

        -- The tables are created by the migration applier; the owning
        -- service role may read and write them, and nothing more.
        EXECUTE format(
            'ALTER DEFAULT PRIVILEGES FOR ROLE %I IN SCHEMA %I '
            'GRANT SELECT, INSERT, UPDATE, DELETE ON TABLES TO %I',
            current_user,
            domain,
            role_name
        );
        EXECUTE format(
            'ALTER DEFAULT PRIVILEGES FOR ROLE %I IN SCHEMA %I '
            'GRANT USAGE, SELECT ON SEQUENCES TO %I',
            current_user,
            domain,
            role_name
        );
    END LOOP;
END
$$;

-- Initial AgriTwin accounts.
-- Passwords are listed here only for the first login. Change them afterward.
--
-- farmer@test.com       / AgriTwin.Admin.2026!
-- user@test.com         / AgriTwin.User.2026!
-- agricultor@test.com   / AgriTwin.Campo.2026!
-- agronomo@test.com     / AgriTwin.Agro.2026!
-- investigador@test.com / AgriTwin.Ciencia.2026!
--
-- The password_hash values are Argon2id hashes generated with pwdlib,
-- matching services/password_service.py.

INSERT INTO users (
    id,
    email,
    full_name,
    password_hash,
    system_role,
    status,
    created_at,
    metadata_json
)
VALUES
(
    'USER-INITIAL-ADMIN',
    'farmer@test.com',
    'Administrador',
    '$argon2id$v=19$m=65536,t=3,p=4$ZRPRgJbuI5YFn/O0VsQZKw$tTFjaDPFbm7TL+h4BSNggEX5nwJnuC4o+zFEKMPd8Rc',
    'ADMIN',
    'ACTIVE',
    CURRENT_TIMESTAMP,
    '{}'::json
),
(
    'USER-INITIAL-GENERAL',
    'user@test.com',
    'Usuario general',
    '$argon2id$v=19$m=65536,t=3,p=4$GaanrlETQ4FehHmN5YDnFA$u0RLWNKXXadd2LIH2WveO0OX1lOnUJK6Axnc3P0LaV0',
    'USER',
    'ACTIVE',
    CURRENT_TIMESTAMP,
    '{}'::json
),
(
    'USER-INITIAL-FARMER',
    'agricultor@test.com',
    'Agricultor',
    '$argon2id$v=19$m=65536,t=3,p=4$BNSWzlgesnOH3uRDGRzyQA$d1QDyyQw4Aws8o6zEOUvHxld/bPP2V3lvwtBDw3h/wk',
    'USER',
    'ACTIVE',
    CURRENT_TIMESTAMP,
    '{}'::json
),
(
    'USER-INITIAL-AGRONOMIST',
    'agronomo@test.com',
    'Ingeniero agrónomo',
    '$argon2id$v=19$m=65536,t=3,p=4$3Qglz23m/0kBIkGafITmgg$u+FZk54Bm1LjLsLYWowG2reIU3VyhD098G9l8IVSDbQ',
    'USER',
    'ACTIVE',
    CURRENT_TIMESTAMP,
    '{}'::json
),
(
    'USER-INITIAL-RESEARCHER',
    'investigador@test.com',
    'Investigador',
    '$argon2id$v=19$m=65536,t=3,p=4$ofC5hKIL8+OOIkPvIRoSew$LXSW8mU6bEaclpwxZXb+QZkiIQtQaVCsyDZWYgl/QSA',
    'USER',
    'ACTIVE',
    CURRENT_TIMESTAMP,
    '{}'::json
)
ON CONFLICT (email) DO UPDATE
SET
    full_name = EXCLUDED.full_name,
    password_hash = EXCLUDED.password_hash,
    system_role = EXCLUDED.system_role,
    status = EXCLUDED.status,
    metadata_json = EXCLUDED.metadata_json;

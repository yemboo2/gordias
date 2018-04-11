DROP TABLE IF EXISTS SOURCE CASCADE;
CREATE TABLE SOURCE (
        contact_id BIGINT NOT NULL,
        sync_interval NUMERIC NOT NULL,
        PRIMARY KEY (contact_id)
);

DROP TABLE IF EXISTS SOURCE_values CASCADE;
CREATE TABLE SOURCE_values (
        contact_id BIGINT NOT NULL REFERENCES SOURCE(contact_id),
        field_name VARCHAR(30) NOT NULL,
        value VARCHAR(500) NOT NULL,
        PRIMARY KEY (contact_id, field_name)
)
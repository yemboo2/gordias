DROP TABLE IF EXISTS contacts CASCADE;
CREATE TABLE contacts (
        contact_id BIGINT NOT NULL,
        last_sync NUMERIC NOT NULL,
        sync_interval NUMERIC NOT NULL,
        PRIMARY KEY (contact_id)
);

DROP TABLE IF EXISTS contacts_values CASCADE;
CREATE TABLE contacts_values (
        contact_id BIGINT NOT NULL REFERENCES contacts(contact_id),
        field_name VARCHAR(30) NOT NULL,
        value VARCHAR(500) NOT NULL,
        PRIMARY KEY (contact_id, field_name)
)

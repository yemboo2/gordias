CREATE TABLE contacts (
        contact_id BIGINT NOT NULL,
        last_sync NUMERIC NOT NULL,
        sync_interval NUMERIC NOT NULL,
        PRIMARY KEY (contact_id)
);

CREATE TABLE contacts_values (
        contact_id BIGINT NOT NULL,
        field_name VARCHAR(30) NOT NULL,
        value VARCHAR(500) NOT NULL,
        PRIMARY KEY (contact_id, field_name)
);

CREATE TABLE sources_contacts (
        contact_id BIGINT NOT NULL,
	source_name VARCHAR(30) NOT NULL,
        sync_interval NUMERIC NOT NULL,
        PRIMARY KEY (contact_id, source_name)
);

CREATE TABLE sources_contacts_values (
        contact_id BIGINT NOT NULL,
	source_name VARCHAR(30) NOT NULL,
        field_name VARCHAR(30) NOT NULL,
        value VARCHAR(500) NOT NULL,
        PRIMARY KEY (contact_id, source_name, field_name)
)

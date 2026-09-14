CREATE TABLE IF NOT EXISTS source (
    source_id VARCHAR PRIMARY KEY,
    name VARCHAR NOT NULL,
    publisher VARCHAR,
    canonical_url VARCHAR NOT NULL
);

CREATE TABLE IF NOT EXISTS ingest_run (
    run_id UUID PRIMARY KEY,
    source_id VARCHAR NOT NULL,
    dataset_id VARCHAR NOT NULL,
    retrieved_at TIMESTAMP NOT NULL,
    artifact_path VARCHAR NOT NULL,
    artifact_sha256 VARCHAR NOT NULL,
    source_url VARCHAR NOT NULL
);

CREATE TABLE IF NOT EXISTS entity (
    entity_id VARCHAR PRIMARY KEY,
    canonical_name VARCHAR NOT NULL,
    entity_type VARCHAR NOT NULL,
    parent_entity_id VARCHAR,
    jurisdiction VARCHAR,
    valid_from DATE,
    valid_to DATE
);

CREATE TABLE IF NOT EXISTS entity_identifier (
    entity_id VARCHAR NOT NULL,
    id_system VARCHAR NOT NULL,
    id_value VARCHAR NOT NULL,
    valid_from DATE,
    valid_to DATE,
    PRIMARY KEY (entity_id, id_system, id_value)
);

CREATE TABLE IF NOT EXISTS observation (
    observation_id VARCHAR PRIMARY KEY,
    source_id VARCHAR NOT NULL,
    dataset_id VARCHAR NOT NULL,
    source_record_id VARCHAR,
    entity_id VARCHAR,
    concept VARCHAR NOT NULL,
    period_start DATE,
    period_end DATE,
    frequency VARCHAR,
    value DOUBLE,
    unit VARCHAR,
    status VARCHAR NOT NULL DEFAULT 'reported',
    confidence DOUBLE,
    provenance JSON
);

CREATE TABLE IF NOT EXISTS flow (
    flow_id VARCHAR PRIMARY KEY,
    source_entity_id VARCHAR NOT NULL,
    target_entity_id VARCHAR NOT NULL,
    flow_type VARCHAR NOT NULL,
    layer VARCHAR NOT NULL,
    period_start DATE,
    period_end DATE,
    value DOUBLE,
    unit VARCHAR NOT NULL,
    status VARCHAR NOT NULL,
    confidence DOUBLE,
    provenance JSON NOT NULL
);

CREATE TABLE IF NOT EXISTS reconciliation_constraint (
    constraint_id VARCHAR PRIMARY KEY,
    parent_concept VARCHAR NOT NULL,
    child_filter JSON NOT NULL,
    period_start DATE,
    period_end DATE,
    authoritative_value DOUBLE,
    unit VARCHAR,
    residual_value DOUBLE,
    provenance JSON NOT NULL
);

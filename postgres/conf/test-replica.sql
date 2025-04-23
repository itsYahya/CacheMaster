CREATE TABLE IF NOT EXISTS test_replication (
    id SERIAL PRIMARY KEY,
    message TEXT,
    created_at TIMESTAMP DEFAULT now()
);

INSERT INTO test_replication (message) VALUES ('Auto-inserted at init!');

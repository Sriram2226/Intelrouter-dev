-- Migration script for existing databases
-- Run this if you already have a queries table and need to update it

-- Remove query_text column if it exists (privacy/storage optimization)
ALTER TABLE queries DROP COLUMN IF EXISTS query_text;

-- Ensure created_at is TIMESTAMP and NOT NULL
ALTER TABLE queries ALTER COLUMN created_at TYPE TIMESTAMP USING created_at::TIMESTAMP;
ALTER TABLE queries ALTER COLUMN created_at SET NOT NULL;

-- Add indexes if they don't exist
CREATE INDEX IF NOT EXISTS idx_queries_user_id ON queries(user_id);
CREATE INDEX IF NOT EXISTS idx_queries_user_time ON queries(user_id, created_at DESC);
CREATE INDEX IF NOT EXISTS idx_queries_routing_source ON queries(routing_source);
CREATE INDEX IF NOT EXISTS idx_queries_final_label ON queries(final_label);
CREATE INDEX IF NOT EXISTS idx_queries_created_at ON queries(created_at);


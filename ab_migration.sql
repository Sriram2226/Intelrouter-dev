-- Migration: Add ab_group column to queries table
-- Run this in your Supabase SQL editor before starting the updated backend.

ALTER TABLE queries ADD COLUMN IF NOT EXISTS ab_group VARCHAR(2) DEFAULT NULL;

-- Optional: Index for efficient A/B stats queries
CREATE INDEX IF NOT EXISTS idx_queries_ab_group ON queries (ab_group);

-- Verify
SELECT column_name, data_type FROM information_schema.columns
WHERE table_name = 'queries' AND column_name = 'ab_group';

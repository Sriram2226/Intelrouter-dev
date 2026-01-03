-- ML Training Data Table Setup
-- Run this in your Supabase SQL editor

-- ML Training Data Table
CREATE TABLE IF NOT EXISTS ml_data (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    query TEXT NOT NULL,
    difficulty TEXT NOT NULL CHECK (difficulty IN ('EASY', 'MEDIUM', 'HARD')),
    created_at TIMESTAMP DEFAULT NOW()
);

-- Indexes for faster queries
CREATE INDEX IF NOT EXISTS idx_ml_data_created_at ON ml_data(created_at);
CREATE INDEX IF NOT EXISTS idx_ml_data_difficulty ON ml_data(difficulty);


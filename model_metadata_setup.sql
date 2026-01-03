-- Model Metadata Table Setup
-- Run this in your Supabase SQL editor

-- Model Metadata Table
CREATE TABLE IF NOT EXISTS model_metadata (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    version TEXT NOT NULL UNIQUE,
    accuracy DECIMAL(5, 4) NOT NULL,
    f1_score DECIMAL(5, 4) NOT NULL,
    confidence_threshold DECIMAL(3, 2) NOT NULL DEFAULT 0.6,
    training_timestamp TIMESTAMP NOT NULL,
    is_active BOOLEAN DEFAULT FALSE,
    metrics JSONB,
    created_at TIMESTAMP DEFAULT NOW()
);

-- Indexes for faster queries
CREATE INDEX IF NOT EXISTS idx_model_metadata_active ON model_metadata(is_active);
CREATE INDEX IF NOT EXISTS idx_model_metadata_version ON model_metadata(version);
CREATE INDEX IF NOT EXISTS idx_model_metadata_created_at ON model_metadata(created_at DESC);


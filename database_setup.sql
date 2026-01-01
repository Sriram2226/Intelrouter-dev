-- IntelRouter Database Setup
-- Run this in your Supabase SQL editor

-- Users table
CREATE TABLE IF NOT EXISTS users (
    id TEXT PRIMARY KEY,
    email TEXT NOT NULL,
    role TEXT DEFAULT 'user',
    created_at TIMESTAMP DEFAULT NOW()
);

-- Queries table
CREATE TABLE IF NOT EXISTS queries (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id TEXT NOT NULL REFERENCES users(id),
    algorithmic_label TEXT,
    ml_label TEXT,
    final_label TEXT NOT NULL,
    routing_source TEXT NOT NULL,
    model_name TEXT NOT NULL,
    created_at TIMESTAMP NOT NULL DEFAULT NOW()
);

-- Indexes for queries table
CREATE INDEX IF NOT EXISTS idx_queries_user_id ON queries(user_id);
CREATE INDEX IF NOT EXISTS idx_queries_user_time ON queries(user_id, created_at DESC);
CREATE INDEX IF NOT EXISTS idx_queries_routing_source ON queries(routing_source);
CREATE INDEX IF NOT EXISTS idx_queries_final_label ON queries(final_label);
CREATE INDEX IF NOT EXISTS idx_queries_created_at ON queries(created_at);

-- Usage logs table
CREATE TABLE IF NOT EXISTS usage_logs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id TEXT NOT NULL REFERENCES users(id),
    query_id UUID REFERENCES queries(id),
    model_name TEXT NOT NULL,
    difficulty TEXT NOT NULL,
    tokens_in INTEGER NOT NULL,
    tokens_out INTEGER NOT NULL,
    total_tokens INTEGER NOT NULL,
    cost DECIMAL(10, 6) NOT NULL,
    created_at TIMESTAMP DEFAULT NOW()
);

-- Indexes for usage_logs
CREATE INDEX IF NOT EXISTS idx_usage_logs_user_id ON usage_logs(user_id);
CREATE INDEX IF NOT EXISTS idx_usage_logs_created_at ON usage_logs(created_at);
CREATE INDEX IF NOT EXISTS idx_usage_logs_difficulty ON usage_logs(difficulty);


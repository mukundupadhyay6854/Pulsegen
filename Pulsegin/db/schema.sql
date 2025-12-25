-- SQLite Database Schema for Agentic App Review Trend Analysis

-- Table: topics
-- Stores stable, deduplicated topics with semantic embeddings
CREATE TABLE IF NOT EXISTS topics (
    topic_id INTEGER PRIMARY KEY AUTOINCREMENT,
    topic_name TEXT NOT NULL,
    description TEXT,
    embedding BLOB NOT NULL,  -- Stored as numpy array bytes
    created_at TEXT NOT NULL,  -- ISO format datetime
    last_seen TEXT NOT NULL    -- ISO format datetime
);

-- Table: topic_daily_counts
-- Stores daily frequency counts for each topic
CREATE TABLE IF NOT EXISTS topic_daily_counts (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    topic_id INTEGER NOT NULL,
    date TEXT NOT NULL,  -- YYYY-MM-DD format
    count INTEGER NOT NULL DEFAULT 0,
    FOREIGN KEY (topic_id) REFERENCES topics(topic_id) ON DELETE CASCADE,
    UNIQUE(topic_id, date)
);

-- Indexes for performance
CREATE INDEX IF NOT EXISTS idx_topic_daily_counts_date ON topic_daily_counts(date);
CREATE INDEX IF NOT EXISTS idx_topic_daily_counts_topic_id ON topic_daily_counts(topic_id);
CREATE INDEX IF NOT EXISTS idx_topics_last_seen ON topics(last_seen);


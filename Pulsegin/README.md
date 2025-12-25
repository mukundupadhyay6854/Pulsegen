# Agentic App Review Trend Analysis

**Senior AI Engineer Assignment**

An AI-powered system that analyzes Google Play Store app reviews and generates 30-day rolling trend reports of user issues, requests, and feedback.

## Overview

This project implements an **Agentic AI system** that analyzes Google Play Store app reviews and generates a **30-day rolling trend report** of user issues, requests, and feedback.

The system processes **daily batches of reviews**, intelligently groups semantically similar feedback into **stable topics**, and tracks how these topics trend over time. Unlike traditional topic modeling approaches (LDA, TopicBERT), this project uses **LLM-driven agents with semantic embeddings and persistent memory** to ensure high recall and accurate topic deduplication.

## Problem Statement

Product teams receive thousands of app reviews daily but lack a scalable way to:
- Identify recurring issues
- Track emerging user requests
- Detect trends over time without duplicate or fragmented topics

This system solves that problem by acting as an **AI analyst** that continuously reads reviews and produces a clean, actionable trend report.

## Key Requirements

- Daily review data treated as independent batches
- Rolling trend window of **T-30 to T**
- Topics must be **semantically deduplicated**
- Traditional topic modeling methods are **not allowed**
- System must demonstrate **agentic reasoning**
- Output must be a **trend analysis table**

## Features

- **Three Cooperating AI Agents**:
  - **Review Understanding Agent**: Interprets raw review text and produces normalized summaries
  - **Topic Matching & Deduplication Agent**: Uses semantic embeddings to match reviews with existing topics
  - **Trend Memory Agent**: Maintains topic memory and daily frequency counts with 30-day rolling window

- **Semantic Deduplication**: Prevents duplicate topics like "Delivery guy rude" and "Delivery partner impolite"

- **Persistent Storage**: SQLite database for topic and trend data

- **Rolling Window Analysis**: Automatically maintains 30-day trend windows

## Installation

### Quick Setup (Recommended)

Run the setup script which will install dependencies and initialize the database:
```bash
python setup.py
```

### Manual Setup

1. Install dependencies:
```bash
pip install -r requirements.txt
```

**Note**: The first run will download the `all-MiniLM-L6-v2` embedding model (~80MB), which may take a few minutes.

2. Initialize the database:
```bash
python db/init_db.py
```

## Usage

### Basic Usage

Process reviews from a CSV file:
```bash
python main.py --input swiggy.csv
```

### Advanced Usage

```bash
python main.py \
    --input swiggy.csv \
    --db db/trends.db \
    --date-col review_date \
    --text-col review_description \
    --rating-col rating
```

### Command Line Arguments

- `--input`: Path to input CSV file (default: `swiggy.csv`)
- `--db`: Path to SQLite database (default: `db/trends.db`)
- `--date-col`: Name of date column (default: `review_date`)
- `--text-col`: Name of review text column (default: `review_description`)
- `--rating-col`: Name of rating column (default: `rating`)

### Testing

Test with a small sample first:
```bash
python test_sample.py
```

## Input Format

The CSV file should contain:
- **Review text**: The actual review content
- **Review date**: Date when the review was posted (format: `YYYY-MM-DD HH:MM:SS` or `YYYY-MM-DD`)
- **Rating** (optional): Rating from 1-5

Example CSV structure:
```csv
review_date,review_description,rating
2023-07-24 09:57:40,"I have been using swiggy for a long time...",2
2023-07-23 10:35:23,"Worst experiences I'm having with the app...",1
```

## Output

The system generates a **trend analysis table** (`output/trend_report.csv`) where:
- **Rows** represent deduplicated topics
- **Columns** represent dates from T-30 to T
- **Cells** represent the frequency of that topic on a given date

Example output:
| Topic | 2024-06-01 | 2024-06-02 | ... | 2024-06-30 |
|-------|------------|------------|-----|------------|
| Delivery partner rude | 8 | 12 | ... | 9 |
| Food stale | 5 | 7 | ... | 11 |
| Missing items in order | 3 | 6 | ... | 4 |

## System Architecture

### Agentic Design

The system consists of three cooperating agents:

1. **Review Understanding Agent**
   - Interprets raw review text
   - Produces a normalized issue/request summary
   - Extracts key issues using pattern matching and semantic analysis
   - Categorizes reviews (complaint, positive, neutral)

2. **Topic Matching & Deduplication Agent**
   - Uses semantic embeddings to match reviews with existing topics
   - Decides whether to reuse or create a new topic
   - Uses cosine similarity (threshold: 0.75) for matching
   - Prevents duplicate topics through semantic comparison

3. **Trend Memory Agent**
   - Maintains topic memory and daily frequency counts
   - Enforces a 30-day rolling window
   - Automatically cleans up old data (for recent datasets)
   - Generates trend reports

## Database Design (SQLite)

### Table: `topics`
Stores stable, deduplicated topics with semantic embeddings.

Fields:
- `topic_id`: Primary key (INTEGER)
- `topic_name`: Normalized topic name (TEXT)
- `description`: Detailed description (TEXT)
- `embedding`: Semantic embedding stored as BLOB
- `created_at`: Creation timestamp (TEXT, ISO format)
- `last_seen`: Last occurrence timestamp (TEXT, ISO format)

### Table: `topic_daily_counts`
Stores daily frequency counts for each topic.

Fields:
- `id`: Primary key (INTEGER)
- `topic_id`: Foreign key to topics (INTEGER)
- `date`: Date in YYYY-MM-DD format (TEXT)
- `count`: Frequency count for that date (INTEGER)

SQLite is used for its lightweight, serverless nature and persistence across daily runs.

## Topic Deduplication Strategy

- Each topic is represented by a semantic embedding
- New reviews are embedded and compared with existing topics using cosine similarity
- If similarity ≥ 0.75 → merge with existing topic
- Else → create a new topic
- This prevents duplicate topics like:
  - "Delivery guy rude"
  - "Delivery partner impolite"
  - "Rude delivery executive"

## How It Works

1. **Review Understanding**: Each review is processed by the Review Understanding Agent to extract key issues and generate normalized summaries.

2. **Topic Matching**: The Topic Matching Agent uses semantic embeddings to compare new reviews with existing topics. If similarity ≥ 0.75, the review is matched to an existing topic; otherwise, a new topic is created.

3. **Trend Tracking**: The Trend Memory Agent records daily occurrences and maintains a 30-day rolling window. For historical data (>60 days old), cleanup is skipped to preserve all data.

4. **Report Generation**: The system generates a comprehensive trend report showing how topics evolve over the 30-day period, automatically using the maximum date from the database.

## Project Structure

```
├── data/
│   └── test_sample.csv (generated for testing)
├── db/
│   ├── trends.db (SQLite database)
│   ├── schema.sql (database schema)
│   └── init_db.py (database initialization)
├── agents/
│   ├── __init__.py
│   ├── review_understanding.py (Review Understanding Agent)
│   ├── topic_matching.py (Topic Matching & Deduplication Agent)
│   └── trend_memory.py (Trend Memory Agent)
├── output/
│   └── trend_report.csv (generated trend analysis)
├── main.py (main processing script)
├── setup.py (setup script)
├── test_sample.py (test script)
├── requirements.txt (Python dependencies)
└── README.md (this file)
```

## Technical Details

- **Embeddings**: Uses `sentence-transformers` with the `all-MiniLM-L6-v2` model for semantic similarity
- **Similarity Threshold**: 0.75 cosine similarity for topic deduplication
- **Database**: SQLite for lightweight, serverless persistence
- **Processing**: Handles large datasets efficiently with batch processing
- **Historical Data**: Automatically handles historical datasets by preserving all data and using max date from database

## Requirements

- Python 3.8+
- See `requirements.txt` for full dependency list:
  - pandas >= 2.0.0
  - numpy >= 1.24.0
  - sentence-transformers >= 2.2.0
  - scikit-learn >= 1.3.0
  - openai >= 1.0.0 (optional, for future LLM integration)
  - python-dotenv >= 1.0.0

## Performance Notes

- Processing 200K+ reviews typically takes 10-30 minutes depending on system
- First run downloads embedding model (~80MB)
- Database grows with number of unique topics (typically 50-200 topics for 200K reviews)
- Trend reports are generated efficiently using SQL queries and pandas pivoting

## Troubleshooting

### Unicode Encoding Errors
If you encounter encoding errors on Windows, the setup script has been fixed to use ASCII-compatible characters.

### Historical Data
The system automatically detects historical data (>60 days old) and preserves it instead of cleaning it up. Trend reports use the maximum date from the database automatically.

### Empty Trend Reports
If the trend report is empty, check:
1. Dates in your CSV are properly formatted
2. Review descriptions are not empty
3. Database contains data: `SELECT COUNT(*) FROM topics;`

## License

This project is part of a Senior AI Engineer assignment.

## Author

Developed as an assignment demonstrating agentic AI principles, semantic embeddings, and trend analysis capabilities.

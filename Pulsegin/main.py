import pandas as pd
import sys
import os
from datetime import datetime, timedelta
from pathlib import Path

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from agents import ReviewUnderstandingAgent, TopicMatchingAgent, TrendMemoryAgent
from db.init_db import init_database

def process_reviews(csv_path: str, db_path: str = 'db/trends.db', 
                   date_column: str = 'review_date',
                   text_column: str = 'review_description',
                   rating_column: str = 'rating'):
    print("="*60)
    print("Agentic App Review Trend Analysis")
    print("="*60)
    
    if not os.path.exists(db_path):
        print("\nInitializing database...")
        init_database(db_path)
    
    print("\nInitializing agents...")
    review_agent = ReviewUnderstandingAgent()
    topic_agent = TopicMatchingAgent(db_path=db_path)
    memory_agent = TrendMemoryAgent(db_path=db_path)
    
    print(f"\nLoading reviews from {csv_path}...")
    try:
        df = pd.read_csv(csv_path, encoding='utf-8', low_memory=False)
        print(f"Loaded {len(df):,} reviews")
    except Exception as e:
        print(f"Error loading CSV: {e}")
        return
    
    required_columns = [date_column, text_column]
    missing_columns = [col for col in required_columns if col not in df.columns]
    if missing_columns:
        print(f"Error: Missing required columns: {missing_columns}")
        return
    
    print("\nProcessing dates...")
    df[date_column] = pd.to_datetime(df[date_column], errors='coerce')
    df = df.dropna(subset=[date_column])
    df['date'] = df[date_column].dt.strftime('%Y-%m-%d')
    
    print(f"Processing {len(df):,} reviews...")
    
    processed = 0
    new_topics = 0
    matched_topics = 0
    
    for idx, row in df.iterrows():
        review_text = str(row.get(text_column, ''))
        review_date = row.get('date', '')
        rating = row.get(rating_column, None)
        
        if not review_text or not review_date:
            continue
        
        understanding = review_agent.understand_review(review_text, rating)
        summary = understanding['summary']
        
        topic_id, is_new = topic_agent.find_or_create_topic(
            review_summary=summary,
            description=review_text[:500]
        )
        
        if is_new:
            new_topics += 1
        else:
            matched_topics += 1
        
        memory_agent.record_topic_occurrence(topic_id, review_date)
        
        processed += 1
        if processed % 1000 == 0:
            print(f"  Processed {processed:,} reviews... (New topics: {new_topics}, Matched: {matched_topics})")
    
    print(f"\nProcessing complete!")
    print(f"  Total reviews processed: {processed:,}")
    print(f"  New topics created: {new_topics:,}")
    print(f"  Topics matched: {matched_topics:,}")
    
    max_date = df['date'].max() if len(df) > 0 else None
    
    print("\nCleaning up old data...")
    if max_date:
        max_date_obj = datetime.strptime(max_date, '%Y-%m-%d')
        days_ago = (datetime.now() - max_date_obj).days
        if days_ago <= 60:
            cleanup_date = max_date if max_date >= datetime.now().strftime('%Y-%m-%d') else datetime.now().strftime('%Y-%m-%d')
            memory_agent.cleanup_old_data(cleanup_date)
            print(f"  Cleaned up data older than 30 days from {cleanup_date}")
        else:
            print(f"  Skipping cleanup (historical data from {max_date}, {days_ago} days ago)")
    else:
        print("  No data to cleanup")
    
    print("\nGenerating trend report...")
    trend_df = memory_agent.get_trend_report()
    
    output_path = 'output/trend_report.csv'
    os.makedirs('output', exist_ok=True)
    trend_df.to_csv(output_path, index=False)
    
    print(f"\nTrend report saved to {output_path}")
    print(f"  Topics tracked: {len(trend_df)}")
    print(f"  Date range: {trend_df.columns[1] if len(trend_df.columns) > 1 else 'N/A'} to {trend_df.columns[-1] if len(trend_df.columns) > 1 else 'N/A'}")
    
    print("\n" + "="*60)
    print("Top 10 Topics by Total Frequency:")
    print("="*60)
    if len(trend_df) > 0:
        date_cols = [col for col in trend_df.columns if col != 'Topic']
        if date_cols:
            trend_df['Total'] = trend_df[date_cols].sum(axis=1)
            top_topics = trend_df.nlargest(10, 'Total')[['Topic', 'Total']]
            print(top_topics.to_string(index=False))
            trend_df = trend_df.drop('Total', axis=1)
    else:
        print("No topics found in the trend report.")
    
    print("\n" + "="*60)
    print("Processing complete!")
    print("="*60)

def main():
    import argparse
    
    parser = argparse.ArgumentParser(
        description='Agentic App Review Trend Analysis System'
    )
    parser.add_argument(
        '--input',
        type=str,
        default='swiggy.csv',
        help='Path to input CSV file (default: swiggy.csv)'
    )
    parser.add_argument(
        '--db',
        type=str,
        default='db/trends.db',
        help='Path to SQLite database (default: db/trends.db)'
    )
    parser.add_argument(
        '--date-col',
        type=str,
        default='review_date',
        help='Name of date column (default: review_date)'
    )
    parser.add_argument(
        '--text-col',
        type=str,
        default='review_description',
        help='Name of review text column (default: review_description)'
    )
    parser.add_argument(
        '--rating-col',
        type=str,
        default='rating',
        help='Name of rating column (default: rating)'
    )
    
    args = parser.parse_args()
    
    if not os.path.exists(args.input):
        print(f"Error: Input file '{args.input}' not found.")
        print(f"Please provide a valid CSV file path.")
        return
    
    process_reviews(
        csv_path=args.input,
        db_path=args.db,
        date_column=args.date_col,
        text_column=args.text_col,
        rating_column=args.rating_col
    )

if __name__ == "__main__":
    main()

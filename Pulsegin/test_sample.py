import pandas as pd
import os
import sys

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from main import process_reviews

def create_test_sample(input_file='swiggy.csv', output_file='data/test_sample.csv', n_rows=100):
    print(f"Creating test sample with {n_rows} rows from {input_file}...")
    
    df = pd.read_csv(input_file, nrows=n_rows)
    os.makedirs('data', exist_ok=True)
    df.to_csv(output_file, index=False)
    print(f"Test sample saved to {output_file}")
    return output_file

if __name__ == "__main__":
    test_file = create_test_sample(n_rows=100)
    
    print("\n" + "="*60)
    print("Processing test sample...")
    print("="*60 + "\n")
    
    process_reviews(
        csv_path=test_file,
        db_path='db/trends_test.db',
        date_column='review_date',
        text_column='review_description',
        rating_column='rating'
    )
    
    print("\n" + "="*60)
    print("Test complete! Check output/trend_report.csv for results.")
    print("="*60)

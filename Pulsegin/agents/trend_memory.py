import sqlite3
from datetime import datetime, timedelta
from typing import Dict, List
import pandas as pd

class TrendMemoryAgent:
    
    def __init__(self, db_path: str = 'db/trends.db', window_days: int = 30):
        self.db_path = db_path
        self.window_days = window_days
    
    def record_topic_occurrence(self, topic_id: int, date: str):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT count FROM topic_daily_counts
            WHERE topic_id = ? AND date = ?
        """, (topic_id, date))
        
        result = cursor.fetchone()
        
        if result:
            new_count = result[0] + 1
            cursor.execute("""
                UPDATE topic_daily_counts
                SET count = ?
                WHERE topic_id = ? AND date = ?
            """, (new_count, topic_id, date))
        else:
            cursor.execute("""
                INSERT INTO topic_daily_counts (topic_id, date, count)
                VALUES (?, ?, 1)
            """, (topic_id, date))
        
        conn.commit()
        conn.close()
    
    def cleanup_old_data(self, current_date: str = None):
        if current_date is None:
            current_date = datetime.now().strftime('%Y-%m-%d')
        
        cutoff_date = (datetime.strptime(current_date, '%Y-%m-%d') - 
                      timedelta(days=self.window_days)).strftime('%Y-%m-%d')
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            DELETE FROM topic_daily_counts
            WHERE date < ?
        """, (cutoff_date,))
        
        conn.commit()
        conn.close()
    
    def get_trend_report(self, end_date: str = None) -> pd.DataFrame:
        conn = sqlite3.connect(self.db_path)
        
        if end_date is None:
            cursor = conn.cursor()
            cursor.execute("SELECT MAX(date) FROM topic_daily_counts")
            result = cursor.fetchone()
            if result and result[0]:
                end_date = result[0]
            else:
                end_date = datetime.now().strftime('%Y-%m-%d')
        
        start_date = (datetime.strptime(end_date, '%Y-%m-%d') - 
                     timedelta(days=self.window_days - 1)).strftime('%Y-%m-%d')
        
        query = """
            SELECT t.topic_id, t.topic_name, tdc.date, tdc.count
            FROM topics t
            JOIN topic_daily_counts tdc ON t.topic_id = tdc.topic_id
            WHERE tdc.date >= ? AND tdc.date <= ?
            ORDER BY t.topic_name, tdc.date
        """
        
        df = pd.read_sql_query(query, conn, params=(start_date, end_date))
        conn.close()
        
        if df.empty:
            return pd.DataFrame(columns=['Topic'])
        
        trend_df = df.pivot_table(
            index='topic_name',
            columns='date',
            values='count',
            fill_value=0,
            aggfunc='sum'
        )
        
        trend_df = trend_df.reset_index()
        trend_df.columns.name = None
        
        trend_df.rename(columns={'topic_name': 'Topic'}, inplace=True)
        
        date_columns = [col for col in trend_df.columns if col != 'Topic']
        date_columns.sort()
        trend_df = trend_df[['Topic'] + date_columns]
        
        trend_df['_total'] = trend_df[date_columns].sum(axis=1)
        trend_df = trend_df.sort_values('_total', ascending=False)
        trend_df = trend_df.drop('_total', axis=1)
        
        return trend_df
    
    def get_all_topics(self) -> List[Dict]:
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT topic_id, topic_name, description, created_at, last_seen
            FROM topics
            ORDER BY last_seen DESC
        """)
        
        topics = []
        for row in cursor.fetchall():
            topics.append({
                'topic_id': row[0],
                'topic_name': row[1],
                'description': row[2],
                'created_at': row[3],
                'last_seen': row[4]
            })
        
        conn.close()
        return topics

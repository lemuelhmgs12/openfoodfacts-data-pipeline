
from pathlib import Path

QUERIES_DIR = Path(__file__).parent / "queries"

def run_query(conn, sql_filename, s3_path):
    sql_file_path = QUERIES_DIR / sql_filename
    with open(sql_file_path) as f:
        query_text = f.read()
        query_text = query_text.format(s3_path=s3_path)
    
    return conn.execute(query_text).df()


    
import duckdb

def get_connection():
    conn = duckdb.connect()

    conn.execute("INSTALL httpfs;")
    conn.execute("LOAD httpfs;")

    conn.execute("""
        CREATE SECRET (
                 TYPE s3,
                 PROVIDER credential_chain
                 );
     """)
    
    return conn
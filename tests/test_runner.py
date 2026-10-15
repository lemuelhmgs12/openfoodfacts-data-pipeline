import duckdb
from pipeline.sql.runner  import run_query

def test_run_query_from_temporary_sql_file(mocker, tmp_path):
	
	mocker.patch("pipeline.sql.runner.QUERIES_DIR", tmp_path)
	src = tmp_path / "in.csv"
	src.write_text("id,name\n1,apple\n2,banana\n")
	dst = tmp_path / "out.parquet"
	
	(tmp_path / "test_query.sql").write_text(
		"COPY (SELECT * FROM '{source}') TO '{target}' (FORMAT parquet)"
    )

	conn = duckdb.connect()
	try:
		run_query(conn, "test_query.sql", source=str(src), target=str(dst))
		assert dst.exists()
		rows = conn.execute(f"select id, name from '{dst}'").fetchall()
		assert rows == [(1, "apple"),(2, "banana")]
	finally:
		conn.close()

   
        


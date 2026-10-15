from pipeline.sql.connection import get_connection

def test_get_connection_sets_up_httpfs_and_s3_secret(mocker):
    fake_conn = mocker.MagicMock()
    mocker.patch("duckdb.connect", return_value=fake_conn)   

    conn = get_connection()

    assert conn is fake_conn
    statements = [c.args[0] for c in fake_conn.execute.call_args_list]
    assert statements[0] == "INSTALL httpfs;"
    assert statements[1] == "LOAD httpfs;"
    assert "credential_chain" in statements[2]
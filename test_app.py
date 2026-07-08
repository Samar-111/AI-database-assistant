import pytest
import sqlite3
import app

@pytest.fixture
def setup_test_db(tmp_path):
    # Set up a temporary mock database file
    db_file = tmp_path / "test.db"
    conn = sqlite3.connect(db_file)
    cursor = conn.cursor()
    cursor.execute("CREATE TABLE inventory (id INT, item TEXT, quantity INT);")
    cursor.execute("INSERT INTO inventory VALUES (1, 'Laptops', 12), (2, 'Monitors', 34);")
    conn.commit()
    conn.close()
    return str(db_file)

def test_successful_query(setup_test_db, monkeypatch):
   
    monkeypatch.setattr("app.db_path", setup_test_db)
    
    result = app.run_query("SELECT item FROM inventory WHERE id = 1;")
    assert result["error"] is None
    assert result["data"] == [("Laptops",)]
    assert result["columns"] == ["item"]

def test_broken_sql_syntax(setup_test_db, monkeypatch):
    monkeypatch.setattr("app.db_path", setup_test_db)
    
    result = app.run_query("SELECT broken_syntax FROM FROM inventory;")
    assert result["error"] is not None
import os
import pandas as pd
from psycopg2 import connect
from urllib.parse import urlparse
from dotenv import load_dotenv

# Load .env if present
load_dotenv()

def _parse_database_url(url: str):
    """Parse a DATABASE_URL (postgres) into psycopg2 kwargs."""
    parsed = urlparse(url)
    return {
        "dbname": parsed.path.lstrip('/'),
        "user": parsed.username,
        "password": parsed.password,
        "host": parsed.hostname or 'localhost',
        "port": str(parsed.port or 5432),
    }

DATABASE_URL = os.getenv("DATABASE_URL")
if DATABASE_URL:
    DB_CONFIG = _parse_database_url(DATABASE_URL)
else:
    DB_CONFIG = {
        "dbname": os.getenv("DB_NAME", "PhonePayDB"),
        "user": os.getenv("DB_USER", "postgres"),
        "password": os.getenv("DB_PASSWORD", "admin"),
        "host": os.getenv("DB_HOST", "localhost"),
        "port": os.getenv("DB_PORT", "5432"),
    }

def run_query(sql_text, params=None):
    with connect(**DB_CONFIG) as conn:
        return pd.read_sql(sql_text, conn, params=params)

def read_sql_file(path: str) -> str:
    """Read a .sql file and return its text.
    Accepts relative paths (to project root) or absolute paths.
    """
    # Normalize to abs path
    abs_path = path
    if not os.path.isabs(path):
        # project root is parent of this file's parent (analysis/..)
        analysis_dir = os.path.dirname(os.path.abspath(__file__))
        project_root = os.path.dirname(analysis_dir)
        abs_path = os.path.join(project_root, path)
    with open(abs_path, 'r', encoding='utf-8') as f:
        return f.read()

def extract_last_select(sql_text: str) -> str:
    """Given a SQL script possibly containing CREATE VIEW and multiple SELECTs,
    return the last SELECT statement for data retrieval.
    Simple heuristic: split by ';' and pick the last chunk containing 'select'.
    """
    parts = [p.strip() for p in sql_text.split(';') if p.strip()]
    # traverse from end to find a select
    for chunk in reversed(parts):
        if 'select' in chunk.lower():
            return chunk
    # fallback to full text
    return sql_text

def run_query_file(path: str, params=None) -> pd.DataFrame:
    """Load SQL from file under sql/queries and execute last SELECT via pandas.read_sql."""
    text = read_sql_file(path)
    select_sql = extract_last_select(text)
    with connect(**DB_CONFIG) as conn:
        return pd.read_sql(select_sql, conn, params=params)

def run_query_file_select(path: str, contains: str, params=None) -> pd.DataFrame:
    """Load SQL from file and execute the SELECT statement that contains the given substring.
    This allows files with multiple SELECTs to be reused for specific datasets.
    """
    text = read_sql_file(path)
    parts = [p.strip() for p in text.split(';') if p.strip()]
    target_sql = None
    for chunk in parts:
        if 'select' in chunk.lower() and contains.lower() in chunk.lower():
            target_sql = chunk
    if target_sql is None:
        # Fallback to last SELECT if no match
        target_sql = extract_last_select(text)
    with connect(**DB_CONFIG) as conn:
        return pd.read_sql(target_sql, conn, params=params)

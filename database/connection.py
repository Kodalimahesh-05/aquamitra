"""
AquaMitra Database Connection Manager
Provides centralized pyodbc connection to Microsoft SQL Server.
Safely falls back to Demo Mode if SQL Server is not reachable or unconfigured.
"""

import os
from typing import Optional, Any, List, Tuple
import pandas as pd
import streamlit as st


def get_db_credentials() -> dict:
    """
    Retrieves database credentials from Streamlit secrets or OS environment variables.
    Never exposes passwords or sensitive strings in logs.
    """
    creds = {
        "server": os.getenv("DB_SERVER", "localhost"),
        "database": os.getenv("DB_NAME", "AquaMitraDB"),
        "username": os.getenv("DB_USERNAME", "sa"),
        "password": os.getenv("DB_PASSWORD", ""),
        "driver": os.getenv("DB_DRIVER", "ODBC Driver 18 for SQL Server"),
        "trust_cert": os.getenv("DB_TRUST_CERT", "yes")
    }

    # Check streamlit secrets if available
    try:
        if hasattr(st, "secrets") and "database" in st.secrets:
            sec = st.secrets["database"]
            creds["server"] = sec.get("server", creds["server"])
            creds["database"] = sec.get("database", creds["database"])
            creds["username"] = sec.get("username", creds["username"])
            creds["password"] = sec.get("password", creds["password"])
            creds["driver"] = sec.get("driver", creds["driver"])
            creds["trust_cert"] = sec.get("trust_server_certificate", creds["trust_cert"])
    except Exception:
        pass

    return creds


def get_connection():
    """
    Attempts to establish a live connection to MS SQL Server using pyodbc.
    Returns the connection object if successful, or None if connection fails.
    """
    creds = get_db_credentials()
    if not creds["password"]:
        return None

    try:
        import pyodbc
        conn_str = (
            f"DRIVER={{{creds['driver']}}};"
            f"SERVER={creds['server']};"
            f"DATABASE={creds['database']};"
            f"UID={creds['username']};"
            f"PWD={creds['password']};"
            f"TrustServerCertificate={creds['trust_cert']};"
            "Connection Timeout=3;"
        )
        conn = pyodbc.connect(conn_str)
        return conn
    except Exception:
        # Graceful fallback: return None without raising raw tracebacks
        return None


def is_database_connected() -> bool:
    """
    Tests if SQL Server is currently connected and accessible.
    """
    conn = get_connection()
    if conn:
        try:
            cursor = conn.cursor()
            cursor.execute("SELECT 1")
            cursor.close()
            conn.close()
            return True
        except Exception:
            return False
    return False


def execute_parameterized_query(query: str, params: Tuple = ()) -> Optional[pd.DataFrame]:
    """
    Safely executes a SELECT query using parameterized arguments to prevent SQL injection.
    Returns a pandas DataFrame of results, or None if database is unavailable.
    """
    conn = get_connection()
    if not conn:
        return None
    try:
        df = pd.read_sql(query, conn, params=params)
        conn.close()
        return df
    except Exception as e:
        if conn:
            conn.close()
        return None


def execute_parameterized_nonquery(query: str, params: Tuple = ()) -> bool:
    """
    Safely executes an INSERT, UPDATE, or DELETE query with parameterized inputs.
    Returns True on success, False on failure.
    """
    conn = get_connection()
    if not conn:
        return False
    try:
        cursor = conn.cursor()
        cursor.execute(query, params)
        conn.commit()
        cursor.close()
        conn.close()
        return True
    except Exception:
        if conn:
            conn.rollback()
            conn.close()
        return False

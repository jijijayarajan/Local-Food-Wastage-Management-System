"""
db_utils.py
------------
Database connection and reusable query helpers for the
Local Food Wastage Management System Streamlit app.
"""

import pandas as pd
from sqlalchemy import create_engine, text
import streamlit as st

@st.cache_resource
def get_engine():
    return create_engine(
        "mysql+pymysql://root:kQkhvfBpjThKfeNKihmNaYsQxyikYSrd@reseau.proxy.rlwy.net:27924/railway",
        pool_pre_ping=True,
        pool_recycle=3600
    )
def run_query(sql: str, params: dict | None = None) -> pd.DataFrame:
    """Run a SELECT query and return a DataFrame."""
    engine = get_engine()
    with engine.connect() as conn:
        return pd.read_sql(text(sql), conn, params=params)


def run_statement(sql: str, params: dict | None = None) -> None:
    """Run an INSERT / UPDATE / DELETE statement (no return value)."""
    engine = get_engine()
    with engine.begin() as conn:  # begin() auto-commits on success
        conn.execute(text(sql), params or {})


def get_filter_options() -> dict:
    """Fetch distinct values used to populate the sidebar filter dropdowns."""
    cities = run_query("SELECT DISTINCT Location FROM food_listings ORDER BY Location")["Location"].tolist()
    providers = run_query("SELECT DISTINCT Name FROM providers ORDER BY Name")["Name"].tolist()
    food_types = run_query("SELECT DISTINCT Food_Type FROM food_listings ORDER BY Food_Type")["Food_Type"].tolist()
    meal_types = run_query("SELECT DISTINCT Meal_Type FROM food_listings ORDER BY Meal_Type")["Meal_Type"].tolist()
    return {
        "cities": cities,
        "providers": providers,
        "food_types": food_types,
        "meal_types": meal_types,
    }

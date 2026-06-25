"""
queries.py
-----------
All analysis queries used by the Streamlit app, wrapped as functions
that return a pandas DataFrame. Mirrors sql/queries.sql.
"""

from db_utils import run_query


def providers_per_city():
    return run_query("""
        SELECT City, COUNT(DISTINCT Provider_ID) AS Provider_Count
        FROM providers GROUP BY City ORDER BY Provider_Count DESC
    """)


def receivers_per_city():
    return run_query("""
        SELECT City, COUNT(DISTINCT Receiver_ID) AS Receiver_Count
        FROM receivers GROUP BY City ORDER BY Receiver_Count DESC
    """)


def top_provider_types_by_quantity():
    return run_query("""
        SELECT p.Type AS Provider_Type, SUM(f.Quantity) AS Total_Quantity_Contributed
        FROM food_listings f JOIN providers p ON f.Provider_ID = p.Provider_ID
        GROUP BY p.Type ORDER BY Total_Quantity_Contributed DESC
    """)


def provider_contacts_by_city(city: str):
    return run_query(
        "SELECT Name, Type, Address, Contact FROM providers WHERE City = :city",
        {"city": city},
    )


def top_receivers_by_quantity_claimed(limit: int = 10):
    return run_query(f"""
        SELECT r.Receiver_ID, r.Name, r.Type, SUM(f.Quantity) AS Total_Quantity_Claimed
        FROM claims c
        JOIN receivers r ON c.Receiver_ID = r.Receiver_ID
        JOIN food_listings f ON c.Food_ID = f.Food_ID
        WHERE c.Status = 'Completed'
        GROUP BY r.Receiver_ID, r.Name, r.Type
        ORDER BY Total_Quantity_Claimed DESC LIMIT {limit}
    """)


def total_quantity_available():
    return run_query("SELECT SUM(Quantity) AS Total_Quantity_Available FROM food_listings")


def listings_per_city(limit: int = 10):
    return run_query(f"""
        SELECT Location AS City, COUNT(*) AS Listing_Count
        FROM food_listings GROUP BY Location ORDER BY Listing_Count DESC LIMIT {limit}
    """)


def food_type_breakdown():
    return run_query("""
        SELECT Food_Type, COUNT(*) AS Listing_Count, SUM(Quantity) AS Total_Quantity
        FROM food_listings GROUP BY Food_Type ORDER BY Listing_Count DESC
    """)


def claims_per_food_item(limit: int = 15):
    return run_query(f"""
        SELECT f.Food_ID, f.Food_Name, COUNT(c.Claim_ID) AS Claim_Count
        FROM food_listings f LEFT JOIN claims c ON f.Food_ID = c.Food_ID
        GROUP BY f.Food_ID, f.Food_Name ORDER BY Claim_Count DESC LIMIT {limit}
    """)


def top_providers_by_successful_claims(limit: int = 10):
    return run_query(f"""
        SELECT p.Provider_ID, p.Name, p.Type, COUNT(c.Claim_ID) AS Successful_Claims
        FROM claims c
        JOIN food_listings f ON c.Food_ID = f.Food_ID
        JOIN providers p ON f.Provider_ID = p.Provider_ID
        WHERE c.Status = 'Completed'
        GROUP BY p.Provider_ID, p.Name, p.Type
        ORDER BY Successful_Claims DESC LIMIT {limit}
    """)


def claim_status_breakdown():
    return run_query("""
        SELECT Status, COUNT(*) AS Count_Of_Claims,
               ROUND(COUNT(*) * 100.0 / (SELECT COUNT(*) FROM claims), 2) AS Percentage
        FROM claims GROUP BY Status ORDER BY Count_Of_Claims DESC
    """)


def avg_quantity_claimed_per_receiver():
    return run_query("""
        SELECT ROUND(AVG(receiver_totals.Total_Quantity), 2) AS Avg_Quantity_Claimed_Per_Receiver
        FROM (
            SELECT c.Receiver_ID, SUM(f.Quantity) AS Total_Quantity
            FROM claims c JOIN food_listings f ON c.Food_ID = f.Food_ID
            WHERE c.Status = 'Completed'
            GROUP BY c.Receiver_ID
        ) AS receiver_totals
    """)


def most_claimed_meal_type():
    return run_query("""
        SELECT f.Meal_Type, COUNT(c.Claim_ID) AS Claim_Count
        FROM claims c JOIN food_listings f ON c.Food_ID = f.Food_ID
        GROUP BY f.Meal_Type ORDER BY Claim_Count DESC
    """)


def total_donated_by_provider(limit: int = 15):
    return run_query(f"""
        SELECT p.Provider_ID, p.Name, p.Type, SUM(f.Quantity) AS Total_Quantity_Donated
        FROM food_listings f JOIN providers p ON f.Provider_ID = p.Provider_ID
        GROUP BY p.Provider_ID, p.Name, p.Type
        ORDER BY Total_Quantity_Donated DESC LIMIT {limit}
    """)


def unclaimed_items_nearing_expiry(limit: int = 15):
    return run_query(f"""
        SELECT f.Food_ID, f.Food_Name, f.Quantity, f.Expiry_Date, f.Location
        FROM food_listings f
        LEFT JOIN claims c ON f.Food_ID = c.Food_ID AND c.Status = 'Completed'
        WHERE c.Claim_ID IS NULL
        ORDER BY f.Expiry_Date ASC LIMIT {limit}
    """)


def claim_status_by_city():
    return run_query("""
        SELECT f.Location AS City, c.Status, COUNT(*) AS Claim_Count
        FROM claims c JOIN food_listings f ON c.Food_ID = f.Food_ID
        GROUP BY f.Location, c.Status ORDER BY City, Claim_Count DESC
    """)


def claims_by_receiver_type():
    return run_query("""
        SELECT r.Type AS Receiver_Type, COUNT(c.Claim_ID) AS Total_Claims
        FROM claims c JOIN receivers r ON c.Receiver_ID = r.Receiver_ID
        GROUP BY r.Type ORDER BY Total_Claims DESC
    """)


# Registry used by the Streamlit page to list all queries with labels
QUERY_REGISTRY = [
    ("1. Providers per city", providers_per_city, None),
    ("2. Receivers per city", receivers_per_city, None),
    ("3. Provider type contributing most food (by quantity)", top_provider_types_by_quantity, None),
    ("4. Top receivers by quantity claimed", top_receivers_by_quantity_claimed, None),
    ("5. Total quantity of food available", total_quantity_available, None),
    ("6. City with most food listings", listings_per_city, None),
    ("7. Most common food types", food_type_breakdown, None),
    ("8. Claims per food item", claims_per_food_item, None),
    ("9. Providers with most successful claims", top_providers_by_successful_claims, None),
    ("10. Claim status breakdown (% Completed/Pending/Cancelled)", claim_status_breakdown, None),
    ("11. Average quantity claimed per receiver", avg_quantity_claimed_per_receiver, None),
    ("12. Most claimed meal type", most_claimed_meal_type, None),
    ("13. Total quantity donated per provider", total_donated_by_provider, None),
    ("14. Unclaimed items nearing expiry", unclaimed_items_nearing_expiry, None),
    ("15. Claim status breakdown by city", claim_status_by_city, None),
    ("16. Claims by receiver type", claims_by_receiver_type, None),
]

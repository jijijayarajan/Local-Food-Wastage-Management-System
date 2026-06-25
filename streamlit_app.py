"""
streamlit_app.py
-----------------
Local Food Wastage Management System — main Streamlit app.

Run with:
    streamlit run streamlit_app.py
"""

import streamlit as st
import plotly.express as px
from db_utils import run_query, run_statement, get_filter_options
from queries import QUERY_REGISTRY, provider_contacts_by_city

st.set_page_config(
    page_title="Local Food Wastage Management System",
    page_icon="🍽️",
    layout="wide",
)

# ----------------------------------------------------------------------
# Minimal, calm styling — data tool, not a marketing page.
# A single accent color (green, for "food rescue") used sparingly.
# ----------------------------------------------------------------------
st.markdown("""
<style>
    .stMetric { background-color: #F2F7F3; border-radius: 8px; padding: 12px; }
    h1, h2, h3 { color: #1B4332; }
</style>
""", unsafe_allow_html=True)

st.title("🍽️ Local Food Wastage Management System")
st.caption("Connecting surplus food providers with people and organizations in need.")

page = st.sidebar.radio(
    "Navigate",
    ["Overview", "Browse & Filter Listings", "Analysis (15 Queries)", "Manage Records (CRUD)"],
)

# ======================================================================
# PAGE 1: OVERVIEW
# ======================================================================
if page == "Overview":
    st.subheader("System Snapshot")

    col1, col2, col3, col4 = st.columns(4)
    n_providers = run_query("SELECT COUNT(*) AS n FROM providers")["n"][0]
    n_receivers = run_query("SELECT COUNT(*) AS n FROM receivers")["n"][0]
    n_listings = run_query("SELECT COUNT(*) AS n FROM food_listings")["n"][0]
    n_quantity = run_query("SELECT SUM(Quantity) AS n FROM food_listings")["n"][0]

    col1.metric("Food Providers", f"{n_providers:,}")
    col2.metric("Receivers", f"{n_receivers:,}")
    col3.metric("Active Listings", f"{n_listings:,}")
    col4.metric("Total Quantity Available", f"{n_quantity:,}")

    st.divider()

    c1, c2 = st.columns(2)
    with c1:
        st.markdown("**Claim status breakdown**")
        status_df = run_query("""
            SELECT Status, COUNT(*) AS Count_Of_Claims FROM claims GROUP BY Status
        """)
        fig = px.pie(status_df, names="Status", values="Count_Of_Claims", hole=0.45,
                     color_discrete_sequence=["#2D6A4F", "#95D5B2", "#D8F3DC"])
        st.plotly_chart(fig, use_container_width=True)

    with c2:
        st.markdown("**Food type distribution**")
        ft_df = run_query("""
            SELECT Food_Type, COUNT(*) AS Listing_Count FROM food_listings GROUP BY Food_Type
        """)
        fig2 = px.bar(ft_df, x="Food_Type", y="Listing_Count", color="Food_Type",
                      color_discrete_sequence=px.colors.sequential.Greens_r)
        st.plotly_chart(fig2, use_container_width=True)

# ======================================================================
# PAGE 2: BROWSE & FILTER LISTINGS (+ provider contact lookup)
# ======================================================================
elif page == "Browse & Filter Listings":
    st.subheader("Browse Food Listings")

    options = get_filter_options()

    f1, f2, f3, f4 = st.columns(4)
    sel_city = f1.selectbox("City", ["All"] + options["cities"])
    sel_provider = f2.selectbox("Provider", ["All"] + options["providers"])
    sel_food_type = f3.selectbox("Food Type", ["All"] + options["food_types"])
    sel_meal_type = f4.selectbox("Meal Type", ["All"] + options["meal_types"])

    where_clauses = []
    params = {}
    if sel_city != "All":
        where_clauses.append("f.Location = :city")
        params["city"] = sel_city
    if sel_provider != "All":
        where_clauses.append("p.Name = :provider")
        params["provider"] = sel_provider
    if sel_food_type != "All":
        where_clauses.append("f.Food_Type = :food_type")
        params["food_type"] = sel_food_type
    if sel_meal_type != "All":
        where_clauses.append("f.Meal_Type = :meal_type")
        params["meal_type"] = sel_meal_type

    where_sql = ("WHERE " + " AND ".join(where_clauses)) if where_clauses else ""

    sql = f"""
        SELECT f.Food_ID, f.Food_Name, f.Quantity, f.Expiry_Date,
               p.Name AS Provider_Name, p.Contact AS Provider_Contact,
               f.Location, f.Food_Type, f.Meal_Type
        FROM food_listings f
        JOIN providers p ON f.Provider_ID = p.Provider_ID
        {where_sql}
        ORDER BY f.Expiry_Date ASC
    """
    results = run_query(sql, params)
    st.write(f"**{len(results)}** matching listings — providers' contact info is included so you can coordinate pickup directly.")
    st.dataframe(results, use_container_width=True, hide_index=True)

    st.divider()
    st.subheader("Look up provider contact info by city")
    lookup_city = st.selectbox("Select a city", options["cities"], key="lookup_city")
    if lookup_city:
        contacts = provider_contacts_by_city(lookup_city)
        st.dataframe(contacts, use_container_width=True, hide_index=True)

# ======================================================================
# PAGE 3: ANALYSIS — all 15+ queries
# ======================================================================
elif page == "Analysis (15 Queries)":
    st.subheader("SQL-Powered Analysis")
    st.caption("Each section below runs a real SQL query against the database and shows the result.")

    labels = [label for label, _, _ in QUERY_REGISTRY]
    selected = st.selectbox("Choose a query to view", labels)

    for label, func, chart_hint in QUERY_REGISTRY:
        if label == selected:
            df = func()
            st.dataframe(df, use_container_width=True, hide_index=True)

            # Auto-chart when there's a sensible categorical + numeric pair
            if df.shape[1] == 2 and df.shape[0] > 1:
                cat_col, num_col = df.columns[0], df.columns[1]
                if df[num_col].dtype.kind in "if":
                    fig = px.bar(df.head(15), x=cat_col, y=num_col,
                                 color_discrete_sequence=["#2D6A4F"])
                    st.plotly_chart(fig, use_container_width=True)
            break

    with st.expander("Show all 16 queries at once"):
        for label, func, _ in QUERY_REGISTRY:
            st.markdown(f"**{label}**")
            st.dataframe(func(), use_container_width=True, hide_index=True)
            st.markdown("---")

# ======================================================================
# PAGE 4: CRUD — Manage food listing records
# ======================================================================
elif page == "Manage Records (CRUD)":
    st.subheader("Manage Food Listing Records")
    tab_add, tab_update, tab_delete = st.tabs(["➕ Add Listing", "✏️ Update Listing", "🗑️ Delete Listing"])

    # ---------------- ADD ----------------
    with tab_add:
        st.markdown("Add a new surplus food listing.")
        provider_df = run_query("SELECT Provider_ID, Name, Type FROM providers ORDER BY Name")
        provider_label = st.selectbox(
            "Provider",
            provider_df["Name"] + " (" + provider_df["Type"] + ")",
            key="add_provider",
        )
        provider_row = provider_df.iloc[
            (provider_df["Name"] + " (" + provider_df["Type"] + ")").tolist().index(provider_label)
        ]

        with st.form("add_form"):
            new_id = st.number_input("Food_ID (must be unique)", min_value=1, step=1)
            name = st.text_input("Food Name")
            qty = st.number_input("Quantity", min_value=1, step=1)
            expiry = st.date_input("Expiry Date")
            location = st.text_input("Location (city)")
            food_type = st.selectbox("Food Type", ["Vegetarian", "Non-Vegetarian", "Vegan"])
            meal_type = st.selectbox("Meal Type", ["Breakfast", "Lunch", "Dinner", "Snacks"])
            submitted = st.form_submit_button("Add Listing")

            if submitted:
                existing = run_query("SELECT 1 FROM food_listings WHERE Food_ID = :id", {"id": new_id})
                if not existing.empty:
                    st.error(f"Food_ID {new_id} already exists. Choose a different ID.")
                elif not name or not location:
                    st.error("Food Name and Location are required.")
                else:
                    run_statement("""
                        INSERT INTO food_listings
                            (Food_ID, Food_Name, Quantity, Expiry_Date, Provider_ID,
                             Provider_Type, Location, Food_Type, Meal_Type)
                        VALUES
                            (:id, :name, :qty, :expiry, :provider_id,
                             :provider_type, :location, :food_type, :meal_type)
                    """, {
                        "id": int(new_id), "name": name, "qty": int(qty), "expiry": expiry,
                        "provider_id": int(provider_row["Provider_ID"]),
                        "provider_type": provider_row["Type"],
                        "location": location, "food_type": food_type, "meal_type": meal_type,
                    })
                    st.success(f"Added '{name}' (Food_ID {new_id}).")

    # ---------------- UPDATE ----------------
    with tab_update:
        st.markdown("Update an existing listing's quantity or expiry date.")
        all_ids = run_query("SELECT Food_ID, Food_Name FROM food_listings ORDER BY Food_ID")
        target_label = st.selectbox(
            "Select listing",
            all_ids["Food_ID"].astype(str) + " — " + all_ids["Food_Name"],
            key="update_select",
        )
        target_id = int(target_label.split(" — ")[0])
        current = run_query("SELECT * FROM food_listings WHERE Food_ID = :id", {"id": target_id}).iloc[0]

        with st.form("update_form"):
            new_qty = st.number_input("Quantity", min_value=0, step=1, value=int(current["Quantity"]))
            new_expiry = st.date_input("Expiry Date", value=current["Expiry_Date"])
            update_submitted = st.form_submit_button("Update Listing")

            if update_submitted:
                run_statement("""
                    UPDATE food_listings SET Quantity = :qty, Expiry_Date = :expiry
                    WHERE Food_ID = :id
                """, {"qty": int(new_qty), "expiry": new_expiry, "id": target_id})
                st.success(f"Updated Food_ID {target_id}.")

    # ---------------- DELETE ----------------
    with tab_delete:
        st.markdown("Remove a listing (this also removes any linked claims).")
        all_ids2 = run_query("SELECT Food_ID, Food_Name FROM food_listings ORDER BY Food_ID")
        delete_label = st.selectbox(
            "Select listing to delete",
            all_ids2["Food_ID"].astype(str) + " — " + all_ids2["Food_Name"],
            key="delete_select",
        )
        delete_id = int(delete_label.split(" — ")[0])
        st.warning(f"This will permanently delete Food_ID {delete_id} and any associated claims.")
        confirm = st.checkbox("I understand this cannot be undone.")
        if st.button("Delete Listing", disabled=not confirm):
            run_statement("DELETE FROM food_listings WHERE Food_ID = :id", {"id": delete_id})
            st.success(f"Deleted Food_ID {delete_id}.")
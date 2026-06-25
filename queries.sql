-- ============================================================
-- Local Food Wastage Management System
-- 15 SQL Analysis Queries  (MySQL syntax)
-- Run after schema.sql + load_data.py
-- ============================================================
USE food_wastage;

-- ============================================================
-- SECTION A: FOOD PROVIDERS & RECEIVERS
-- ============================================================

-- Q1. How many food providers and receivers are there in each city?
SELECT
    City,
    COUNT(DISTINCT Provider_ID) AS Provider_Count
FROM providers
GROUP BY City
ORDER BY Provider_Count DESC;

-- (companion) receivers per city
SELECT
    City,
    COUNT(DISTINCT Receiver_ID) AS Receiver_Count
FROM receivers
GROUP BY City
ORDER BY Receiver_Count DESC;

-- Q2. Which type of food provider contributes the most food (by quantity)?
SELECT
    p.Type AS Type,
    SUM(f.Quantity) AS Total_Quantity_Contributed
FROM food_listings f
JOIN providers p ON f.Provider_ID = p.Provider_ID
GROUP BY p.Type
ORDER BY Total_Quantity_Contributed DESC;

-- Q3. What is the contact information of food providers in a specific city?
-- (Example city = 'New Jessica' — change as needed, or parameterize in the app)
SELECT Name, Type, Address, Contact
FROM providers
WHERE City = 'New Jessica';

-- Q4. Which receivers have claimed the most food (by quantity successfully received)?
SELECT
    r.Receiver_ID,
    r.Name,
    r.Type,
    SUM(f.Quantity) AS Total_Quantity_Claimed
FROM claims c
JOIN receivers r ON c.Receiver_ID = r.Receiver_ID
JOIN food_listings f ON c.Food_ID = f.Food_ID
WHERE c.Status = 'Completed'
GROUP BY r.Receiver_ID, r.Name, r.Type
ORDER BY Total_Quantity_Claimed DESC
LIMIT 10;

-- ============================================================
-- SECTION B: FOOD LISTINGS & AVAILABILITY
-- ============================================================

-- Q5. What is the total quantity of food available from all providers?
SELECT SUM(Quantity) AS Total_Quantity_Available
FROM food_listings;

-- Q6. Which city has the highest number of food listings?
SELECT
    Location AS City,
    COUNT(*) AS Listing_Count
FROM food_listings
GROUP BY Location
ORDER BY Listing_Count DESC
LIMIT 10;

-- Q7. What are the most commonly available food types?
SELECT
    Food_Type,
    COUNT(*) AS Listing_Count,
    SUM(Quantity) AS Total_Quantity
FROM food_listings
GROUP BY Food_Type
ORDER BY Listing_Count DESC;

-- ============================================================
-- SECTION C: CLAIMS & DISTRIBUTION
-- ============================================================

-- Q8. How many food claims have been made for each food item?
SELECT
    f.Food_ID,
    f.Food_Name,
    COUNT(c.Claim_ID) AS Claim_Count
FROM food_listings f
LEFT JOIN claims c ON f.Food_ID = c.Food_ID
GROUP BY f.Food_ID, f.Food_Name
ORDER BY Claim_Count DESC
LIMIT 15;

-- Q9. Which provider has had the highest number of successful (Completed) food claims?
SELECT
    p.Provider_ID,
    p.Name,
    p.Type,
    COUNT(c.Claim_ID) AS Successful_Claims
FROM claims c
JOIN food_listings f ON c.Food_ID = f.Food_ID
JOIN providers p ON f.Provider_ID = p.Provider_ID
WHERE c.Status = 'Completed'
GROUP BY p.Provider_ID, p.Name, p.Type
ORDER BY Successful_Claims DESC
LIMIT 10;

-- Q10. What percentage of food claims are Completed vs Pending vs Cancelled?
SELECT
    Status,
    COUNT(*) AS Count_Of_Claims,
    ROUND(COUNT(*) * 100.0 / (SELECT COUNT(*) FROM claims), 2) AS Percentage
FROM claims
GROUP BY Status
ORDER BY Count_Of_Claims DESC;

-- ============================================================
-- SECTION D: ANALYSIS & INSIGHTS
-- ============================================================

-- Q11. What is the average quantity of food claimed per receiver (Completed claims only)?
SELECT
    ROUND(AVG(receiver_totals.Total_Quantity), 2) AS Avg_Quantity_Claimed_Per_Receiver
FROM (
    SELECT
        c.Receiver_ID,
        SUM(f.Quantity) AS Total_Quantity
    FROM claims c
    JOIN food_listings f ON c.Food_ID = f.Food_ID
    WHERE c.Status = 'Completed'
    GROUP BY c.Receiver_ID
) AS receiver_totals;

-- Q12. Which meal type is claimed the most?
SELECT
    f.Meal_Type,
    COUNT(c.Claim_ID) AS Claim_Count
FROM claims c
JOIN food_listings f ON c.Food_ID = f.Food_ID
GROUP BY f.Meal_Type
ORDER BY Claim_Count DESC;

-- Q13. What is the total quantity of food donated by each provider?
SELECT
    p.Provider_ID,
    p.Name,
    p.Type,
    SUM(f.Quantity) AS Total_Quantity_Donated
FROM food_listings f
JOIN providers p ON f.Provider_ID = p.Provider_ID
GROUP BY p.Provider_ID, p.Name, p.Type
ORDER BY Total_Quantity_Donated DESC
LIMIT 15;

-- ============================================================
-- SECTION E: EXTRA INSIGHTS (beyond the required 13, to exceed "15+")
-- ============================================================

-- Q14. Which food items are nearing expiry (within next 3 days of listing's max expiry) and still unclaimed?
-- Useful for the "reduce waste" business goal.
SELECT
    f.Food_ID,
    f.Food_Name,
    f.Quantity,
    f.Expiry_Date,
    f.Location
FROM food_listings f
LEFT JOIN claims c ON f.Food_ID = c.Food_ID AND c.Status = 'Completed'
WHERE c.Claim_ID IS NULL
ORDER BY f.Expiry_Date ASC
LIMIT 15;

-- Q15. Claim status breakdown by city (where the food was listed)
SELECT
    f.Location AS City,
    c.Status,
    COUNT(*) AS Claim_Count
FROM claims c
JOIN food_listings f ON c.Food_ID = f.Food_ID
GROUP BY f.Location, c.Status
ORDER BY City, Claim_Count DESC;

-- Q16. Top 5 receiver types by number of claims made (any status)
SELECT
    r.Type AS Receiver_Type,
    COUNT(c.Claim_ID) AS Total_Claims
FROM claims c
JOIN receivers r ON c.Receiver_ID = r.Receiver_ID
GROUP BY r.Type
ORDER BY Total_Claims DESC;

-- ============================================================
-- Local Food Wastage Management System - Database Schema
-- MySQL
-- ============================================================

CREATE DATABASE food_wastage;
USE food_wastage;

DROP TABLE IF EXISTS claims;
DROP TABLE IF EXISTS food_listings;
DROP TABLE IF EXISTS receivers;
DROP TABLE IF EXISTS providers;

-- ------------------------------------------------------------
-- Providers: who is donating food
-- ------------------------------------------------------------
CREATE TABLE providers (
    Provider_ID   INT PRIMARY KEY,
    Name          VARCHAR(255) NOT NULL,
    Type          VARCHAR(100) NOT NULL,
    Address       VARCHAR(500),
    City          VARCHAR(150) NOT NULL,
    Contact       VARCHAR(100)
);

-- ------------------------------------------------------------
-- Receivers: who is claiming food
-- ------------------------------------------------------------
CREATE TABLE receivers (
    Receiver_ID   INT PRIMARY KEY,
    Name          VARCHAR(255) NOT NULL,
    Type          VARCHAR(100) NOT NULL,
    City          VARCHAR(150) NOT NULL,
    Contact       VARCHAR(100)
);

-- ------------------------------------------------------------
-- Food Listings: surplus food items available
-- ------------------------------------------------------------
CREATE TABLE food_listings (
    Food_ID        INT PRIMARY KEY,
    Food_Name      VARCHAR(255) NOT NULL,
    Quantity       INT NOT NULL,
    Expiry_Date    DATE NOT NULL,
    Provider_ID    INT NOT NULL,
    Provider_Type  VARCHAR(100),
    Location       VARCHAR(150),
    Food_Type      VARCHAR(50),
    Meal_Type      VARCHAR(50),
    CONSTRAINT fk_food_provider
        FOREIGN KEY (Provider_ID) REFERENCES providers(Provider_ID)
        ON DELETE CASCADE
);

-- ------------------------------------------------------------
-- Claims: each claim made on a food item by a receiver
-- ------------------------------------------------------------
CREATE TABLE claims (
    Claim_ID      INT PRIMARY KEY,
    Food_ID       INT NOT NULL,
    Receiver_ID   INT NOT NULL,
    Status        VARCHAR(20) NOT NULL,
    Timestamp     DATETIME NOT NULL,
    CONSTRAINT fk_claims_food
        FOREIGN KEY (Food_ID) REFERENCES food_listings(Food_ID)
        ON DELETE CASCADE,
    CONSTRAINT fk_claims_receiver
        FOREIGN KEY (Receiver_ID) REFERENCES receivers(Receiver_ID)
        ON DELETE CASCADE
);

-- Helpful indexes for the analysis queries / app filters
CREATE DATABASE food_wastage;
USE food_wastage;
CREATE INDEX idx_food_location ON food_listings(Location);
CREATE INDEX idx_food_type ON food_listings(Food_Type);
CREATE INDEX idx_food_provider ON food_listings(Provider_ID);
CREATE INDEX idx_claims_status ON claims(Status);
CREATE INDEX idx_claims_food ON claims(Food_ID);
CREATE INDEX idx_claims_receiver ON claims(Receiver_ID);
CREATE INDEX idx_provider_city ON providers(City);
CREATE INDEX idx_receiver_city ON receivers(City);

CREATE INDEX idx_food_location ON food_listings(Location);
CREATE INDEX idx_food_type ON food_listings(Food_Type);
CREATE INDEX idx_food_provider ON food_listings(Provider_ID);
CREATE INDEX idx_claims_status ON claims(Status);
CREATE INDEX idx_claims_food ON claims(Food_ID);
CREATE INDEX idx_claims_receiver ON claims(Receiver_ID);
CREATE INDEX idx_provider_city ON providers(City);
CREATE INDEX idx_receiver_city ON receivers(City);

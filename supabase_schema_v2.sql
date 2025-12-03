-- ============================================================================
-- GALAPAGOS CAR TRACKING - STREAMLINED DATABASE SCHEMA
-- ============================================================================
-- COPY THIS ENTIRE FILE AND RUN IT IN SUPABASE SQL EDITOR
-- ============================================================================

-- ============================================================================
-- CLEANUP: Drop old tables if they exist with wrong columns
-- ============================================================================
DROP TABLE IF EXISTS trips CASCADE;
DROP TABLE IF EXISTS "TripData" CASCADE;

-- ============================================================================
-- TABLE: TripData (NEW - ONE ROW PER COMPLETED TRIP)
-- ============================================================================
-- This table stores ONE summary row for each completed trip
-- Much cleaner than storing hundreds of GPS points!
-- ============================================================================

CREATE TABLE "TripData" (
    -- Auto-incrementing ID
    id BIGSERIAL PRIMARY KEY,
    
    -- Trip identification
    trip_id TEXT NOT NULL UNIQUE,
    username TEXT NOT NULL,
    company TEXT,
    car_number TEXT,
    
    -- Where and who
    destination TEXT,
    passenger_type TEXT,
    passenger_count TEXT,
    cargo_type TEXT,
    
    -- Trip measurements
    distance_km DECIMAL(10, 3),
    duration_seconds INTEGER,
    fuel_gallons DECIMAL(10, 3),
    
    -- When
    start_time TIMESTAMP WITH TIME ZONE,
    end_time TIMESTAMP WITH TIME ZONE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT TIMEZONE('utc'::text, NOW())
);


-- ============================================================================
-- INDEXES (Makes queries faster)
-- ============================================================================

CREATE INDEX IF NOT EXISTS idx_tripdata_trip_id ON "TripData"(trip_id);
CREATE INDEX IF NOT EXISTS idx_tripdata_username ON "TripData"(username);
CREATE INDEX IF NOT EXISTS idx_tripdata_start_time ON "TripData"(start_time);
CREATE INDEX IF NOT EXISTS idx_tripdata_username_start_time ON "TripData"(username, start_time);


-- ============================================================================
-- SECURITY SETTINGS (Row Level Security)
-- ============================================================================

ALTER TABLE "TripData" ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Allow all access to TripData" ON "TripData"
    FOR ALL USING (true) WITH CHECK (true);


-- ============================================================================
-- DONE! 
-- ============================================================================
-- After running this SQL:
-- 1. Go to "Table Editor" in Supabase
-- 2. You should see a new table called "TripData"
-- 3. It will be empty until you complete a trip in the app
-- 4. Each completed trip will add ONE row to this table
-- ============================================================================

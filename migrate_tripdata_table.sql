-- Migration: Rebuild TripData table to match app column names
-- Run this in the Supabase SQL Editor (Dashboard → SQL Editor → New Query)

-- Step 1: Drop the old TripData table (all old data will be lost)
DROP TABLE IF EXISTS "TripData";

-- Step 2: Create TripData with the correct columns that the app sends
CREATE TABLE "TripData" (
    id              BIGSERIAL PRIMARY KEY,
    trip_id         TEXT NOT NULL,
    username        TEXT NOT NULL,
    company         TEXT,
    car_number      TEXT,
    destination     TEXT,
    passenger_type  TEXT,
    passenger_count TEXT,
    cargo_type      TEXT,
    distance_km     FLOAT DEFAULT 0,
    duration_seconds INTEGER DEFAULT 0,
    fuel_gallons    FLOAT DEFAULT 0,
    start_time      TIMESTAMP WITH TIME ZONE,
    end_time        TIMESTAMP WITH TIME ZONE,
    starting_point  TEXT,
    created_at      TIMESTAMP WITH TIME ZONE DEFAULT TIMEZONE('utc'::text, NOW())
);

-- Step 3: Indexes
CREATE INDEX IF NOT EXISTS idx_tripdata_username   ON "TripData"(username);
CREATE INDEX IF NOT EXISTS idx_tripdata_trip_id    ON "TripData"(trip_id);
CREATE INDEX IF NOT EXISTS idx_tripdata_start_time ON "TripData"(start_time);

-- Step 4: Row Level Security
ALTER TABLE "TripData" ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Enable read access for all users"   ON "TripData" FOR SELECT USING (true);
CREATE POLICY "Enable insert access for all users" ON "TripData" FOR INSERT WITH CHECK (true);
CREATE POLICY "Enable update access for all users" ON "TripData" FOR UPDATE USING (true);
CREATE POLICY "Enable delete access for all users" ON "TripData" FOR DELETE USING (true);

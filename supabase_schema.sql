-- Supabase Database Schema for Galapagos Car Tracking App
-- Run this SQL in your Supabase SQL Editor to create the required tables

-- Table: UserData
-- Stores user account information
CREATE TABLE IF NOT EXISTS "UserData" (
    username TEXT PRIMARY KEY,
    password TEXT NOT NULL,
    name TEXT NOT NULL,
    phone TEXT NOT NULL UNIQUE,
    company1 TEXT,
    comp1num TEXT,
    company2 TEXT,
    comp2num TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT TIMEZONE('utc'::text, NOW())
);

-- Table: TrackingData
-- Stores GPS tracking data points for trips
CREATE TABLE IF NOT EXISTS "TrackingData" (
    id BIGSERIAL PRIMARY KEY,
    tripID TEXT NOT NULL,
    company TEXT,
    carnum TEXT,
    destinationXstatus TEXT,
    passengersXtotalTime TEXT,
    cargoXtotalDist TEXT,
    gpslonXworkingFuel TEXT,
    gpslat TEXT,
    time TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT TIMEZONE('utc'::text, NOW())
);

-- Create indexes for better query performance
CREATE INDEX IF NOT EXISTS idx_trackingdata_tripid ON "TrackingData"(tripID);
CREATE INDEX IF NOT EXISTS idx_trackingdata_destinationstatus ON "TrackingData"(destinationXstatus);
CREATE INDEX IF NOT EXISTS idx_trackingdata_tripid_destination ON "TrackingData"(tripID, destinationXstatus);

-- Enable Row Level Security (RLS)
ALTER TABLE "UserData" ENABLE ROW LEVEL SECURITY;
ALTER TABLE "TrackingData" ENABLE ROW LEVEL SECURITY;

-- Create policies for public access (you may want to modify these for production)
-- These policies allow anyone with the anon key to read and write
CREATE POLICY "Enable read access for all users" ON "UserData"
    FOR SELECT USING (true);

CREATE POLICY "Enable insert access for all users" ON "UserData"
    FOR INSERT WITH CHECK (true);

CREATE POLICY "Enable update access for all users" ON "UserData"
    FOR UPDATE USING (true);

CREATE POLICY "Enable delete access for all users" ON "UserData"
    FOR DELETE USING (true);

CREATE POLICY "Enable read access for all users" ON "TrackingData"
    FOR SELECT USING (true);

CREATE POLICY "Enable insert access for all users" ON "TrackingData"
    FOR INSERT WITH CHECK (true);

CREATE POLICY "Enable update access for all users" ON "TrackingData"
    FOR UPDATE USING (true);

CREATE POLICY "Enable delete access for all users" ON "TrackingData"
    FOR DELETE USING (true);

-- Note: For production, you should implement more restrictive RLS policies
-- For example, users should only be able to access their own data

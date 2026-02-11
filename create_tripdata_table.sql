-- Create TripData table in Supabase
-- Run this SQL in your Supabase SQL Editor

-- Table: TripData
-- Stores GPS tracking data points for trips
CREATE TABLE IF NOT EXISTS "TripData" (
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
CREATE INDEX IF NOT EXISTS idx_tripdata_tripid ON "TripData"(tripID);
CREATE INDEX IF NOT EXISTS idx_tripdata_destinationstatus ON "TripData"(destinationXstatus);
CREATE INDEX IF NOT EXISTS idx_tripdata_tripid_destination ON "TripData"(tripID, destinationXstatus);

-- Enable Row Level Security (RLS)
ALTER TABLE "TripData" ENABLE ROW LEVEL SECURITY;

-- Create policies for public access
CREATE POLICY "Enable read access for all users" ON "TripData"
    FOR SELECT USING (true);

CREATE POLICY "Enable insert access for all users" ON "TripData"
    FOR INSERT WITH CHECK (true);

CREATE POLICY "Enable update access for all users" ON "TripData"
    FOR UPDATE USING (true);

CREATE POLICY "Enable delete access for all users" ON "TripData"
    FOR DELETE USING (true);

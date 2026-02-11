-- ============================================================================
-- GALAPAGOS CAR TRACKING - WEEKLY TRIP STATISTICS BY COMPANY
-- ============================================================================
-- Organized by week, then by company within each week
-- ============================================================================


-- ============================================================================
-- WEEKLY OVERVIEW - All Weeks Summary
-- ============================================================================

SELECT 
    '📊 OVERALL SUMMARY' AS report_section,
    DATE_TRUNC('week', start_time)::DATE AS week_start,
    (DATE_TRUNC('week', start_time) + INTERVAL '6 days')::DATE AS week_end,
    COUNT(*) AS total_trips,
    COUNT(DISTINCT company) AS companies,
    COUNT(DISTINCT username) AS drivers,
    COUNT(DISTINCT car_number) AS vehicles,
    ROUND(SUM(distance_km)::NUMERIC, 2) AS total_km,
    ROUND(AVG(distance_km)::NUMERIC, 2) AS avg_km,
    TO_CHAR((SUM(duration_seconds) || ' seconds')::INTERVAL, 'HH24:MI:SS') AS total_duration,
    ROUND(SUM(fuel_gallons)::NUMERIC, 2) AS fuel_gal,
    ROUND((SUM(fuel_gallons) / NULLIF(SUM(distance_km), 0) * 100)::NUMERIC, 2) AS gal_per_100km
FROM "TripData"
WHERE start_time >= DATE_TRUNC('week', CURRENT_DATE)
  AND start_time < DATE_TRUNC('week', CURRENT_DATE) + INTERVAL '1 week'
GROUP BY DATE_TRUNC('week', start_time)
ORDER BY week_start DESC;


-- ============================================================================
-- WEEKLY BY COMPANY - Company Performance Each Week
-- ============================================================================

SELECT 
    '🏢 WEEKLY BY COMPANY' AS report_section,
    DATE_TRUNC('week', start_time)::DATE AS week_start,
    COALESCE(company, 'Unassigned') AS company,
    COUNT(*) AS trips,
    COUNT(DISTINCT username) AS drivers,
    COUNT(DISTINCT car_number) AS vehicles,
    COUNT(DISTINCT destination) AS destinations,
    ROUND(SUM(distance_km)::NUMERIC, 2) AS total_km,
    ROUND(AVG(distance_km)::NUMERIC, 2) AS avg_km_per_trip,
    TO_CHAR((SUM(duration_seconds) || ' seconds')::INTERVAL, 'HH24:MI:SS') AS total_time,
    TO_CHAR((AVG(duration_seconds) || ' seconds')::INTERVAL, 'HH24:MI:SS') AS avg_time,
    ROUND(SUM(fuel_gallons)::NUMERIC, 2) AS fuel_gal,
    ROUND((SUM(fuel_gallons) / NULLIF(SUM(distance_km), 0) * 100)::NUMERIC, 2) AS gal_per_100km
FROM "TripData"
WHERE start_time >= DATE_TRUNC('week', CURRENT_DATE)
  AND start_time < DATE_TRUNC('week', CURRENT_DATE) + INTERVAL '1 week'
GROUP BY DATE_TRUNC('week', start_time), company
ORDER BY week_start DESC, trips DESC;


-- ============================================================================
-- DAILY BY COMPANY - Day-by-Day Company Breakdown
-- ============================================================================

SELECT 
    '📅 DAILY BY COMPANY' AS report_section,
    start_time::DATE AS date,
    TO_CHAR(start_time, 'Day') AS day_of_week,
    COALESCE(company, 'Unassigned') AS company,
    COUNT(*) AS trips,
    COUNT(DISTINCT username) AS drivers,
    ROUND(SUM(distance_km)::NUMERIC, 2) AS total_km,
    ROUND(AVG(distance_km)::NUMERIC, 2) AS avg_km,
    ROUND(SUM(fuel_gallons)::NUMERIC, 2) AS fuel_gal
FROM "TripData"
WHERE start_time >= DATE_TRUNC('week', CURRENT_DATE)
  AND start_time < DATE_TRUNC('week', CURRENT_DATE) + INTERVAL '1 week'
GROUP BY date, day_of_week, company, EXTRACT(DOW FROM start_time)
ORDER BY date, company;


-- ============================================================================
-- DRIVERS BY COMPANY - Individual Driver Performance
-- ============================================================================

SELECT 
    '👤 DRIVERS BY COMPANY' AS report_section,
    COALESCE(company, 'Unassigned') AS company,
    username,
    COUNT(*) AS trips,
    ROUND(SUM(distance_km)::NUMERIC, 2) AS total_km,
    ROUND(AVG(distance_km)::NUMERIC, 2) AS avg_km,
    TO_CHAR((SUM(duration_seconds) || ' seconds')::INTERVAL, 'HH24:MI:SS') AS total_time,
    ROUND(SUM(fuel_gallons)::NUMERIC, 2) AS fuel_gal,
    ROUND((SUM(fuel_gallons) / NULLIF(SUM(distance_km), 0) * 100)::NUMERIC, 2) AS gal_per_100km,
    COUNT(DISTINCT destination) AS destinations,
    COUNT(DISTINCT car_number) AS vehicles_used
FROM "TripData"
WHERE start_time >= DATE_TRUNC('week', CURRENT_DATE)
  AND start_time < DATE_TRUNC('week', CURRENT_DATE) + INTERVAL '1 week'
GROUP BY company, username
ORDER BY company, trips DESC;


-- ============================================================================
-- VEHICLES BY COMPANY - Car Utilization
-- ============================================================================

SELECT 
    '🚗 VEHICLES BY COMPANY' AS report_section,
    COALESCE(company, 'Unassigned') AS company,
    car_number,
    COUNT(*) AS trips,
    COUNT(DISTINCT username) AS drivers,
    ROUND(SUM(distance_km)::NUMERIC, 2) AS total_km,
    ROUND(AVG(distance_km)::NUMERIC, 2) AS avg_km,
    TO_CHAR((SUM(duration_seconds) || ' seconds')::INTERVAL, 'HH24:MI:SS') AS total_usage,
    ROUND(SUM(fuel_gallons)::NUMERIC, 2) AS fuel_gal,
    ROUND((SUM(fuel_gallons) / NULLIF(SUM(distance_km), 0) * 100)::NUMERIC, 2) AS gal_per_100km
FROM "TripData"
WHERE start_time >= DATE_TRUNC('week', CURRENT_DATE)
  AND start_time < DATE_TRUNC('week', CURRENT_DATE) + INTERVAL '1 week'
  AND car_number IS NOT NULL
  AND car_number != ''
GROUP BY company, car_number
ORDER BY company, trips DESC;


-- ============================================================================
-- DESTINATIONS BY COMPANY - Where Each Company Travels
-- ============================================================================

SELECT 
    '📍 DESTINATIONS BY COMPANY' AS report_section,
    COALESCE(company, 'Unassigned') AS company,
    destination,
    COUNT(*) AS visits,
    COUNT(DISTINCT username) AS drivers,
    ROUND(AVG(distance_km)::NUMERIC, 2) AS avg_km,
    ROUND(SUM(distance_km)::NUMERIC, 2) AS total_km,
    TO_CHAR((AVG(duration_seconds) || ' seconds')::INTERVAL, 'HH24:MI:SS') AS avg_time,
    ROUND(AVG(fuel_gallons)::NUMERIC, 2) AS avg_fuel_gal
FROM "TripData"
WHERE start_time >= DATE_TRUNC('week', CURRENT_DATE)
  AND start_time < DATE_TRUNC('week', CURRENT_DATE) + INTERVAL '1 week'
  AND destination IS NOT NULL
  AND destination != ''
GROUP BY company, destination
ORDER BY company, visits DESC;


-- ============================================================================
-- PASSENGER TYPES BY COMPANY - Trip Purpose Analysis
-- ============================================================================

SELECT 
    '🧳 PASSENGER TYPES BY COMPANY' AS report_section,
    COALESCE(company, 'Unassigned') AS company,
    COALESCE(passenger_type, 'Not Specified') AS passenger_type,
    COUNT(*) AS trips,
    ROUND((COUNT(*) * 100.0 / SUM(COUNT(*)) OVER (PARTITION BY company))::NUMERIC, 1) AS pct_of_company,
    ROUND(AVG(CASE WHEN passenger_count ~ '^[0-9]+$' 
        THEN passenger_count::INTEGER 
        ELSE NULL END)::NUMERIC, 1) AS avg_passengers,
    ROUND(SUM(distance_km)::NUMERIC, 2) AS total_km,
    ROUND(AVG(distance_km)::NUMERIC, 2) AS avg_km,
    ROUND(SUM(fuel_gallons)::NUMERIC, 2) AS fuel_gal
FROM "TripData"
WHERE start_time >= DATE_TRUNC('week', CURRENT_DATE)
  AND start_time < DATE_TRUNC('week', CURRENT_DATE) + INTERVAL '1 week'
GROUP BY company, passenger_type
ORDER BY company, trips DESC;


-- ============================================================================
-- FUEL EFFICIENCY BY COMPANY - Top Performers
-- ============================================================================

SELECT 
    '⚡ FUEL EFFICIENCY BY COMPANY' AS report_section,
    COALESCE(company, 'Unassigned') AS company,
    username,
    COUNT(*) AS trips,
    ROUND(SUM(distance_km)::NUMERIC, 2) AS total_km,
    ROUND(SUM(fuel_gallons)::NUMERIC, 2) AS fuel_gal,
    ROUND((SUM(distance_km) / NULLIF(SUM(fuel_gallons), 0))::NUMERIC, 2) AS km_per_gal,
    ROUND((SUM(fuel_gallons) / NULLIF(SUM(distance_km), 0) * 100)::NUMERIC, 3) AS gal_per_100km
FROM "TripData"
WHERE start_time >= DATE_TRUNC('week', CURRENT_DATE)
  AND start_time < DATE_TRUNC('week', CURRENT_DATE) + INTERVAL '1 week'
  AND fuel_gallons > 0
  AND distance_km > 0
GROUP BY company, username
HAVING COUNT(*) >= 3
ORDER BY company, km_per_gal DESC;


-- ============================================================================
-- LONGEST TRIPS BY COMPANY - Top Distances
-- ============================================================================

SELECT 
    '🏆 LONGEST TRIPS BY COMPANY' AS report_section,
    COALESCE(company, 'Unassigned') AS company,
    trip_id,
    username,
    destination,
    car_number,
    ROUND(distance_km::NUMERIC, 2) AS distance_km,
    TO_CHAR((duration_seconds || ' seconds')::INTERVAL, 'HH24:MI:SS') AS duration,
    ROUND(fuel_gallons::NUMERIC, 2) AS fuel_gal,
    start_time::TIMESTAMP AS started_at
FROM "TripData"
WHERE start_time >= DATE_TRUNC('week', CURRENT_DATE)
  AND start_time < DATE_TRUNC('week', CURRENT_DATE) + INTERVAL '1 week'
ORDER BY company, distance_km DESC;


-- ============================================================================
-- HOURLY ACTIVITY BY COMPANY - Peak Hours
-- ============================================================================

SELECT 
    '⏰ HOURLY ACTIVITY BY COMPANY' AS report_section,
    COALESCE(company, 'Unassigned') AS company,
    EXTRACT(HOUR FROM start_time) AS hour,
    TO_CHAR(TO_TIMESTAMP(EXTRACT(HOUR FROM start_time) * 3600), 'HH12:00 AM') AS time,
    COUNT(*) AS trips,
    ROUND(SUM(distance_km)::NUMERIC, 2) AS total_km,
    COUNT(DISTINCT username) AS drivers
FROM "TripData"
WHERE start_time >= DATE_TRUNC('week', CURRENT_DATE)
  AND start_time < DATE_TRUNC('week', CURRENT_DATE) + INTERVAL '1 week'
GROUP BY company, hour
ORDER BY company, hour;


-- ============================================================================
-- QUICK COMPANY COMPARISON - Single View
-- ============================================================================

SELECT 
    '📈 COMPANY COMPARISON' AS report_section,
    COALESCE(company, 'Unassigned') AS company,
    COUNT(*) AS trips,
    COUNT(DISTINCT username) AS drivers,
    COUNT(DISTINCT car_number) AS vehicles,
    ROUND(SUM(distance_km)::NUMERIC, 1) AS total_km,
    ROUND(AVG(distance_km)::NUMERIC, 1) AS avg_km,
    ROUND(SUM(fuel_gallons)::NUMERIC, 1) AS fuel_gal,
    ROUND((SUM(fuel_gallons) / NULLIF(SUM(distance_km), 0) * 100)::NUMERIC, 2) AS gal_per_100km,
    TO_CHAR((SUM(duration_seconds) || ' seconds')::INTERVAL, 'HH24:MI:SS') AS total_time
FROM "TripData"
WHERE start_time >= DATE_TRUNC('week', CURRENT_DATE)
  AND start_time < DATE_TRUNC('week', CURRENT_DATE) + INTERVAL '1 week'
GROUP BY company
ORDER BY trips DESC;

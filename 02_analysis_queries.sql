-- ============================================================
-- Air Cargo / Airline Booking Analysis
-- Analysis Queries
-- ============================================================
-- Run these against the database created with 01_schema.sql
-- and populated via the CSVs in /data.
-- ============================================================


-- ------------------------------------------------------------
-- 1. BUSIEST ROUTES
-- Which origin-destination pairs carry the most passengers and revenue?
-- ------------------------------------------------------------
SELECT
    f.departure_airport,
    dep.city AS departure_city,
    f.arrival_airport,
    arr.city AS arrival_city,
    COUNT(DISTINCT f.flight_id) AS total_flights,
    COUNT(tf.ticket_no) AS total_passengers,
    ROUND(SUM(tf.amount), 2) AS total_revenue,
    ROUND(AVG(tf.amount), 2) AS avg_fare
FROM flights f
JOIN airports_data dep ON f.departure_airport = dep.airport_code
JOIN airports_data arr ON f.arrival_airport = arr.airport_code
LEFT JOIN ticket_flights tf ON f.flight_id = tf.flight_id
GROUP BY f.departure_airport, dep.city, f.arrival_airport, arr.city
ORDER BY total_passengers DESC
LIMIT 10;


-- ------------------------------------------------------------
-- 2. MONTHLY REVENUE TREND
-- Ticket sales trajectory across the year
-- ------------------------------------------------------------
SELECT
    DATE_TRUNC('month', book_date) AS month,
    COUNT(*) AS total_bookings,
    ROUND(SUM(total_amount), 2) AS total_revenue,
    ROUND(AVG(total_amount), 2) AS avg_booking_value
FROM bookings
GROUP BY 1
ORDER BY 1;


-- ------------------------------------------------------------
-- 3. REVENUE GROWTH: H1 vs H2
-- Headline metric — supports "25% increase in revenue collection"
-- ------------------------------------------------------------
SELECT
    CASE WHEN EXTRACT(MONTH FROM book_date) <= 6 THEN 'H1 (Jan-Jun)' ELSE 'H2 (Jul-Dec)' END AS period,
    COUNT(*) AS bookings,
    ROUND(SUM(total_amount), 2) AS revenue
FROM bookings
GROUP BY 1
ORDER BY 1;


-- ------------------------------------------------------------
-- 4. COMPLAINT VOLUME & RESOLUTION RATE: H1 vs H2
-- Headline metric — supports "15% reduction in customer complaints"
-- ------------------------------------------------------------
SELECT
    CASE WHEN EXTRACT(MONTH FROM complaint_date) <= 6 THEN 'H1 (Jan-Jun)' ELSE 'H2 (Jul-Dec)' END AS period,
    COUNT(*) AS total_complaints,
    ROUND(100.0 * SUM(CASE WHEN resolved THEN 1 ELSE 0 END) / COUNT(*), 1) AS pct_resolved
FROM complaints
GROUP BY 1
ORDER BY 1;


-- ------------------------------------------------------------
-- 5. COMPLAINT BREAKDOWN BY TYPE
-- What's actually driving customer dissatisfaction
-- ------------------------------------------------------------
SELECT
    complaint_type,
    COUNT(*) AS total,
    ROUND(100.0 * COUNT(*) / SUM(COUNT(*)) OVER (), 1) AS pct_of_total
FROM complaints
GROUP BY complaint_type
ORDER BY total DESC;


-- ------------------------------------------------------------
-- 6. BOOKING CHANNEL PERFORMANCE
-- Website / Mobile App / Travel Agent / Call Center — where's the money and volume?
-- ------------------------------------------------------------
SELECT
    channel,
    COUNT(*) AS total_bookings,
    ROUND(SUM(total_amount), 2) AS total_revenue,
    ROUND(AVG(total_amount), 2) AS avg_booking_value
FROM bookings
GROUP BY channel
ORDER BY total_bookings DESC;


-- ------------------------------------------------------------
-- 7. SEAT OCCUPANCY / LOAD FACTOR BY FLIGHT (highest)
-- Which flights are running near capacity (candidates for upsizing/
-- added frequency)
-- ------------------------------------------------------------
SELECT
    f.departure_airport || '-' || f.arrival_airport AS route,
    ac.model AS aircraft,
    ac.total_seats,
    COUNT(tf.ticket_no) AS seats_sold,
    ROUND(100.0 * COUNT(tf.ticket_no) / ac.total_seats, 1) AS load_factor_pct
FROM flights f
JOIN aircrafts_data ac ON f.aircraft_code = ac.aircraft_code
LEFT JOIN ticket_flights tf ON f.flight_id = tf.flight_id
WHERE f.status != 'Cancelled'
GROUP BY f.flight_id, f.departure_airport, f.arrival_airport, ac.model, ac.total_seats
ORDER BY load_factor_pct DESC
LIMIT 15;


-- ------------------------------------------------------------
-- 8. LOWEST LOAD FACTOR ROUTES (underperforming flights)
-- Complements query 7 — where operations could be trimmed or repriced
-- ------------------------------------------------------------
SELECT
    f.departure_airport || '-' || f.arrival_airport AS route,
    ac.model AS aircraft,
    ac.total_seats,
    COUNT(tf.ticket_no) AS seats_sold,
    ROUND(100.0 * COUNT(tf.ticket_no) / ac.total_seats, 1) AS load_factor_pct
FROM flights f
JOIN aircrafts_data ac ON f.aircraft_code = ac.aircraft_code
LEFT JOIN ticket_flights tf ON f.flight_id = tf.flight_id
WHERE f.status != 'Cancelled'
GROUP BY f.flight_id, f.departure_airport, f.arrival_airport, ac.model, ac.total_seats
ORDER BY load_factor_pct ASC
LIMIT 15;


-- ------------------------------------------------------------
-- 9. DELAY/CANCELLATION IMPACT ON COMPLAINTS
-- Quantifies how much operational reliability drives complaint volume
-- ------------------------------------------------------------
SELECT
    f.status,
    COUNT(DISTINCT tf.ticket_no) AS tickets_sold,
    COUNT(DISTINCT c.complaint_id) AS complaints_raised,
    ROUND(100.0 * COUNT(DISTINCT c.complaint_id) / NULLIF(COUNT(DISTINCT tf.ticket_no), 0), 1) AS complaint_rate_pct
FROM flights f
JOIN ticket_flights tf ON f.flight_id = tf.flight_id
LEFT JOIN complaints c ON c.flight_id = f.flight_id AND c.ticket_no = tf.ticket_no
GROUP BY f.status
ORDER BY complaint_rate_pct DESC;


-- ------------------------------------------------------------
-- 10. FARE CLASS REVENUE MIX
-- Economy vs Comfort vs Business contribution to revenue
-- ------------------------------------------------------------
SELECT
    fare_conditions,
    COUNT(*) AS tickets_sold,
    ROUND(SUM(amount), 2) AS total_revenue,
    ROUND(AVG(amount), 2) AS avg_fare,
    ROUND(100.0 * SUM(amount) / SUM(SUM(amount)) OVER (), 1) AS pct_of_revenue
FROM ticket_flights
GROUP BY fare_conditions
ORDER BY total_revenue DESC;

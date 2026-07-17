-- ============================================================
-- Air Cargo / Airline Booking Analysis
-- Schema definition (PostgreSQL)
-- ============================================================

DROP TABLE IF EXISTS complaints CASCADE;
DROP TABLE IF EXISTS boarding_passes CASCADE;
DROP TABLE IF EXISTS ticket_flights CASCADE;
DROP TABLE IF EXISTS tickets CASCADE;
DROP TABLE IF EXISTS bookings CASCADE;
DROP TABLE IF EXISTS seats CASCADE;
DROP TABLE IF EXISTS flights CASCADE;
DROP TABLE IF EXISTS aircrafts_data CASCADE;
DROP TABLE IF EXISTS airports_data CASCADE;

-- ------------------------------------------------------------
-- Reference tables
-- ------------------------------------------------------------

CREATE TABLE airports_data (
    airport_code    CHAR(3) PRIMARY KEY,
    airport_name    VARCHAR(100) NOT NULL,
    city            VARCHAR(100) NOT NULL,
    country         VARCHAR(100) NOT NULL,
    timezone        VARCHAR(50)
);

CREATE TABLE aircrafts_data (
    aircraft_code   CHAR(3) PRIMARY KEY,
    model           VARCHAR(50) NOT NULL,
    range_km        INT NOT NULL,
    total_seats     INT NOT NULL
);

CREATE TABLE seats (
    aircraft_code   CHAR(3) NOT NULL REFERENCES aircrafts_data(aircraft_code),
    seat_no         VARCHAR(4) NOT NULL,
    fare_conditions VARCHAR(10) NOT NULL CHECK (fare_conditions IN ('Economy','Comfort','Business')),
    PRIMARY KEY (aircraft_code, seat_no)
);

-- ------------------------------------------------------------
-- Operational tables
-- ------------------------------------------------------------

CREATE TABLE flights (
    flight_id           SERIAL PRIMARY KEY,
    flight_no           VARCHAR(6) NOT NULL,
    scheduled_departure  TIMESTAMP NOT NULL,
    scheduled_arrival    TIMESTAMP NOT NULL,
    actual_departure     TIMESTAMP,
    actual_arrival       TIMESTAMP,
    departure_airport   CHAR(3) NOT NULL REFERENCES airports_data(airport_code),
    arrival_airport     CHAR(3) NOT NULL REFERENCES airports_data(airport_code),
    aircraft_code       CHAR(3) NOT NULL REFERENCES aircrafts_data(aircraft_code),
    status              VARCHAR(20) NOT NULL CHECK (status IN ('Scheduled','On Time','Delayed','Cancelled','Arrived')),
    base_fare_economy   NUMERIC(10,2) NOT NULL
);

CREATE TABLE bookings (
    book_ref        CHAR(6) PRIMARY KEY,
    book_date       TIMESTAMP NOT NULL,
    total_amount    NUMERIC(12,2) NOT NULL,
    channel         VARCHAR(20) NOT NULL CHECK (channel IN ('Website','Mobile App','Travel Agent','Call Center'))
);

CREATE TABLE tickets (
    ticket_no       CHAR(10) PRIMARY KEY,
    book_ref        CHAR(6) NOT NULL REFERENCES bookings(book_ref),
    passenger_id    VARCHAR(15) NOT NULL,
    passenger_name  VARCHAR(100) NOT NULL,
    contact_email   VARCHAR(100)
);

CREATE TABLE ticket_flights (
    ticket_no       CHAR(10) NOT NULL REFERENCES tickets(ticket_no),
    flight_id       INT NOT NULL REFERENCES flights(flight_id),
    fare_conditions VARCHAR(10) NOT NULL CHECK (fare_conditions IN ('Economy','Comfort','Business')),
    amount          NUMERIC(10,2) NOT NULL,
    PRIMARY KEY (ticket_no, flight_id)
);

CREATE TABLE boarding_passes (
    ticket_no       CHAR(10) NOT NULL,
    flight_id       INT NOT NULL,
    boarding_no     INT,
    seat_no         VARCHAR(4) NOT NULL,
    PRIMARY KEY (ticket_no, flight_id),
    FOREIGN KEY (ticket_no, flight_id) REFERENCES ticket_flights(ticket_no, flight_id)
);

-- ------------------------------------------------------------
-- Customer experience table (drives the "complaints" KPI)
-- ------------------------------------------------------------

CREATE TABLE complaints (
    complaint_id      SERIAL PRIMARY KEY,
    ticket_no         CHAR(10) NOT NULL REFERENCES tickets(ticket_no),
    flight_id         INT REFERENCES flights(flight_id),
    complaint_date    TIMESTAMP NOT NULL,
    complaint_type    VARCHAR(30) NOT NULL CHECK (complaint_type IN
                        ('Flight Delay','Cancellation','Baggage','Booking Error',
                         'Customer Service','Overbooking','Refund Issue')),
    resolved          BOOLEAN NOT NULL DEFAULT FALSE,
    resolution_days   INT
);

-- ------------------------------------------------------------
-- Indexes to support the analytical queries in step 4
-- ------------------------------------------------------------

CREATE INDEX idx_flights_route ON flights(departure_airport, arrival_airport);
CREATE INDEX idx_flights_departure ON flights(scheduled_departure);
CREATE INDEX idx_ticket_flights_flight ON ticket_flights(flight_id);
CREATE INDEX idx_bookings_date ON bookings(book_date);
CREATE INDEX idx_complaints_date ON complaints(complaint_date);

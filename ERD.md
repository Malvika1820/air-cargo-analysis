# Entity-Relationship Diagram

```mermaid
erDiagram
    airports_data ||--o{ flights : "departure/arrival"
    aircrafts_data ||--o{ flights : "operates"
    aircrafts_data ||--o{ seats : "has"
    bookings ||--o{ tickets : "contains"
    tickets ||--o{ ticket_flights : "covers"
    flights ||--o{ ticket_flights : "sold on"
    ticket_flights ||--|| boarding_passes : "issues"
    tickets ||--o{ complaints : "may raise"
    flights ||--o{ complaints : "relates to"

    airports_data {
        char3 airport_code PK
        varchar airport_name
        varchar city
        varchar country
    }
    aircrafts_data {
        char3 aircraft_code PK
        varchar model
        int total_seats
    }
    flights {
        int flight_id PK
        varchar flight_no
        timestamp scheduled_departure
        timestamp scheduled_arrival
        char3 departure_airport FK
        char3 arrival_airport FK
        char3 aircraft_code FK
        varchar status
        numeric base_fare_economy
    }
    bookings {
        char6 book_ref PK
        timestamp book_date
        numeric total_amount
        varchar channel
    }
    tickets {
        char10 ticket_no PK
        char6 book_ref FK
        varchar passenger_id
        varchar passenger_name
    }
    ticket_flights {
        char10 ticket_no PK,FK
        int flight_id PK,FK
        varchar fare_conditions
        numeric amount
    }
    boarding_passes {
        char10 ticket_no PK,FK
        int flight_id PK,FK
        varchar seat_no
    }
    complaints {
        int complaint_id PK
        char10 ticket_no FK
        int flight_id FK
        varchar complaint_type
        boolean resolved
    }
```

**Design notes**

- `bookings` → `tickets` → `ticket_flights` mirrors real airline reservation systems (a booking can hold multiple passengers, each ticket can span multiple flight legs).
- `ticket_flights.amount` is the actual revenue line — this is what ticket-sales and revenue queries aggregate.
- `complaints` is linked to both `tickets` and `flights` so complaint rates can be sliced by route, aircraft, or booking channel — needed to support the "reduction in customer complaints" analysis.

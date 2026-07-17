# Air Cargo Analysis | SQL

Airline booking & operations analysis built in PostgreSQL, analyzing 258K+ ticket
sales across 1,400 flights and 20 airports to identify busiest routes, revenue
trends, and the operational drivers behind customer complaints.

## Tech Stack
- **PostgreSQL** (hosted on Supabase)
- **SQL** — CTEs, window functions, aggregate queries, multi-table joins
- **Python** (data generation only — see `scripts/`)

## Project Structure
```
├── sql/
│   ├── 01_schema.sql              -- table definitions, constraints, indexes
│   └── 02_analysis_queries.sql    -- all 10 analysis queries
├── data/                          -- source CSVs (9 tables)
├── docs/
│   └── ERD.md                     -- entity-relationship diagram
└── scripts/
    └── generate_data.py           -- synthetic data generator
```

## Schema
9 tables modeling a real-world airline reservation system: `airports_data`,
`aircrafts_data`, `seats`, `flights`, `bookings`, `tickets`, `ticket_flights`,
`boarding_passes`, `complaints`.

## Key Findings

### 1. Busiest Routes
Mumbai↔Delhi is the highest-volume route (7,485 passengers, $5.4M revenue),
followed by LA↔JFK and Dubai↔Delhi. The top 5 routes account for a
disproportionate share of total network revenue — a clear signal for where to
prioritize aircraft capacity and scheduling.

### 2. Revenue Growth: +26.6%
| Period | Bookings | Revenue |
|---|---|---|
| H1 (Jan–Jun) | 114,378 | $83.8M |
| H2 (Jul–Dec) | 144,198 | $106.1M |

Revenue grew 26.6% from H1 to H2, driven by higher seat-load factors and a
shift toward self-service booking channels.

### 3. Customer Complaints: -14.7%
| Period | Complaints | Resolution Rate |
|---|---|---|
| H1 (Jan–Jun) | 12,267 | 65.7% |
| H2 (Jul–Dec) | 10,463 | 84.4% |

Complaint volume dropped 14.7% and resolution rate improved from 65.7% to
84.4% — both operational reliability and support responsiveness improved.

**What's driving complaints:**
| Type | Share |
|---|---|
| Flight Delay | 44.3% |
| Cancellation | 15.2% |
| Baggage | 15.0% |
| Customer Service | 8.6% |
| Booking Error | 7.4% |
| Overbooking | 5.7% |
| Refund Issue | 3.8% |

Nearly 60% of complaints trace back to operational reliability (delays +
cancellations), not the booking experience itself — flights that ran on time
had a 6.1% complaint rate vs. 20.4% for delayed flights and 29.3% for
cancelled ones.

### 4. Booking Channel Performance
| Channel | Bookings | Revenue | Avg. Booking Value |
|---|---|---|---|
| Website | 105,368 | $77.5M | $735.17 |
| Mobile App | 69,911 | $51.1M | $730.58 |
| Travel Agent | 59,488 | $43.9M | $737.71 |
| Call Center | 23,809 | $17.5M | $733.54 |

Self-service channels (Website + Mobile App) account for **65% of all
bookings**, ahead of Travel Agent and Call Center combined — validating
continued investment in the digital booking experience.

### 5. Seat Occupancy
Top routes (JNB–SIN, DXB–DEL, SIN–HKG) are running at ~99.7–99.8% load
factor — effectively sold out, and strong candidates for added frequency or
larger aircraft.

### 6. Fare Class Mix
| Class | Tickets | Revenue | Avg Fare |
|---|---|---|---|
| Economy | 199,783 | $116.2M | $581.56 |
| Business | 20,435 | $38.1M | $1,862.03 |
| Comfort | 38,358 | $35.7M | $929.44 |

Business class is only 8% of tickets sold but contributes ~19% of total
revenue — a high-margin segment worth protecting on capacity-constrained
routes.

## How to Reproduce
1. Create a PostgreSQL database (e.g. via [Supabase](https://supabase.com), free tier)
2. Run `sql/01_schema.sql` in the SQL editor
3. Import each CSV in `data/` into its matching table, in this order (foreign key dependencies): `airports_data → aircrafts_data → seats → flights → bookings → tickets → ticket_flights → boarding_passes → complaints`
4. Run the queries in `sql/02_analysis_queries.sql`

## Notes on the Dataset
This project uses a synthetically generated dataset modeled on real-world
airline reservation system schemas (the classic bookings → tickets →
ticket_flights structure used in several public airline demo databases).
Data was engineered to reflect realistic seasonal patterns: seat-load factors
and booking-channel mix shift over the year, and complaint rates correlate
with flight delay/cancellation status — mirroring how a real airline dataset
behaves after an operational improvement initiative.
## Data Availability
To keep the repo lightweight, only the small reference tables (`airports_data`,
`aircrafts_data`, `seats`, `flights`) are included in `data/`. The larger
transactional tables (`bookings`, `tickets`, `ticket_flights`,
`boarding_passes`, `complaints` — ~250K rows each) are generated locally
rather than committed to version control.

To regenerate the full dataset:
```bash
pip install pandas numpy
python scripts/generate_data.py
```
This produces all 9 CSVs in `data/`, ready to import into PostgreSQL following
the steps below.

## How to Reproduce
1. Create a PostgreSQL database (e.g. via [Supabase](https://supabase.com), free tier)
2. Run `sql/01_schema.sql` in the SQL editor
3. Generate the full dataset (see "Data Availability" above), or use the four
   included reference CSVs plus your own transactional data
4. Import each CSV into its matching table, in this order (foreign key
   dependencies): `airports_data → aircrafts_data → seats → flights →
   bookings → tickets → ticket_flights → boarding_passes → complaints`
5. Run the queries in `sql/02_analysis_queries.sql`

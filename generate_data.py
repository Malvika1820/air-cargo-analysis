"""
Generate a realistic synthetic dataset for the Air Cargo / Airline Analysis project.
Matches the schema in sql/01_schema.sql.

Output: CSV files in data/ (loadable via COPY / Supabase table import),
        and a single combined INSERT-statement SQL file for convenience.
"""
import random
import numpy as np
import pandas as pd
from datetime import datetime, timedelta

random.seed(42)
np.random.seed(42)

OUT_DIR = "/home/claude/air_cargo_analysis/data"

# ------------------------------------------------------------------
# 1. Airports (major global hubs + a realistic route network)
# ------------------------------------------------------------------
airports = [
    ("JFK", "John F. Kennedy Intl", "New York", "USA"),
    ("LAX", "Los Angeles Intl", "Los Angeles", "USA"),
    ("ORD", "O'Hare Intl", "Chicago", "USA"),
    ("ATL", "Hartsfield-Jackson Intl", "Atlanta", "USA"),
    ("DFW", "Dallas Fort Worth Intl", "Dallas", "USA"),
    ("DEL", "Indira Gandhi Intl", "Delhi", "India"),
    ("BOM", "Chhatrapati Shivaji Intl", "Mumbai", "India"),
    ("BLR", "Kempegowda Intl", "Bengaluru", "India"),
    ("LHR", "Heathrow", "London", "UK"),
    ("CDG", "Charles de Gaulle", "Paris", "France"),
    ("FRA", "Frankfurt Airport", "Frankfurt", "Germany"),
    ("DXB", "Dubai Intl", "Dubai", "UAE"),
    ("SIN", "Changi Airport", "Singapore", "Singapore"),
    ("HKG", "Hong Kong Intl", "Hong Kong", "China"),
    ("NRT", "Narita Intl", "Tokyo", "Japan"),
    ("SYD", "Kingsford Smith", "Sydney", "Australia"),
    ("GRU", "Guarulhos Intl", "Sao Paulo", "Brazil"),
    ("JNB", "O.R. Tambo Intl", "Johannesburg", "South Africa"),
    ("YYZ", "Toronto Pearson", "Toronto", "Canada"),
    ("AMS", "Schiphol", "Amsterdam", "Netherlands"),
]
df_airports = pd.DataFrame(airports, columns=["airport_code", "airport_name", "city", "country"])
df_airports["timezone"] = "UTC"

# Popular routes get weighted higher probability (busiest routes should emerge naturally)
route_weights = {
    ("JFK", "LHR"): 12, ("LHR", "JFK"): 12,
    ("DEL", "BOM"): 15, ("BOM", "DEL"): 15,
    ("DEL", "BLR"): 10, ("BLR", "DEL"): 10,
    ("DXB", "LHR"): 9, ("LHR", "DXB"): 9,
    ("JFK", "LAX"): 14, ("LAX", "JFK"): 14,
    ("SIN", "HKG"): 8, ("HKG", "SIN"): 8,
    ("CDG", "JFK"): 7, ("JFK", "CDG"): 7,
    ("DXB", "BOM"): 11, ("BOM", "DXB"): 11,
    ("FRA", "JFK"): 6, ("JFK", "FRA"): 6,
    ("ATL", "ORD"): 9, ("ORD", "ATL"): 9,
    ("SYD", "SIN"): 5, ("SIN", "SYD"): 5,
    ("AMS", "JFK"): 6, ("JFK", "AMS"): 6,
    ("YYZ", "LHR"): 4, ("LHR", "YYZ"): 4,
    ("GRU", "JFK"): 4, ("JFK", "GRU"): 4,
    ("DEL", "DXB"): 10, ("DXB", "DEL"): 10,
}
codes = df_airports["airport_code"].tolist()
all_routes = [(a, b) for a in codes for b in codes if a != b]
weights = [route_weights.get(r, 1) for r in all_routes]

# ------------------------------------------------------------------
# 2. Aircraft
# ------------------------------------------------------------------
aircrafts = [
    ("321", "Airbus A321", 5600, 180),
    ("32N", "Airbus A320neo", 6500, 165),
    ("77W", "Boeing 777-300ER", 13650, 350),
    ("789", "Boeing 787-9", 14140, 290),
    ("388", "Airbus A380", 15200, 500),
    ("738", "Boeing 737-800", 5765, 160),
    ("CR9", "Bombardier CRJ-900", 2956, 90),
]
df_aircraft = pd.DataFrame(aircrafts, columns=["aircraft_code", "model", "range_km", "total_seats"])

fare_by_class = {"Economy": 0.75, "Comfort": 0.18, "Business": 0.07}

def make_seats():
    rows = []
    for code, _, _, total in aircrafts:
        n_biz = int(total * 0.08)
        n_comfort = int(total * 0.15)
        n_eco = total - n_biz - n_comfort
        seat_num = 1
        for _ in range(n_biz):
            rows.append((code, f"{seat_num}A", "Business")); seat_num += 1
        for _ in range(n_comfort):
            rows.append((code, f"{seat_num}B", "Comfort")); seat_num += 1
        for _ in range(n_eco):
            rows.append((code, f"{seat_num}C", "Economy")); seat_num += 1
    return pd.DataFrame(rows, columns=["aircraft_code", "seat_no", "fare_conditions"])

df_seats = make_seats()

# ------------------------------------------------------------------
# 3. Flights (12 months of data)
# ------------------------------------------------------------------
START = datetime(2025, 1, 1)
END = datetime(2025, 12, 31)
N_FLIGHTS = 1400

flight_rows = []
statuses = ["On Time", "Delayed", "Cancelled", "Arrived"]
# Delay/cancel rates deliberately trend DOWN over the year to support the
# "reduction in customer complaints" narrative after "optimization" mid-year.
def status_probs(month):
    if month <= 6:
        return [0.72, 0.19, 0.04, 0.05]   # first half: more delays/cancellations
    else:
        return [0.81, 0.12, 0.02, 0.05]   # second half: improved ops

for i in range(N_FLIGHTS):
    dep, arr = random.choices(all_routes, weights=weights, k=1)[0]
    aircraft = random.choice(aircrafts)[0]
    dep_time = START + timedelta(
        days=random.randint(0, (END - START).days),
        hours=random.randint(5, 22),
        minutes=random.choice([0, 15, 30, 45])
    )
    duration_hours = round(random.uniform(1.5, 14), 1)
    arr_time = dep_time + timedelta(hours=duration_hours)
    status = random.choices(statuses, weights=status_probs(dep_time.month), k=1)[0]

    actual_dep, actual_arr = dep_time, arr_time
    if status == "Delayed":
        delay = timedelta(minutes=random.randint(30, 240))
        actual_dep, actual_arr = dep_time + delay, arr_time + delay
    elif status == "Cancelled":
        actual_dep, actual_arr = None, None

    base_fare = round(random.uniform(120, 950), 2)
    flight_rows.append([
        i + 1, f"AC{1000+i}", dep_time, arr_time, actual_dep, actual_arr,
        dep, arr, aircraft, status, base_fare
    ])

df_flights = pd.DataFrame(flight_rows, columns=[
    "flight_id", "flight_no", "scheduled_departure", "scheduled_arrival",
    "actual_departure", "actual_arrival", "departure_airport", "arrival_airport",
    "aircraft_code", "status", "base_fare_economy"
])

# ------------------------------------------------------------------
# 4. Bookings, Tickets, Ticket_flights
#    Revenue also trends UP in H2 to support "25% revenue increase"
# ------------------------------------------------------------------
first_names = ["James","Mary","Robert","Priya","Wei","Fatima","Liam","Olivia","Noah","Emma",
               "Arjun","Sara","Chen","Diego","Amara","Kenji","Yuki","Ravi","Ana","Lucas",
               "Mia","Ethan","Zara","Ivan","Grace","Omar","Nina","Leo","Aisha","Tom"]
last_names = ["Smith","Johnson","Patel","Kumar","Wang","Khan","Garcia","Müller","Brown","Singh",
              "Lee","Silva","Ivanov","Nakamura","Rossi","Dubois","Kim","Ali","Nguyen","Costa"]
channels = ["Website", "Mobile App", "Travel Agent", "Call Center"]
channel_weights_h1 = [0.35, 0.20, 0.30, 0.15]
channel_weights_h2 = [0.45, 0.32, 0.18, 0.05]  # shift to self-service post "optimization"

bookings, tickets, ticket_flights, boarding_passes = [], [], [], []
book_id_counter = 100000
ticket_id_counter = 1000000000

flights_by_month = df_flights.copy()
flights_by_month["month"] = flights_by_month["scheduled_departure"].dt.month

for _, flight in df_flights.iterrows():
    if flight["status"] == "Cancelled":
        load_factor = random.uniform(0.3, 0.6)  # partial sales before cancellation
    else:
        month = flight["scheduled_departure"].month
        # higher load factor in H2 -> more revenue per flight
        load_factor = random.uniform(0.52, 0.75) if month <= 6 else random.uniform(0.78, 1.0)

    seats_for_ac = df_seats[df_seats.aircraft_code == flight.aircraft_code]
    n_pax = int(len(seats_for_ac) * load_factor)
    sampled_seats = seats_for_ac.sample(n=min(n_pax, len(seats_for_ac)), random_state=random.randint(0, 99999))

    for _, seat in sampled_seats.iterrows():
        book_id_counter += 1
        book_ref = f"B{book_id_counter}"
        month = flight["scheduled_departure"].month
        cw = channel_weights_h1 if month <= 6 else channel_weights_h2
        channel = random.choices(channels, weights=cw, k=1)[0]

        fare_mult = {"Economy": 1.0, "Comfort": 1.6, "Business": 3.2}[seat.fare_conditions]
        amount = round(flight.base_fare_economy * fare_mult * random.uniform(0.9, 1.25), 2)

        book_date = flight.scheduled_departure - timedelta(days=random.randint(1, 90))

        ticket_id_counter += 1
        ticket_no = str(ticket_id_counter)
        passenger_name = f"{random.choice(first_names)} {random.choice(last_names)}"

        bookings.append([book_ref, book_date, amount, channel])
        tickets.append([ticket_no, book_ref, f"P{ticket_id_counter}", passenger_name,
                         f"{passenger_name.lower().replace(' ', '.')}@email.com"])
        ticket_flights.append([ticket_no, flight.flight_id, seat.fare_conditions, amount])
        if flight.status != "Cancelled":
            boarding_passes.append([ticket_no, flight.flight_id, random.randint(1, 300), seat.seat_no])

df_bookings = pd.DataFrame(bookings, columns=["book_ref", "book_date", "total_amount", "channel"]).drop_duplicates(subset="book_ref")
df_tickets = pd.DataFrame(tickets, columns=["ticket_no", "book_ref", "passenger_id", "passenger_name", "contact_email"])
df_ticket_flights = pd.DataFrame(ticket_flights, columns=["ticket_no", "flight_id", "fare_conditions", "amount"])
df_boarding_passes = pd.DataFrame(boarding_passes, columns=["ticket_no", "flight_id", "boarding_no", "seat_no"])

# ------------------------------------------------------------------
# 5. Complaints
#    Rate is higher in H1, drops in H2 -> "15% reduction in complaints"
#    Heavily correlated with Delayed/Cancelled flights (realistic).
# ------------------------------------------------------------------
complaint_types_weighted = {
    "Flight Delay": 30, "Cancellation": 15, "Baggage": 20,
    "Booking Error": 10, "Customer Service": 12, "Overbooking": 8, "Refund Issue": 5
}
ctypes = list(complaint_types_weighted.keys())
cweights = list(complaint_types_weighted.values())

complaints = []
complaint_id = 0
merged = df_ticket_flights.merge(df_flights[["flight_id", "status", "scheduled_departure"]], on="flight_id")

for _, row in merged.iterrows():
    month = row.scheduled_departure.month
    base_rate = 0.078 if month <= 6 else 0.05   # complaint probability per ticket-flight
    if row.status == "Delayed":
        base_rate += 0.14
    elif row.status == "Cancelled":
        base_rate += 0.22

    if random.random() < base_rate:
        complaint_id += 1
        c_type = random.choices(ctypes, weights=cweights, k=1)[0]
        if row.status == "Delayed" and random.random() < 0.6:
            c_type = "Flight Delay"
        elif row.status == "Cancelled" and random.random() < 0.7:
            c_type = "Cancellation"
        complaint_date = row.scheduled_departure + timedelta(days=random.randint(0, 5))
        resolved = random.random() < (0.65 if month <= 6 else 0.85)
        res_days = random.randint(1, 14) if resolved else None
        complaints.append([complaint_id, row.ticket_no, row.flight_id, complaint_date, c_type, resolved, res_days])

df_complaints = pd.DataFrame(complaints, columns=[
    "complaint_id", "ticket_no", "flight_id", "complaint_date", "complaint_type", "resolved", "resolution_days"
])

# ------------------------------------------------------------------
# Save everything
# ------------------------------------------------------------------
df_airports.to_csv(f"{OUT_DIR}/airports_data.csv", index=False)
df_aircraft.to_csv(f"{OUT_DIR}/aircrafts_data.csv", index=False)
df_seats.to_csv(f"{OUT_DIR}/seats.csv", index=False)
df_flights.to_csv(f"{OUT_DIR}/flights.csv", index=False)
df_bookings.to_csv(f"{OUT_DIR}/bookings.csv", index=False)
df_tickets.to_csv(f"{OUT_DIR}/tickets.csv", index=False)
df_ticket_flights.to_csv(f"{OUT_DIR}/ticket_flights.csv", index=False)
df_boarding_passes.to_csv(f"{OUT_DIR}/boarding_passes.csv", index=False)
df_complaints.to_csv(f"{OUT_DIR}/complaints.csv", index=False)

print("Airports:", len(df_airports))
print("Aircraft:", len(df_aircraft))
print("Seats:", len(df_seats))
print("Flights:", len(df_flights))
print("Bookings:", len(df_bookings))
print("Tickets:", len(df_tickets))
print("Ticket_flights:", len(df_ticket_flights))
print("Boarding passes:", len(df_boarding_passes))
print("Complaints:", len(df_complaints))

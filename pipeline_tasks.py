import os
import io
import time
import datetime
import numpy as np
import pandas as pd
import requests
from supabase import create_client, Client

# ====================================================================
# CONFIGURATION & CREDENTIALS
SUPABASE_URL = os.getenv("SUPABASE_URL", "https://dajourmarbthhfmkkjqs.supabase.co")
SUPABASE_KEY = os.getenv("SUPABASE_KEY", "your_supabase_service_role_key")
OPENWEATHER_API_KEY = os.getenv("OPENWEATHER_API_KEY", "your_openweather_api_key")

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

headers = {
    "apikey": SUPABASE_KEY,
    "Authorization": f"Bearer {SUPABASE_KEY}",
    "Content-Type": "application/json",
    "Prefer": "return=representation"
}

# ====================================================================
# HELPER: CHECK DATABASE TABLE STATUS
# ====================================================================
def check_table_exists(table_name: str) -> bool:
    """Check if a table exists and is accessible via PostgREST."""
    try:
        url = f"{SUPABASE_URL}/rest/v1/{table_name}?select=*&limit=1"
        res = requests.get(url, headers=headers)
        return res.status_code in [200, 206]
    except Exception as e:
        print(f"[ERROR] Exception checking table '{table_name}': {e}")
        return False

def verify_all_tables() -> bool:
    """Verify that all three required tables are present."""
    tables = ["weather_logs", "train_schedules", "passenger_density_logs"]
    missing = [t for t in tables if not check_table_exists(t)]
    if missing:
        print(f"[STATUS] Waiting for tables to be created in Supabase: {missing}")
        return False
    print("[SUCCESS] All 3 tables (weather_logs, train_schedules, passenger_density_logs) are verified in Supabase!")
    return True


# ====================================================================
# TASK 2: TRAIN SCHEDULE MOCK DATA (MASTER DATA)
# ====================================================================
def generate_and_insert_train_schedules():
    """
    Generate 1-day train schedule dataset:
    - Peak hours (07:00-09:00 and 16:00-18:00): 1 train every 30 minutes.
    - Off-peak hours (05:00-07:00, 09:00-16:00, 18:00-23:00): 1 train every 60 minutes.
    - max_capacity: 1000 passengers per train.
    """
    print("\n=======================================================")
    print("TASK 2: GENERATING TRAIN SCHEDULE MASTER DATA")
    print("=======================================================")
    
    schedule_records = []
    
    # Generate schedule from 05:00 to 23:00
    # Peak 1: 07:00 - 09:00 (every 30m) -> 07:00, 07:30, 08:00, 08:30, 09:00
    # Peak 2: 16:00 - 18:00 (every 30m) -> 16:00, 16:30, 17:00, 17:30, 18:00
    # Off-peak: every 60m
    
    current_time = datetime.datetime.strptime("05:00:00", "%H:%M:%S")
    end_time = datetime.datetime.strptime("23:00:00", "%H:%M:%S")
    
    while current_time <= end_time:
        hour = current_time.hour
        minute = current_time.minute
        
        dep_str = current_time.strftime("%H:%M:%S")
        # Train arrives 10 minutes prior to departure
        arr_dt = current_time - datetime.timedelta(minutes=10)
        arr_str = arr_dt.strftime("%H:%M:%S")
        
        train_id = f"TR_{current_time.strftime('%H%M')}"
        
        schedule_records.append({
            "train_id": train_id,
            "arrival_time": arr_str,
            "departure_time": dep_str,
            "max_capacity": 1000
        })
        
        # Check if next interval is in peak period
        is_peak = (7 <= hour < 9) or (16 <= hour < 18)
        step_minutes = 30 if is_peak else 60
        current_time += datetime.timedelta(minutes=step_minutes)

    # Convert to DataFrame and simulate in-memory CSV
    df_schedules = pd.DataFrame(schedule_records)
    csv_buffer = io.StringIO()
    df_schedules.to_csv(csv_buffer, index=False)
    csv_buffer.seek(0)
    
    print(f"[INFO] Generated {len(df_schedules)} train schedules for 1 operational day:")
    print(df_schedules.to_string(index=False))
    
    # Insert / Upsert into Supabase train_schedules
    print("[INFO] Inserting train schedules into Supabase 'train_schedules' table...")
    try:
        # Upsert records using Supabase Python Client
        response = supabase.table("train_schedules").upsert(schedule_records).execute()
        print(f"[SUCCESS] Successfully inserted/updated {len(schedule_records)} rows into 'train_schedules'.")
        return df_schedules
    except Exception as e:
        print(f"[ERROR] Failed to insert via supabase-py, attempting direct REST POST: {e}")
        url = f"{SUPABASE_URL}/rest/v1/train_schedules"
        res = requests.post(url, headers=headers, json=schedule_records)
        if res.status_code in [200, 201]:
            print(f"[SUCCESS] REST API inserted {len(schedule_records)} rows into 'train_schedules'.")
            return df_schedules
        else:
            print(f"[ERROR] REST API response ({res.status_code}): {res.text}")
            raise


# ====================================================================
# TASK 3: SYNTHETIC PASSENGER DATA GENERATION (PYTHON)
# ====================================================================
def generate_and_insert_passenger_density():
    """
    Step 3.1: Query train_schedules from Supabase.
    Step 3.2: For each departure_time and 1000 passengers, generate arrival times with normal distribution (mean = departure - 35 mins).
    Step 3.3: Group into 5-minute intervals.
    Step 3.4: Apply uniform random noise to passenger counts.
    Step 3.5: Push final time-series dataset to passenger_density_logs in Supabase.
    """
    print("\n=======================================================")
    print("TASK 3: SYNTHETIC PASSENGER DATA GENERATION")
    print("=======================================================")
    
    # Step 3.1: Query train_schedules
    print("[STEP 3.1] Querying train_schedules from Supabase...")
    res = supabase.table("train_schedules").select("train_id, departure_time, max_capacity").order("departure_time").execute()
    trains = res.data
    
    if not trains:
        print("[WARNING] No train schedules found in Supabase. Running Task 2 first...")
        df_sched = generate_and_insert_train_schedules()
        trains = df_sched.to_dict(orient="records")

    print(f"[INFO] Retrieved {len(trains)} trains for simulation.")
    
    base_date = datetime.date.today()
    all_density_records = []
    
    # Steps 3.2, 3.3, 3.4: Generate passenger arrivals per train
    np.random.seed(42) # For reproducible baseline with realistic randomness
    
    for train in trains:
        t_id = train["train_id"]
        dep_time_str = train["departure_time"]
        max_cap = train.get("max_capacity", 1000)
        
        # Parse departure time to full datetime on base_date
        t_dep = datetime.datetime.combine(base_date, datetime.datetime.strptime(dep_time_str, "%H:%M:%S").time())
        
        # Step 3.2: Mean arrival time = exactly 35 minutes before departure
        mu_dt = t_dep - datetime.timedelta(minutes=35)
        # Standard deviation in minutes (e.g. 10 minutes spread)
        sigma_minutes = 10.0
        
        # Generate 1000 passenger arrival offsets in minutes from departure
        # Offsets are negative (before departure): mean = -35.0
        arrival_offsets = np.random.normal(loc=-35.0, scale=sigma_minutes, size=max_cap)
        
        # Convert offsets to actual arrival datetimes
        arrival_datetimes = [t_dep + datetime.timedelta(minutes=float(offset)) for offset in arrival_offsets]
        
        # Step 3.3: Group arrival times into 5-minute intervals
        df_passengers = pd.DataFrame({"arrival_time": arrival_datetimes})
        # Floor timestamps to 5-minute bins
        df_passengers["interval_bin"] = df_passengers["arrival_time"].dt.floor("5min")
        
        # Aggregate passenger count per 5-minute interval
        agg = df_passengers.groupby("interval_bin").size().reset_index(name="raw_count")
        
        # Step 3.4: Apply uniform random noise to passenger counts
        # Add realistic noise: uniform between -10% and +10% of bin count, minimum 1 passenger
        noise_factor = np.random.uniform(-0.10, 0.10, size=len(agg))
        agg["passenger_count"] = np.maximum(1, np.round(agg["raw_count"] * (1 + noise_factor))).astype(int)
        
        for _, row in agg.iterrows():
            all_density_records.append({
                "timestamp": row["interval_bin"].isoformat(),
                "train_id": t_id,
                "passenger_count": int(row["passenger_count"])
            })

    print(f"\n[INFO] Generated {len(all_density_records)} 5-minute time-series aggregated density points.")
    df_density = pd.DataFrame(all_density_records)
    print("\n--- SAMPLE GENERATED PASSENGER DENSITY DATA (FIRST 10 ROWS) ---")
    print(df_density.head(10).to_string(index=False))
    
    # Step 3.5: Push time-series dataset to passenger_density_logs in Supabase
    print("\n[STEP 3.5] Pushing time-series dataset to Supabase 'passenger_density_logs' table in batches...")
    
    batch_size = 100
    total_inserted = 0
    
    for i in range(0, len(all_density_records), batch_size):
        batch = all_density_records[i:i + batch_size]
        try:
            supabase.table("passenger_density_logs").insert(batch).execute()
            total_inserted += len(batch)
            print(f"[INFO] Inserted batch {i // batch_size + 1}/{(len(all_density_records) + batch_size - 1) // batch_size} ({total_inserted}/{len(all_density_records)} rows)")
        except Exception as e:
            print(f"[ERROR] Batch insertion error: {e}. Retrying via REST API...")
            url = f"{SUPABASE_URL}/rest/v1/passenger_density_logs"
            res = requests.post(url, headers=headers, json=batch)
            if res.status_code in [200, 201]:
                total_inserted += len(batch)
                print(f"[INFO] REST fallback successfully inserted batch ({total_inserted}/{len(all_density_records)} rows)")
            else:
                print(f"[FATAL] Failed to insert batch: {res.status_code} - {res.text}")
                raise
                
    print(f"\n[SUCCESS] Successfully pushed all {total_inserted} passenger density records to 'passenger_density_logs'!")
    return df_density


# ====================================================================
# TEST WEATHER PIPELINE INSERTION DIRECTLY
# ====================================================================
def test_weather_pipeline_live():
    """Fetch live weather from OpenWeatherMap for Hanoi and insert into weather_logs to verify end-to-end flow."""
    print("\n=======================================================")
    print("TASK 1 VERIFICATION: LIVE OPENWEATHER -> SUPABASE TEST")
    print("=======================================================")
    
    url = f"https://api.openweathermap.org/data/2.5/weather?q=Hanoi&appid={OPENWEATHER_API_KEY}&units=metric"
    res = requests.get(url)
    if res.status_code != 200:
        print(f"[ERROR] OpenWeatherMap API request failed: {res.status_code} - {res.text}")
        return
    
    data = res.json()
    temp = float(data["main"]["temp"])
    humidity = float(data["main"]["humidity"])
    
    print(f"[INFO] Hanoi Weather Fetched: Temp = {temp}°C, Humidity = {humidity}%")
    
    log_entry = {
        "temp": temp,
        "humidity": humidity
    }
    
    try:
        supabase.table("weather_logs").insert(log_entry).execute()
        print(f"[SUCCESS] Successfully inserted test record into 'weather_logs': {log_entry}")
    except Exception as e:
        print(f"[ERROR] weather_logs insertion: {e}")


if __name__ == "__main__":
    print("[INITIALIZATION] Checking Supabase database tables...")
    if verify_all_tables():
        generate_and_insert_train_schedules()
        generate_and_insert_passenger_density()
        test_weather_pipeline_live()
    else:
        print("\n[ACTION REQUIRED] Please execute the SQL schema in your Supabase SQL Editor.")
        print("Schema is saved in 'schema.sql'.")

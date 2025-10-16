import os
import json
import psycopg2
from psycopg2 import sql
from datetime import datetime

# ==========================
# PostgreSQL Configuration
# ==========================
DB_CONFIG = {
    "dbname": "PhonePayDB",
    "user": "postgres",
    "password": "admin",
    "host": "localhost",
    "port": "5432"
}

def get_connection():
    return psycopg2.connect(**DB_CONFIG)

# ==========================
# Logging Setup
# ==========================
LOG_FOLDER = "logs"
os.makedirs(LOG_FOLDER, exist_ok=True)
LOG_FILE = os.path.join(LOG_FOLDER, f"pulse_loader_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log")

def log(message):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    msg = f"[{timestamp}] {message}"
    print(msg)
    with open(LOG_FILE, "a", encoding="utf-8") as f:
        f.write(msg + "\n")

# ==========================
# Table Setup
# ==========================
TABLES = {
    # --- Aggregated ---
    "aggregated_transaction": """
        CREATE TABLE aggregated_transaction(
            id SERIAL PRIMARY KEY,
            country VARCHAR(50),
            state VARCHAR(100),
            year INT,
            quarter INT,
            transaction_type VARCHAR(100),
            count BIGINT,
            amount DOUBLE PRECISION
        );
    """,
    "aggregated_insurance": """
        CREATE TABLE aggregated_insurance(
            id SERIAL PRIMARY KEY,
            country VARCHAR(50),
            state VARCHAR(100),
            year INT,
            quarter INT,
            insurance_type VARCHAR(100),
            count BIGINT,
            amount DOUBLE PRECISION
        );
    """,
    "aggregated_user": """
        CREATE TABLE aggregated_user(
            id SERIAL PRIMARY KEY,
            country VARCHAR(50),
            state VARCHAR(100),
            year INT,
            quarter INT,
            device_brand VARCHAR(100),
            user_count BIGINT,
            user_percentage DOUBLE PRECISION
        );
    """,

    # --- Map ---
    "map_transaction": """
        CREATE TABLE map_transaction(
            id SERIAL PRIMARY KEY,
            country VARCHAR(50),
            state VARCHAR(100),
            year INT,
            quarter INT,
            district VARCHAR(150),
            count BIGINT,
            amount DOUBLE PRECISION
        );
    """,
    "map_user": """
        CREATE TABLE map_user(
            id SERIAL PRIMARY KEY,
            country VARCHAR(50),
            state VARCHAR(100),
            year INT,
            quarter INT,
            district VARCHAR(150),
            registered_users BIGINT,
            app_opens BIGINT
        );
    """,

    # --- Top ---
    "top_transaction": """
        CREATE TABLE top_transaction(
            id SERIAL PRIMARY KEY,
            country VARCHAR(50),
            state VARCHAR(100),
            year INT,
            quarter INT,
            entity_name VARCHAR(150),
            entity_type VARCHAR(50),
            count BIGINT,
            amount DOUBLE PRECISION
        );
    """,
    "top_user": """
        CREATE TABLE top_user(
            id SERIAL PRIMARY KEY,
            country VARCHAR(50),
            state VARCHAR(100),
            year INT,
            quarter INT,
            entity_name VARCHAR(150),
            entity_type VARCHAR(50),
            registered_users BIGINT
        );
    """
}

def setup_tables():
    with get_connection() as conn:
        with conn.cursor() as cur:
            for table_name in TABLES:
                cur.execute(sql.SQL("DROP TABLE IF EXISTS {} CASCADE").format(sql.Identifier(table_name)))
                cur.execute(TABLES[table_name])
    log("✅ All tables dropped and created successfully.")

# ==========================
# Generic Insert
# ==========================
def insert_data(table, columns, values):
    with get_connection() as conn:
        with conn.cursor() as cur:
            query = sql.SQL("INSERT INTO {} ({}) VALUES ({})").format(
                sql.Identifier(table),
                sql.SQL(', ').join(map(sql.Identifier, columns)),
                sql.SQL(', ').join(sql.Placeholder() * len(columns))
            )
            cur.execute(query, values)
        conn.commit()

# ==========================
# Insert Functions with logging
# ==========================
def insert_aggregated_transaction(country, state, year, quarter, data, file_path=None):
    if not data or "transactionData" not in data:
        log(f"⚠️ Skipped aggregated_transaction: {file_path} → missing transactionData")
        return
    rows_inserted = 0
    for item in data["transactionData"]:
        t_type = item.get("name", "Unknown")
        for instr in item.get("paymentInstruments", []):
            insert_data(
                "aggregated_transaction",
                ["country","state","year","quarter","transaction_type","count","amount"],
                [country, state, year, quarter, t_type, instr.get("count", 0), instr.get("amount", 0.0)]
            )
            rows_inserted += 1
    log(f"✅ Inserted {rows_inserted} rows for aggregated_transaction: {file_path}")

def insert_aggregated_insurance(country, state, year, quarter, data, file_path=None):
    if not data or "transactionData" not in data:
        log(f"⚠️ Skipped aggregated_insurance: {file_path} → missing transactionData")
        return
    rows_inserted = 0
    for item in data["transactionData"]:
        ins_type = item.get("name", "Unknown")
        for instr in item.get("paymentInstruments", []):
            insert_data(
                "aggregated_insurance",
                ["country","state","year","quarter","insurance_type","count","amount"],
                [country, state, year, quarter, ins_type, instr.get("count", 0), instr.get("amount", 0.0)]
            )
            rows_inserted += 1
    log(f"✅ Inserted {rows_inserted} rows for aggregated_insurance: {file_path}")

def insert_aggregated_user(country, state, year, quarter, data, file_path=None):
    if not data:
        log(f"⚠️ Skipped aggregated_user: {file_path} → no data")
        return
    rows_inserted = 0
    if "usersByDevice" in data and data["usersByDevice"]:
        for device in data["usersByDevice"]:
            insert_data(
                "aggregated_user",
                ["country","state","year","quarter","device_brand","user_count","user_percentage"],
                [country, state, year, quarter, device.get("brand","Unknown"), device.get("count",0), device.get("percentage",0.0)]
            )
            rows_inserted += 1
    elif "totalUsers" in data:
        insert_data(
            "aggregated_user",
            ["country","state","year","quarter","device_brand","user_count","user_percentage"],
            [country, state, year, quarter, "All Devices", data["totalUsers"], 100.0]
        )
        rows_inserted = 1
    log(f"✅ Inserted {rows_inserted} rows for aggregated_user: {file_path}")

# ==========================
# MAP Insert Functions
# ==========================
def insert_map_transaction(country, state, year, quarter, data, file_path=None):
    if not data or "hoverDataList" not in data:
        log(f"⚠️ Skipped map_transaction: {file_path} → no hoverDataList")
        return
    rows_inserted = 0
    for district_data in data["hoverDataList"]:
        district = district_data.get("name", "Unknown")
        metrics = district_data.get("metric", [])
        if metrics:
            m = metrics[0]
            insert_data(
                "map_transaction",
                ["country","state","year","quarter","district","count","amount"],
                [country, state, year, quarter, district, m.get("count",0), m.get("amount",0.0)]
            )
            rows_inserted += 1
    log(f"✅ Inserted {rows_inserted} rows for map_transaction: {file_path}")

def insert_map_user(country, state, year, quarter, data, file_path=None):
    if not data or "hoverData" not in data:
        log(f"⚠️ Skipped map_user: {file_path} → no hoverData")
        return
    rows_inserted = 0
    for district, info in data["hoverData"].items():
        insert_data(
            "map_user",
            ["country","state","year","quarter","district","registered_users","app_opens"],
            [country, state, year, quarter, district, info.get("registeredUsers",0), info.get("appOpens",0)]
        )
        rows_inserted += 1
    log(f"✅ Inserted {rows_inserted} rows for map_user: {file_path}")

# ==========================
# TOP Insert Functions
# ==========================
def insert_top_transaction(country, state, year, quarter, data, file_path=None):
    if not data:
        log(f"⚠️ Skipped top_transaction: {file_path} → no data")
        return
    rows_inserted = 0
    for entity_type in ["districts","pincodes"]:
        for item in data.get(entity_type, []):
            entity_name = item.get("entityName","Unknown")
            metric = item.get("metric",{})
            insert_data(
                "top_transaction",
                ["country","state","year","quarter","entity_name","entity_type","count","amount"],
                [country, state, year, quarter, entity_name, entity_type, metric.get("count",0), metric.get("amount",0.0)]
            )
            rows_inserted += 1
    log(f"✅ Inserted {rows_inserted} rows for top_transaction: {file_path}")

def insert_top_user(country, state, year, quarter, data, file_path=None):
    if not data:
        log(f"⚠️ Skipped top_user: {file_path} → no data")
        return
    rows_inserted = 0
    for entity_type in ["districts","pincodes"]:
        for item in data.get(entity_type, []):
            entity_name = item.get("name","Unknown")
            registered_users = item.get("registeredUsers",0)
            insert_data(
                "top_user",
                ["country","state","year","quarter","entity_name","entity_type","registered_users"],
                [country, state, year, quarter, entity_name, entity_type, registered_users]
            )
            rows_inserted += 1
    log(f"✅ Inserted {rows_inserted} rows for top_user: {file_path}")

# ==========================
# Loader Helper
# ==========================
def process_json_files(path, func, country="India", state="All", quarter_default=0):
    if not os.path.exists(path):
        log(f"⚠️ Path does not exist: {path}")
        return
    for year_folder in os.listdir(path):
        year_path = os.path.join(path, year_folder)
        if not os.path.isdir(year_path):
            continue
        try:
            year = int(year_folder)
        except:
            year = 0
        for file in os.listdir(year_path):
            if not file.endswith(".json"):
                continue
            try:
                quarter = int(file.replace(".json",""))
            except:
                quarter = quarter_default
            file_path = os.path.join(year_path, file)
            try:
                with open(file_path,"r",encoding="utf-8") as f:
                    json_data = json.load(f).get("data")
            except Exception as e:
                log(f"❌ Failed to load {file_path}: {e}")
                continue
            func(country,state,year,quarter,json_data,file_path=file_path)

# ==========================
# Master Loader
# ==========================
def load_pulse_data(pulse_folder):
    base_agg = os.path.join(pulse_folder,"data","aggregated")
    base_map = os.path.join(pulse_folder,"data","map")
    base_top = os.path.join(pulse_folder,"data","top")
    country = "India"

    # Aggregated
    process_json_files(os.path.join(base_agg,"transaction","country","india"), insert_aggregated_transaction)
    trans_state_path = os.path.join(base_agg,"transaction","country","india","state")
    if os.path.exists(trans_state_path):
        for s in os.listdir(trans_state_path):
            process_json_files(os.path.join(trans_state_path,s), insert_aggregated_transaction,state=s)

    process_json_files(os.path.join(base_agg,"insurance","country","india"), insert_aggregated_insurance)
    ins_state_path = os.path.join(base_agg,"insurance","country","india","state")
    if os.path.exists(ins_state_path):
        for s in os.listdir(ins_state_path):
            process_json_files(os.path.join(ins_state_path,s), insert_aggregated_insurance,state=s)

    process_json_files(os.path.join(base_agg,"user","country","india"), insert_aggregated_user)
    user_state_path = os.path.join(base_agg,"user","country","india","state")
    if os.path.exists(user_state_path):
        for s in os.listdir(user_state_path):
            process_json_files(os.path.join(user_state_path,s), insert_aggregated_user,state=s)

    # Map
    process_json_files(os.path.join(base_map,"transaction","hover","country","india"), insert_map_transaction)
    map_trans_state_path = os.path.join(base_map,"transaction","hover","country","india","state")
    if os.path.exists(map_trans_state_path):
        for s in os.listdir(map_trans_state_path):
            process_json_files(os.path.join(map_trans_state_path,s), insert_map_transaction,state=s)

    process_json_files(os.path.join(base_map,"user","hover","country","india"), insert_map_user)
    map_user_state_path = os.path.join(base_map,"user","hover","country","india","state")
    if os.path.exists(map_user_state_path):
        for s in os.listdir(map_user_state_path):
            process_json_files(os.path.join(map_user_state_path,s), insert_map_user,state=s)

    # Top
    process_json_files(os.path.join(base_top,"transaction","country","india"), insert_top_transaction)
    top_trans_state_path = os.path.join(base_top,"transaction","country","india","state")
    if os.path.exists(top_trans_state_path):
        for s in os.listdir(top_trans_state_path):
            process_json_files(os.path.join(top_trans_state_path,s), insert_top_transaction,state=s)

    process_json_files(os.path.join(base_top,"user","country","india"), insert_top_user)
    top_user_state_path = os.path.join(base_top,"user","country","india","state")
    if os.path.exists(top_user_state_path):
        for s in os.listdir(top_user_state_path):
            process_json_files(os.path.join(top_user_state_path,s), insert_top_user,state=s)

    log("✅ All datasets (aggregated + map + top) loaded successfully.")

# ==========================
# Main
# ==========================
if __name__ == "__main__":
    PULSE_FOLDER = r"D:\Labmentix\Phone Pay\pulse"  # change this to your folder path
    setup_tables()
    load_pulse_data(PULSE_FOLDER)

import psycopg2
import time
from datetime import datetime, timezone

from app.db.schema_loader import load_schema
from app.graph.state import DataSageState
from app.cache.redis_cache import cache_key, get_cached_schema, set_cached_schema

from app.services.write_to_file import write_table_names
from app.core.settings import get_settings

settings = get_settings()



# def ts():
#     return datetime.now(timezone.utc).isoformat(timespec="milliseconds")


def schema_loader_node(state: DataSageState) -> DataSageState:
    """
    Load the database schema based on user query and db_id
    """

    print("schema_loader_node called")

    # start_total = time.perf_counter()
    # print(f"[{ts()}] 🔵 schema_loader_node START")

    if state is None:
        state = {}
    
    db_id = state["db_id"]

    schema_name = state["schema_name"]
    

    conn_str = state["db_conn_string"]
    

    if not db_id or not schema_name:
        return state

    key = cache_key(db_id, schema_name)

    # ── Cache check ─────────────────────────────
    # t0 = time.perf_counter()
    cached = get_cached_schema(key)
    # print(f"[{ts()}] ⏱ cache lookup: {(time.perf_counter() - t0):.3f}s")

    if cached:
        # print(f"[{ts()}] ✅ cache HIT")
        # print(f"[{ts()}] 🟢 schema_loader_node END "
        #       f"(total {(time.perf_counter() - start_total):.3f}s)")
        # print("Schema Loaded to DataSage state from cache")

        return {**state, "schema": cached}

    # print(f"[{ts()}] ❌ cache MISS")

    # ── Connection string ───────────────────────
    
    if not conn_str:
        raise ValueError(f"No connection string found for db_id: {db_id}")

    # ── DB connect ──────────────────────────────
    # t1 = time.perf_counter()
    conn = psycopg2.connect(conn_str)
    # print(f"[{ts()}] ⏱ db connect: {(time.perf_counter() - t1):.3f}s")

    # ── Schema load ─────────────────────────────
    try:
        # t2 = time.perf_counter()
        schema = load_schema(conn=conn, schema_name=state["schema_name"])
        write_table_names(schema=schema, output_file='schema.txt')
        # print(f"[{ts()}] ⏱ load_schema(): {(time.perf_counter() - t2):.3f}s")
    finally:
        conn.close()
        # print(f"[{ts()}] 🔌 db connection closed")

    # ── Cache write ─────────────────────────────
    # t3 = time.perf_counter()
    set_cached_schema(key, schema)
    # print(f"[{ts()}] ⏱ cache set: {(time.perf_counter() - t3):.3f}s")

    # print(f"[{ts()}] 🟢 schema_loader_node END "
    #       f"(total {(time.perf_counter() - start_total):.3f}s)")

    # print("Schema Loaded to DataSage state from database")

    

    return {
        **state,
        "schema": schema
    }

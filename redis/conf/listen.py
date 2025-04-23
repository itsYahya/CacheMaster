import psycopg2
import redis
import select
import json

# Connect to PostgreSQL
pg_conn = psycopg2.connect(
    dbname='mydb',
    user='admin',
    password='@dmin1234',
    host='postgres', 
    port=5432
)
pg_conn.set_isolation_level(psycopg2.extensions.ISOLATION_LEVEL_AUTOCOMMIT)
pg_cursor = pg_conn.cursor()

# Listen on the correct channel
pg_cursor.execute("LISTEN taux_change_channel;")

# Connect to Redis
redis_conn = redis.Redis(host='localhost', port=6379, decode_responses=True)

while True:
    if select.select([pg_conn], [], [], 5) == ([], [], []):
        continue

    pg_conn.poll()
    while pg_conn.notifies:
        notify = pg_conn.notifies.pop(0)
        data = json.loads(notify.payload)

        key = f"taux:{data['devise_source']}:{data['devise_cible']}:{data['date_taux']}"
        value = data['taux']
        
        redis_conn.set(key, value)
        #print(f"✅ Synced: {key} → {value}")

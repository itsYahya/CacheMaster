#! /usr/bin/env python

import psycopg2
import redis

# Connexion à PostgreSQL
pg_conn = psycopg2.connect(
    host="postgres",
    database="mydb",
    user="admin",
    password="@dmin1234"
)

# Connexion à Redis
redis_conn = redis.Redis(host="localhost", port=6379, db=0)

# Récupération des données de la table
cursor = pg_conn.cursor()
cursor.execute("SELECT devise_source, devise_cible, taux, date_taux FROM taux_de_change")
rows = cursor.fetchall()

# Insertion dans Redis
for source, cible, taux, date in rows:
    key = f"taux:{source}:{cible}"
    redis_conn.hset(key, mapping={
        "taux": str(taux),
        "date": date.strftime("%Y-%m-%d")
    })
    print(f"Insertion dans Redis : {key} → taux={taux}, date={date}")

# Fermeture des connexions
cursor.close()
pg_conn.close()



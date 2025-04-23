# The Cach Master

## Description
This project involves a PostgreSQL setup with a primary and replica instance, integrated with Redis for caching. A trigger in the primary database sends notifications to a Redis channel, which caches the relevant data upon receiving these notifications. Additionally, a Flask API is used to interact with both the database and Redis cache.

### primary node
   It gets lunched first of course, but there's some thing that we need to change:

         - pg_hba.conf           => this one to allow the replication from second postgres node
         - init-replication.sql  => this file to create the replicator role, which will be used by the second node
         - .env                  => this file holds the env variables

   *Triggers* won't be inserted automaticly, go ahead and add them when the primary node is up and running.

### replication node
   To run properly, you need to keep those points in mind:

         - /var/lib/postgresql/data => this file needs to be empty
         - /var/lib/postgresql/data => this file also needs to be owned by postgres user
         - /var/lib/postgresql/data => adjust the permision to 0700
         - pg_basebackup ...        => this is how postgres will be lunched (as a backup)

   Check docker-compose.yml file

### redis
   Nothing to be mentioned here, just for this script '/data/setup.sh' you need to run it manually :( 

## Technologies Used
- PostgreSQL
- Redis
- flask (Python)

------------------------------

## TESTS

### test replica
 psql -U admin -d mydb -c "SELECT * FROM test_replication;"
 psql -U admin -d mydb -c "INSERT INTO test_replication (message) VALUES ('MANUAL-insert to test replica')"

### test redis 
    time redis-cli HGETALL taux:YYY:ZZZ
    time psql -U admin -d mydb -c "SELECT devise_source, devise_cible, taux, date_taux FROM taux_de_change WHERE devise_source = 'USD' AND devise_cible = 'EUR';"

### test trigger
    INSERT INTO taux_de_change (devise_source, devise_cible, taux, date_taux)
    VALUES ('CHF', 'EUR', 1.0305, '2025-04-20');
    get taux:YYY:ZZZ:2025-04-20

    
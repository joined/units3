virtualenv --no-site-packages .env && source .env/bin/activate && pip install -r requirements.txt && mkdir db && sqlite3 db/database.db < schema.sql

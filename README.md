# tingr

python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

1. Create *'tingr'* database on system

sudo -u postgres psql -c "CREATE DATABASE tingr;"


2. Create *user credentials*

sudo -u postgres psql -c "CREATE USER username WITH PASSWORD 'yourpassword';"

3. *Set user privileges* on the tingr database

sudo -u postgres psql -c "GRANT ALL PRIVILEGES ON DATABASE tingr TO username;"

sudo -u postgres psql -d tingr -c "GRANT ALL ON SCHEMA public TO username;"


4. Update *database.py* with your credentials
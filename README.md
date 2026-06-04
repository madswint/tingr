# tingr

![Tingr screenshot](static/readme_ss.png)

## SETUP: (python3 or py)

### Python environment (if wanted)
```python3 -m venv .venv```

```source .venv/bin/activate```

```pip install -r requirements.txt```

### Database setup (linux)
These are the steps we use on our machines.

1. Create *'tingr'* database on system 

```sudo -u postgres psql -c "CREATE DATABASE tingr;"```

2. Create *user credentials*

```sudo -u postgres psql -c "CREATE USER username WITH PASSWORD 'yourpassword';"```

3. *Set user privileges* on the tingr database

```sudo -u postgres psql -c "GRANT ALL PRIVILEGES ON DATABASE tingr TO username;"```

```sudo -u postgres psql -d tingr -c "GRANT ALL ON SCHEMA public TO username;"```

4. Update *database.py* with your credentials

## USE:

### Run server
*Run "run.sh"*, or run "flask_server.py" manually with your own python path if it isn't python3.

Server opens on ```http://127.0.0.1:8000/```

### How to play

Pick your starting politician. 

Next page presents politicians that relate politically to this person. 

"Swipe" by liking or rejecting a politician.

Each like adds a politician to your bag (max of 6, can be removed and replaced).

At 6/6 politicians you have the option of seeing your most related party and other stats. Same option is given when no more politicians are left to swipe.


## ER Diagram

![ER diagram](ER_diagram_tingr.jpg)


## AI Declaration

1) Formål (hvad har du/I brugt værktøjet til)
   
Generativ AI er blevet brugt til de manuelle og tidstunge dele af opgaven, hvilket vil sige data genereringen og HTML koden, da disse to områder ikke er formålet med kurset. 
Dataindsamlingen med GenAI foregik ved at vi valgte hvilke politikkere og partier vi ville have data på, hvorefter vi kom med eksemmpler på mærkesager, citater, skandeler etc. og bad Gen AI om at søge på nettet for lignende eksempler på vores  andre politikkere og partier. Her blev AI brugt da det er en meget omfattende process at gøre manuelt, og ikke lærigt som datalog. 
HTML, CSS koden blev lavet med gen AI, og i mange tilfælde gjort pænere gennem AI, da det primære formål med faget ikke er frontend html produktion. 

Al python/flask/SQL interaktionn og database design er lavet af os med ingen brug af AI. AI har få gange rådgivet til python libraries der kunne bruges til f.eks. at få date-time, og dette er markeret med comments heri.

2) Arbejdsfase (hvornår i arbejdsprocessen har du/I brugt GAI)

Dataindsamling og data display.

3) Hvad gjorde du/I med outputtet (herunder også, om du/I har redigeret outputtet og arbejdet videre med det)

Data’et er blevet gennemarbejdet og valideret, samt redigeret så det kunne indsættes i databasen. HTML koden er indsat i de relevante templates, så det kunne virke med den egenkodedet backend. 

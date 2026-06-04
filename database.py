import psycopg2
import os
import csv

# Try to get from system enviroment variable
# Set your Postgres user and password as second arguments of these two next function calls
user = os.environ.get('PGUSER', 'postgres')
password = os.environ.get('PGPASSWORD', '123')
host = os.environ.get('HOST', '127.0.0.1')


def db_connection():
    db = "dbname='tingr' user=" + user + " host=" + host + " password =" + password
    conn = psycopg2.connect(db)

    return conn



def load_csv(cur, table, filename, columns):
    path = "data/" + filename

    column_names = ", ".join((c) for c in columns)
    placeholders = ", ".join(["%s"] * len(columns))

    insert_sql = (
        f"INSERT INTO {(table)} ({column_names}) "
        f"VALUES ({placeholders})"
    )

    with open(path, "r", encoding="utf-8-sig", newline="") as f:
        reader = csv.DictReader(f, delimiter=";")

        for row in reader:
            first_column = columns[0]

            if row.get(first_column) is None or row.get(first_column).strip() == "":
                continue

            values = []

            for col in columns:
                value = row.get(col)

                if value is None or value.strip() == "":
                    values.append(None)
                else:
                    value = value.strip()

                    if col in ["fordelingsscore", "vaerdiscore"]:
                        value = value.replace(",", ".")

                    values.append(value)

            cur.execute(insert_sql, values)


def init_db():
    conn = db_connection()
    cur = conn.cursor()

    with open("db_setup.sql", "r", encoding="utf-8-sig") as f:
        sql = f.read()

    cur.execute(sql)

    load_csv(cur, "parti", "parti.csv",
             ["partiid", "parti", "oprettet"])

    load_csv(cur, "politiker", "politiker.csv",
             ["politikerid", "navn", "fodselsdato", "partiid", "stilling", "uddannelse", "deltagelsesprocent"])

    load_csv(cur, "maerkesag", "maerkesag.csv",
             ["maerkesagid", "maerkesag", "fordelingsscore", "vaerdiscore"])

    load_csv(cur, "citat", "citat.csv",
             ["citatid", "politikerid", "citat"])

    load_csv(cur, "skandale", "skandale.csv",
             ["skandaleid", "politikerid", "beskrivelse"])

    load_csv(cur, "tidlparti", "tidlparti.csv",
             ["tidlpartiid", "partiid", "politikerid"])

    load_csv(cur, "maerkesagparti", "maerkesagparti.csv",
             ["maerkesagpartiid", "maerkesagid", "partiid"])

    load_csv(cur, "maerkesagpolitiker", "maerkesagpolitiker.csv",
             ["maerkesagpolitikerid", "maerkesagid", "politikerid"])

    conn.commit()
    cur.close()
    conn.close()

    print("database loaded")
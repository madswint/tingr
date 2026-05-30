import os
from database import db_connection

 # For simpelhedens skyld gemmer vi det i en klasse her, og viser direkte i html via denne.
 # En anden mulighed var at populærer databasen med spillerens valg så det kan genbruges til næste session,
 # men det tænker vi er unødvendigt
class Politician:
    def __init__(self, id, name, party, politics_score, born, position, education, 
                 photo_urls=None, quotes=None, scandals=None, issues=None):
        self.id = id
        self.name = name
        self.party = party
        self.politics_score = politics_score
        self.born = born
        self.position = position
        self.education = education
        self.photo_urls = photo_urls or []
        self.quotes = quotes or []
        self.scandals = scandals or []
        self.issues = issues or []


# Fordi vi ved at datasættet aldrig bliver større og det er et lille datasæt, så puller vi ved startup og gemmer i memory
# fremfor at SQL query hver gang vi skal e.g. bruge en random politiker, specifik politiker osv. 
# dette er simplere og giver bedre mening her
politicians: list[Politician] = []


bag: list[Politician] = []
swiped: list[Politician] = []
bag_politics_score: tuple[float, float] = (0.0, 0.0)


def bag_add(politician: Politician):
    if len(bag) < 6:
        bag.append(politician)
        bag_update_score()
    else:
        print("GIV MULIGHED FOR ERSTATTELSE AF POLITIKER VED BRUG AF REGEX?")


def bag_update_score():
    global bag_politics_score
    bag_politics_score = (
        sum((p.politics_score[0] or 0.0) for p in bag) * 1 / len(bag),
        sum((p.politics_score[1] or 0.0) for p in bag) * 1 / len(bag),)
    print(bag_politics_score)



def reset():
    global bag, swiped, bag_politics_score
    bag = []
    swiped = []
    bag_politics_score = (0.0, 0.0)
        
def build_politician(row, cur) -> Politician:
    _pol_id, _name, _party, _born, _position, _education = row

    cur.execute("select citat from citat where politikerid = %s", (_pol_id,))
    _quotes = [r[0] for r in cur.fetchall()]

    cur.execute("select beskrivelse from skandale where politikerid = %s", (_pol_id,))
    _scandals = [r[0] for r in cur.fetchall()]

    cur.execute("""
        select m.maerkesag from maerkesag m
        join maerkesagpolitiker mp on m.maerkesagid = mp.maerkesagid
        where mp.politikerid = %s
    """, (_pol_id,))
    _issues = [r[0] for r in cur.fetchall()]

    cur.execute("select ps.samletfordelingsscore,ps.samletvaerdiscore from politikerscore ps where ps.politikerid = %s", (_pol_id,))
    _politics_score = cur.fetchone() or (0.0, 0.0)

    _photo_urls = []
    photo_dir = f"static/politicians/{_pol_id}"
    if os.path.isdir(photo_dir):
        _photo_urls = [
            f"/static/politicians/{_pol_id}/{f}"
            for f in sorted(os.listdir(photo_dir))
        ]

    return Politician(
        id=_pol_id,
        name=_name.strip(),
        party=_party.strip(),
        politics_score=_politics_score,
        born=_born.strip() if _born else "",
        position=_position.strip() if _position else "",
        education=_education.strip() if _education else "",
        photo_urls=_photo_urls,
        quotes=_quotes,
        scandals=_scandals,
        issues=_issues,
    )


def load_all_politicians():
    global politicians
    conn = db_connection()
    cur = conn.cursor()
    cur.execute("""
        select p.politikerid, p.navn, pa.parti, p.fodselsdato, p.stilling, p.uddannelse
        from politiker p
        join parti pa on p.partiid = pa.partiid
    """)
    rows = cur.fetchall()
    politicians = [build_politician(row, cur) for row in rows]
    cur.close()
    conn.close()


def get_random_politicians(n: int) -> list[Politician]:
    import random
    swiped_ids = {p.id for p in swiped}
    pool = [p for p in politicians if p.id not in swiped_ids]
    return random.sample(pool, min(n, len(pool)))


def get_next_politician() -> Politician | None:
    swiped_ids = {p.id for p in swiped}
    for p in politicians:
        if p.id not in swiped_ids:
            return p
    return None

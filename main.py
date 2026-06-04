import os
import re
import requests
from datetime import datetime, timedelta, timezone
from email.utils import parsedate_to_datetime
from database import db_connection


PARTY_META = {
    "Moderaterne":                  {"color": "#692582", "logo": "moderaterne.png"},
    "Venstre":                      {"color": "#003d80", "logo": "venstre.png"},
    "SF":                           {"color": "#F0025A", "logo": "socialistisk_folkeparti.png"},
    "Socialdemokratiet":            {"color": "#E3000F", "logo": "socialdemokratiet.png"},
    "Dansk Folkeparti":             {"color": "#FFDD00", "logo": "dansk_folkeparti.png"},
    "Enhedslisten":                 {"color": "#EE2020", "logo": "enhedslisten.png"},
    "Borgernes Parti":              {"color": "#444444", "logo": "borgernes_parti.png"},
    "Liberal Alliance":             {"color": "#00B2A9", "logo": "liberal_alliance.png"},
    "Alternativet":                 {"color": "#00C050", "logo": "alternativet.png"},
    "Radikale Venstre":             {"color": "#9B1F82", "logo": "radikale.png"},
    "Det Konservative Folkeparti":  {"color": "#00A04B", "logo": "konservative.png"},
    "Frie Grønne":                  {"color": "#4CAF50", "logo": "frie_grønne.png"},
    "Danmarksdemokraterne":         {"color": "#2E5FA3", "logo": "dd.png"},
    "Løsgænger":                    {"color": "#888888", "logo": "ufg.png"},
}

# For simplicity we store politicians data in a class in order to easily render in html
class Politician:
    def __init__(self, id, name, party, politics_score, born, position, education,
                 photo_urls=None, quotes=None, scandals=None, issues=None, deltagelsesprocent=None):
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
        self.deltagelsesprocent = deltagelsesprocent
        meta = PARTY_META.get(party, {})
        logo = meta.get("logo")
        self.party_color = meta.get("color", "#888888") # løsgænger per. default
        self.party_logo = f"/static/party_logos/{logo}" if logo else None


# since the dataset is static and manually given (and its a small dataset), we only pull at startup and save it in memory
# instead of using a SQL query every time we need a random politcian, specific politcian etc.
# this is simpler and makes better sense to us given the scale
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
    _pol_id, _name, _party, _born, _position, _education, _deltagelsesprocent = row

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
        deltagelsesprocent=_deltagelsesprocent
    )


def load_all_politicians():
    global politicians
    conn = db_connection()
    cur = conn.cursor()
    cur.execute("""
        select p.politikerid, p.navn, pa.parti, p.fodselsdato, p.stilling, p.uddannelse, p.deltagelsesprocent
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


def fetch_news(name: str) -> list[dict]:
    cutoff = datetime.now(timezone.utc) - timedelta(days=180)
    query = name.replace(' ', '+') + "+site:tv2.dk+OR+site:dr.dk+OR+site:berlingske.dk+OR+site:politiken.dk+OR+site:ekstrabladet.dk+OR+site:bt.dk" 
    url = f"https://news.google.com/rss/search?q={query}"  # this was gotten from appending the query to to the base google query https://news.google.com/rss/search?q=
                                                           # however, for us it adds hl=no&gl=NO&ceid=NO:no to the query, and we cant force location so we get primarily norwegian articles it seems?
    def reg(pattern, text):     # for readability
        m = re.search(pattern, text, re.DOTALL) #DOTALL was needed to hit contents that are on several lines..
        return m.group(1) if m else ""  # just return the first result incase we have more

    res = requests.get(url, timeout=5)
    articles = []
    for item in re.findall("<item>(.*?)</item>", res.text, re.DOTALL): # ? to stop at the first occurence
        title = reg("<title>(.*?)</title>", item)      # -"-...
        link = reg("<link>(.*?)</link>", item)
        source = reg("<source[^>]*>(.*?)</source>", item)  # every but '>', zero or more of that, since source is followed by ="url".
        description = reg("<description>(.*?)</description>", item)
        pub_date = reg("<pubDate>(.*?)</pubDate>", item)
        published = parsedate_to_datetime(pub_date) if pub_date else None   # <-- AI help to filter recent 
        if published and published < cutoff:
            continue
        if re.search(name, title, re.IGNORECASE) or re.search(name, description, re.IGNORECASE): # Match on aA (not case sensitive)
            articles.append({"title": title, "url": link, "source": source})
    return articles[:5]  # seem to mostly return results from Politiken.dk, we think its because they also publish articles in english and perhaos this gets picked up better by google?
                        # removing Politiken.dk we get primarily dr.dk, but also rare to have articles.
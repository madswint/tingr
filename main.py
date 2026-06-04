import os
import re
import requests
from datetime import datetime, timedelta, timezone
from email.utils import parsedate_to_datetime
from database import db_connection
from math import dist 

conn = db_connection()
cur = conn.cursor() ## Needs to be closed again on exit.. How to do ~Main() equivalant in flask??

PARTY_META = {
    1: {"color": "#692582", "logo": "moderaterne.png"},
    2: {"color": "#003d80", "logo": "venstre.png"},
    3: {"color": "#F0025A", "logo": "socialistisk_folkeparti.png"},
    4: {"color": "#E3000F", "logo": "socialdemokratiet.png"},
    5: {"color": "#FFDD00", "logo": "dansk_folkeparti.png"},
    6: {"color": "#EE2020", "logo": "enhedslisten.png"},
    7: {"color": "#444444", "logo": "borgernes_parti.png"},
    8: {"color": "#00B2A9", "logo": "liberal_alliance.png"},
    9: {"color": "#00C050", "logo": "alternativet.png"},
    10: {"color": "#9B1F82", "logo": "radikale.png"},
    11: {"color": "#00A04B", "logo": "konservative.png"},
    12: {"color": "#4CAF50", "logo": "frie_grønne.png"},
    13: {"color": "#2E5FA3", "logo": "dd.png"},
    14: {"color": "#888888", "logo": "ufg.png"},
}

def party_name_to_id(name):
    cur.execute("select partiid from parti where parti = %s", (name,))
    row = cur.fetchone()
    return row[0] if row else 14


# For simplicity we store politicians data in a class in order to easily render in html
class Politician:
    def __init__(self, id, name, party, politics_score, born, position, education,
                 photo_urls=None, quotes=None, scandals=None, issues=None, established=None, deltagelsesprocent=None):
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
        self.established = established or []
        self.deltagelsesprocent = deltagelsesprocent
        meta = PARTY_META.get(party_name_to_id(party), {})
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


def bag_add(politician):
    if len(bag) < 6 and politician not in bag:
        bag.append(politician)
        bag_update_score()

def bag_remove(politician: Politician):
    if politician not in bag:
        print("Pretend this is a handled exception..")
    else:
        bag.remove(politician)
        bag_update_score()


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
        
def build_politician(row):
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

    cur.execute("""select tiltag 
                from Tiltag 
                where politikerid = %s""", (_pol_id,))
    _established = [r[0] for r in cur.fetchall()]

    cur.execute("select ps.samletfordelingsscore,ps.samletvaerdiscore from politikerscore ps where ps.politikerid = %s", (_pol_id,))
    _politics_score = cur.fetchone() or (0.0, 0.0)

    _photo_urls = []
    photo_dir = f"static/politicians/{_pol_id}"
    if os.path.isdir(photo_dir):                # <- AI help
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
        established=_established,
        deltagelsesprocent=_deltagelsesprocent
    )


def load_all_politicians():
    global politicians
    cur.execute("""
        select p.politikerid, p.navn, pa.parti, p.fodselsdato, p.stilling, p.uddannelse, p.deltagelsesprocent
        from politiker p
        join parti pa on p.partiid = pa.partiid
    """)
    rows = cur.fetchall()
    politicians = [build_politician(row) for row in rows]


def get_random_politicians(n):
    import random
    swiped_ids = {p.id for p in swiped}
    pool = [p for p in politicians if p.id not in swiped_ids]
    return random.sample(pool, min(n, len(pool)))


def get_next_politician():
    swiped_ids = {p.id for p in swiped}

    candidates = [p for p in politicians if p.id not in swiped_ids]

    if len(candidates) == 0:
        return None

    return min(candidates, key=lambda p: dist(bag_politics_score, p.politics_score)
    )

def build_end_stats():
    liked = bag
    swiped_all = swiped

    swiped_right_count = len(liked)
    swiped_left_count = len([p for p in swiped_all if p not in liked])
    total_swiped = len(swiped_all)
    like_rate = round(swiped_right_count / total_swiped * 100) if total_swiped else 0

    avg_attendance = None
    attendances = [p.deltagelsesprocent for p in liked if p.deltagelsesprocent is not None]
    if attendances:
        avg_attendance = round(sum(attendances) / len(attendances), 1)

    scandals_total = sum(len(p.scandals) for p in liked)

    most_scandalous = max(liked, key=lambda p: len(p.scandals)) if liked else None

    
    cur.execute("""
        select pa.parti, pas.gnsfordelingscore, pas.gnsvaerdiscore
        from partiscore pas
        join parti pa on pa.partiid = pas.partiid
    """)
    party_scores = cur.fetchall()


    closest_party = None
    closest_dist = float('inf')
    for name, f_score, v_score in party_scores:
        if f_score is None or v_score is None:
            continue
        d = dist(bag_politics_score, (f_score, v_score))
        if d < closest_dist:
            closest_dist = d
            closest_party = name

    party_color = PARTY_META.get(party_name_to_id(closest_party), {}).get("color", "#888888")
    party_logo = PARTY_META.get(party_name_to_id(closest_party), {}).get("logo")

    return {
        "bag": liked,
        "top_party": closest_party,
        "party_color": party_color,
        "party_logo": f"/static/party_logos/{party_logo}" if party_logo else None,
        "swiped_right": swiped_right_count,
        "swiped_left": swiped_left_count,
        "total_swiped": total_swiped,
        "like_rate": like_rate,
        "avg_attendance": avg_attendance,
        "scandals_total": scandals_total,
        "most_scandalous": most_scandalous,
        "axis_fordeling": round(bag_politics_score[0], 2),
        "axis_vaerdi": round(bag_politics_score[1], 2),
    }
    


def fetch_news(name):
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
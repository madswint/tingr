DROP SCHEMA public CASCADE;
CREATE SCHEMA public;


CREATE TABLE IF NOT EXISTS parti (
    partiid INTEGER,
    parti TEXT,
    oprettet char(20),
    PRIMARY KEY (partiid)
);

CREATE TABLE IF NOT EXISTS politiker (
    politikerid INTEGER,
    navn char(40),
    fodselsdato char(20),
    partiid integer REFERENCES parti(partiid),
    stilling char(60),
    uddannelse char(100),
    PRIMARY KEY (politikerid)
);

CREATE TABLE IF NOT EXISTS maerkesag (
    maerkesagid INTEGER,
    maerkesag TEXT,
    fordelingsscore FLOAT,
    vaerdiscore FLOAT,
    PRIMARY KEY (maerkesagid)
);

CREATE TABLE IF NOT EXISTS tidlparti (
    tidlpartiid INTEGER,
    partiid INTEGER REFERENCES parti(partiid),
    politikerid INTEGER REFERENCES politiker(politikerid),
    PRIMARY KEY (tidlpartiid)
);

CREATE TABLE IF NOT EXISTS maerkesagpolitiker (
    maerkesagpolitikerid INTEGER,
    maerkesagid INTEGER REFERENCES maerkesag(maerkesagid),
    politikerid INTEGER REFERENCES politiker(politikerid),
    PRIMARY KEY (maerkesagpolitikerid)
);

CREATE TABLE IF NOT EXISTS maerkesagparti (
    maerkesagpartiid INTEGER,
    maerkesagid INTEGER REFERENCES maerkesag(maerkesagid),
    partiid INTEGER REFERENCES parti(partiid),
    PRIMARY KEY (maerkesagpartiid)
);

CREATE TABLE IF NOT EXISTS skandale (
    skandaleid INTEGER,
    politikerid INTEGER REFERENCES politiker(politikerid),
    beskrivelse TEXT,
    PRIMARY KEY (skandaleid)
);

CREATE TABLE IF NOT EXISTS citat (
    citatid INTEGER,
    politikerid INTEGER REFERENCES politiker(politikerid),
    citat TEXT,
    PRIMARY KEY (citatid)
);

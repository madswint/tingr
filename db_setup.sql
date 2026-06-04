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
    deltagelsesprocent FLOAT,
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

CREATE TABLE IF NOT EXISTS tiltag (
    tiltagid INTEGER,
    politikerid INTEGER REFERENCES politiker(politikerid),
    periode TEXT,
    tiltag TEXT,
    beskrivelse  TEXT,
    rolle TEXT,
    PRIMARY KEY (tiltagid)
);

CREATE OR REPLACE VIEW politikerscore AS 
    with politikermaerkesag as (
        select pol.politikerid, pol.navn, pol.partiid, avg(sag.fordelingsscore) as gnsfordelingscore, avg(sag.vaerdiscore) as gnsvaerdiscore
        from politiker pol
        join maerkesagpolitiker sagpol on sagpol.politikerid = pol.politikerid
        join maerkesag sag on sag.maerkesagid = sagpol.maerkesagid
        group by  pol.politikerid, pol.navn, pol.partiid
    ),

    partimaerkesag as (
        select par.partiid, par.parti, avg(sag.fordelingsscore) as gnsfordelingscore, avg(sag.vaerdiscore) as gnsvaerdiscore
        from parti par
        join maerkesagparti sagpar on sagpar.partiid = par.partiid
        join maerkesag sag on sag.maerkesagid = sagpar.maerkesagid
        group by par.partiid, par.parti
    )


    select polsag.politikerid, polsag.navn, parsag.partiid, parsag.parti, (polsag.gnsfordelingscore * 0.7 + parsag.gnsfordelingscore * 0.3) as samletfordelingsscore, (polsag.gnsvaerdiscore * 0.7 + parsag.gnsvaerdiscore * 0.3) as samletvaerdiscore
    from politikermaerkesag polsag
    join partimaerkesag parsag on polsag.partiid = parsag.partiid;

CREATE OR REPLACE VIEW partiscore AS 
    select par.partiid, par.parti, avg(sag.fordelingsscore) as gnsfordelingscore, avg(sag.vaerdiscore) as gnsvaerdiscore
    from parti par
    join maerkesagparti sagpar on sagpar.partiid = par.partiid
    join maerkesag sag on sag.maerkesagid = sagpar.maerkesagid
    group by par.partiid, par.parti;

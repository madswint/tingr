DROP SCHEMA public CASCADE;
CREATE SCHEMA public;

CREATE TABLE IF NOT EXISTS Politiker (
    politiker_id SERIAL PRIMARY KEY,
    navn TEXT NOT NULL,
    fødselsdato DATE NOT NULL
 /*    parti_id 
    deltagelses_procent
    stilling
    uddannelse */
);

CREATE TABLE IF NOT EXISTS Tidligere_Ægteskaber (

);

CREATE TABLE IF NOT EXISTS Parti (

);

CREATE TABLE IF NOT EXISTS Mærkesag-politiker (

);

CREATE TABLE IF NOT EXISTS Mærkesager (

);

CREATE TABLE IF NOT EXISTS Mærkesag-parti (

);

CREATE TABLE IF NOT EXISTS Skandaler (

);

CREATE TABLE IF NOT EXISTS Citater (

);
import sqlalchemy
from sqlalchemy import text

engine = sqlalchemy.create_engine("sqlite+pysqlite:///:memory:", echo=True)

def init_db():
    with engine.connect() as conn:
        print("Connected to the database")
        conn.execute(text("CREATE TABLE user (discord_id TEXT, osu_id INTEGER, rolls_amount INTEGER, rolls_done INTEGER)"))
        conn.execute(text("CREATE TABLE tasks (task_id INTEGER, tier INTEGER, map_id INTEGER, criteria TEXT, criteria_amount INTEGER)"))
        conn.execute(text("CREATE TABLE tasks_complition (complition_time DATETIME, task_id INTEGER, discord_id TEXT)"))
        conn.execute(text("CREATE TABLE gacha (rarity_id INTEGER, gacha_text TEXT)"))
        conn.execute(text("CREATE TABLE gacha_rarity (rarity_id INTEGER, rarity TEXT, odds REAL)"))
        conn.execute(text('INSERT INTO user (discord_id, osu_id, rolls_amount, rolls_done) VALUES (297349637411569665, 9274544, 0, 0)'))

def dump():
    with engine.connect() as con:
        with open('dump.sql', 'w') as f: 
            for line in con.iterdump():
                f.write('%s\n' % line)
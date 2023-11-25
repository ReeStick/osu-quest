import sqlalchemy
from sqlalchemy import text

engine = sqlalchemy.create_engine("sqlite+pysqlite:///:memory:", echo=True)

def init_db():
    with engine.connect() as conn:
        conn.execute(text("CREATE TABLE user (discord_id TEXT, osu_id INTEGER, rolls_amount INTEGER, rolls_done INTEGER)"))
        conn.execute(text("CREATE TABLE map_tasks (tier INTEGER, map_id INTEGER, modset TEXT)"))
        conn.execute(text("CREATE TABLE count_tasks (criteria TEXT, criteria_amount INTEGER)"))
        conn.execute(text("CREATE TABLE tasks_complition (task_id INTEGER, discord_id TEXT, complition_status INTEGER)"))
        conn.execute(text("CREATE TABLE gacha (rarity_id INTEGER, gacha_text TEXT)"))
        conn.execute(text("CREATE TABLE gacha_rarity (rarity_id INTEGER, rarity TEXT, odds REAL)"))
        
def add_count_task(criteria: str, criteria_amount: int):
    '''
    Adds a task in db
    criteria - One of 'combo', 'score', 'total_stars', 'pp', 'maps' params
    criteria_amount - how much of criteria is need to pass
    '''
    with engine.connect() as conn:
        if criteria in ['combo', 'score', 'total_stars', 'pp', 'maps'] and criteria_amount > 0:
            conn.execute(f'INSERT INTO count_tasks (criteria, criteria_amount) VALUES ({criteria}, {criteria_amount})')
            conn.commit()
            return f"Added - {criteria}:{criteria_amount}"
        else:
            return "Can't add this type of count task"

def dump():
    with engine.connect() as con:
        with open('dump.sql', 'w') as f: 
            for line in con.iterdump():
                f.write('%s\n' % line)
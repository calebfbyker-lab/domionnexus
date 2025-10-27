import sqlite3, os
DB=os.environ.get("NEXUS_DB","./nexus.db")
def migrate():
    c=sqlite3.connect(DB)
    c.executescript("""
    create table if not exists kv(key text primary key, val text);
    alter table events add column meta text default '{}' ;
    """)
    c.commit(); c.close()

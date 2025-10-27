import sqlite3, os
DB=os.environ.get("NEXUS_DB","./nexus.db")
def render_metrics()->str:
    c=sqlite3.connect(DB)
    ev = c.execute("select count(*) from events").fetchone()[0]
    pr = c.execute("select count(*) from proofs").fetchone()[0]
    c.close()
    return "\n".join([
        "# HELP nexus_events_total Total events ingested",
        "# TYPE nexus_events_total counter",
        f"nexus_events_total {ev}",
        "# HELP nexus_proofs_total Total AEON proofs stored",
        "# TYPE nexus_proofs_total counter",
        f"nexus_proofs_total {pr}",
        ""
    ])

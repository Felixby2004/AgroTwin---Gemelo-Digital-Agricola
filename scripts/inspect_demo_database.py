from dotenv import dotenv_values
import psycopg
url = dotenv_values('.env')['DATABASE_URL'].replace('postgresql+psycopg://','postgresql://')
try:
 with psycopg.connect(url, connect_timeout=12) as conn:
  with conn.cursor() as cur:
   cur.execute("SELECT table_name FROM information_schema.tables WHERE table_schema='public' ORDER BY table_name")
   print('TABLES:', [r[0] for r in cur.fetchall()])
   for table in ['users','parcels','sensors','machine_evidence','farmer_knowledge','decision_traces','data_consents']:
    cur.execute('SELECT count(*) FROM '+table)
    print(table, cur.fetchone()[0])
   cur.execute("SELECT id, system_role, status FROM users WHERE email=%s",('farmer@test.com',))
   print('ADMIN_MATCH:',cur.fetchone())
   cur.execute("SELECT extname FROM pg_extension")
   print('EXTENSIONS:',[r[0] for r in cur.fetchall()])
except Exception as exc:
 print('CONNECTION_FAILED:', type(exc).__name__)
 raise SystemExit(1)

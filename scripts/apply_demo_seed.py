"""Validate/apply additive demo seed; default ALWAYS rolls back."""
import argparse
import hashlib
import json
from pathlib import Path
from datetime import datetime, timezone
import psycopg
from dotenv import dotenv_values

ROOT=Path(__file__).resolve().parents[1]
parser=argparse.ArgumentParser()
parser.add_argument('--apply',action='store_true')
args=parser.parse_args()
path=ROOT/'artifacts/demo_publicacion/seed_demo_agrotwin.sql'
sql=path.read_text(encoding='utf-8')
assert sql.rstrip().endswith('COMMIT;')
# Strip only the outer transaction; psycopg owns the transaction below.
body=sql.partition('\nBEGIN;')[2].rstrip()[:-len('COMMIT;')]
assert body and '\nCOMMIT;' not in body and '\nBEGIN;' not in body
url=dotenv_values(ROOT/'.env')['DATABASE_URL'].replace('postgresql+psycopg://','postgresql://')
tables=['parcels','parcel_memberships','sensors','machine_evidence','farmer_knowledge','decision_traces','data_consents','data_audit_events']
try:
 with psycopg.connect(url,autocommit=False,connect_timeout=15) as conn:
  with conn.cursor() as cur:
   cur.execute('SELECT id,email,password_hash,system_role,status FROM users ORDER BY id')
   original_users=cur.fetchall()
   before={}
   for table in tables:
    cur.execute('SELECT count(*) FROM '+table)
    before[table]=cur.fetchone()[0]
   cur.execute(body,prepare=False)
   cur.execute("SELECT count(*) FROM parcels WHERE id LIKE 'DEMO26-%' AND ST_IsValid(geometry) AND area_ha>0")
   assert cur.fetchone()[0]==4
   cur.execute("SELECT count(*) FROM machine_evidence WHERE id LIKE 'DEMO26-%' AND provenance->>'source_type'='SYNTHETIC'")
   assert cur.fetchone()[0]==6740
   snapshot=json.loads((path.parent/'demo_dataset.json').read_text(encoding='utf-8'))
   cur.execute("SELECT id,observed_at,value FROM machine_evidence WHERE id LIKE 'DEMO26-%'")
   observed={row[0]:(row[1].isoformat(),row[2]) for row in cur.fetchall()}
   expected={row['id']:(row['observed_at'],row['value']) for row in snapshot['evidence']}
   assert observed==expected, 'Seed content differs from the frozen snapshot'
   cur.execute('SELECT id,email,password_hash,system_role,status FROM users ORDER BY id')
   assert cur.fetchall()==original_users, 'User accounts unexpectedly changed'
   after={}
   for table in tables:
    cur.execute('SELECT count(*) FROM '+table)
    after[table]=cur.fetchone()[0]
  if args.apply:
   conn.commit()
  else:
   conn.rollback()
   with conn.cursor() as cur:
    for table in tables:
     cur.execute('SELECT count(*) FROM '+table)
     assert cur.fetchone()[0]==before[table], 'Rollback failed'
   conn.rollback()
  record=dict(mode='COMMITTED' if args.apply else 'DRY_RUN_ROLLED_BACK',at=datetime.now(timezone.utc).isoformat(),sql_sha256=hashlib.sha256(path.read_bytes()).hexdigest(),users_unchanged=True,before=before,after=after)
  if args.apply:
   (path.parent/'neon_seed_receipt.json').write_text(json.dumps(record,indent=2),encoding='utf-8')
  print(json.dumps(record))
except Exception as exc:
 print('SEED_FAILED:',type(exc).__name__,getattr(exc,'sqlstate',None))
 raise SystemExit(1)

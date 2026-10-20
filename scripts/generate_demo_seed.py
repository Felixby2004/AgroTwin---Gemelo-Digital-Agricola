"""Build a reproducible, additive PostgreSQL demo dataset. No credentials here."""
import argparse
import json
import math
from datetime import datetime, timedelta, timezone
from pathlib import Path
import random
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
BATCH = 'AGROTWIN-DEMO-20261020-V1'
DEFAULT_END = datetime.fromisoformat('2026-10-20T13:00:00+00:00')


def build_dataset(end):
    end = end.astimezone(timezone.utc).replace(minute=0, second=0, microsecond=0)
    start = end - timedelta(days=14)
    rng = random.Random(20261020)
    data = dict(batch=BATCH, start=start.isoformat(), end=end.isoformat(), parcels=[], sensors=[], evidence=[], knowledge=[], traces=[])
    configs = [
        ('MOCH', 'Moche maíz', 'Maize', -8.1718, -78.9960, .00130, .00105, 22, 5, .295, 20),
        ('VIRU', 'Virú cebolla', 'Onion', -8.4140, -78.7520, .00110, .00090, 23, 6, .275, 15),
        ('CHAO', 'Chao palta', 'Avocado', -8.5430, -78.6610, .00160, .00110, 23, 5, .31, 25),
        ('OTUZ', 'Otuzco papa', 'Potato', -7.9000, -78.5690, .00095, .00085, 13, 7, .32, 20),
    ]
    for index, (code, name, crop, lat, lon, dx, dy, temp, amplitude, theta, limit) in enumerate(configs, 1):
        pid = f'DEMO26-{code}'
        polygon = {'type':'Polygon','coordinates':[[[lon,lat],[lon+dx,lat],[lon+dx,lat+dy],[lon,lat+dy],[lon,lat]]]}
        area = 111320 * math.cos(math.radians(lat)) * dx * 110574 * dy / 10000
        parcel = dict(id=pid, name='DEMO - '+name+' (simulado)', crop_type=crop, area_approx_ha=round(area,3), geometry=polygon, created_at=start.isoformat())
        data['parcels'].append(parcel)
        meta = dict(seed_batch=BATCH, is_simulated=True, data_origin='SYNTHETIC', note='Datos ficticios para demostración; no son observaciones de campo.')
        for suffix, label, variables in [('SM','Humedad radicular',['soil_moisture']),('MET','Estación meteorológica',['air_temperature','relative_humidity','rainfall']),('FL','Caudal de riego',['flow_rate'])]:
            data['sensors'].append(dict(id=f'{pid}-{suffix}', parcel_id=pid, name=f'DEMO {label} {code}', sensor_type='SIMULATED_IOT', variables=variables, latitude=lat+dy/2, longitude=lon+dx/2, manufacturer='Simulador AgroTwin', model='DEMO-v1', installed_at=start.isoformat(), is_active=True, metadata=meta, created_at=start.isoformat(), updated_at=end.isoformat()))
        for hour in range(337):
            at = start + timedelta(hours=hour)
            local_hour = (at.hour-5)%24
            day = hour//24
            daylight = max(0, math.sin(math.pi*(local_hour-6)/12))
            irrigating = day in (3,7,11) and local_hour in (6,7)
            rainfall = round((1.4 if code=='OTUZ' else .15) * (1+.2*rng.random()),3) if day in (6,10) and local_hour in (2,3,4) else 0.0
            irrigation_mm = 5.0 if irrigating else 0.0
            theta = max(.12,min(.41, theta + (.85*irrigation_mm+.8*rainfall)/350 - (.00022+.00075*daylight) + rng.gauss(0,.00017)))
            values = [
                ('soil_water_state',{'soil_moisture':round(theta,5)},'m3/m3','SM'),
                ('air_temperature',round(temp-amplitude*math.cos((local_hour-3)/24*2*math.pi)+rng.gauss(0,.35),2),'degC','MET'),
                ('relative_humidity',round(max(25,min(96,76-22*daylight+rng.gauss(0,1.8))),2),'%','MET'),
                ('rainfall',rainfall,'mm','MET'),
                ('flow_rate',round(irrigation_mm*area*10000/60,2),'L/min','FL'),
            ]
            for variable,value,unit,suffix in values:
                eid=f'{pid}-{hour:03}-{variable}'
                data['evidence'].append(dict(id=eid,parcel_id=pid,variable=variable,value=value,unit=unit,observed_at=at.isoformat(),status='ACTIVE',quality_score=round(.92+.06*rng.random(),3),uncertainty=None,
                    provenance=dict(source_type='SYNTHETIC',source_name='AGROTWIN_DEMO_GENERATOR',source_id=f'{pid}-{suffix}',source_version='1.0',generated_at=at.isoformat(),valid_at=at.isoformat(),spatial_scope=pid,transformation='Balance horario ilustrativo, pulsos de riego, ciclo diurno y ruido reproducible.',parent_ids=[],metadata=meta),
                    metadata={**meta,'sensor_id':f'{pid}-{suffix}','ingestion_type':'SIMULATED_IOT','input_variable':'soil_moisture' if suffix=='SM' else variable,'original_unit':unit,'age_hours':0,'status_note':'ACTIVE al momento de la ingestión simulada, no certifica vigencia actual.'},created_at=at.isoformat()))
        knowledge = [
            ('CONSTRAINT',{'variable':'irrigation_mm','operator':'<=','value':limit,'unit':'mm'},'HARD',['irrigation_mm'],'Límite de dotación por turno en el caso demostrativo.'),
            ('PREFERENCE',{'variable':'irrigation_mm','preference':'MINIMIZE_WATER','label':'Minimizar agua','priority':4},None,['irrigation_mm'],'Se prefiere la menor dosis entre alternativas viables.'),
            ('OBSERVATION',{'variable':'soil_moisture','value':round(theta,3),'unit':'m3/m3','observation':'Observación ficticia del estrato radicular.'},None,['soil_moisture'],'Observación simulada para probar el aporte de conocimiento.'),
            ('EVENT',{'event_type':'IRRIGATION','description':'Riego simulado de 10 mm distribuido en dos horas.','occurred_at':(start+timedelta(days=11)).isoformat()},None,['irrigation_mm'],'Evento ilustrativo; no corresponde a una operación real.'),
            ('LOCAL_KNOWLEDGE',{'statement':'En el sector bajo se observa menor velocidad de secado después del riego (supuesto del escenario).','context':'FARMER_LOCAL_KNOWLEDGE'},None,['soil_water_state'],'Conocimiento local ficticio, pendiente de validación de campo.'),
            ('LOCAL_KNOWLEDGE',{'statement':f'Caso de cultivo {crop}; siembra demostrativa 60 días antes del cierre. Riego por goteo.','context':'CROP_CONTEXT','crop_type':crop,'planting_date':(end-timedelta(days=60)).date().isoformat(),'irrigation_system':'DRIP','engine_support':'SUPPORTED' if crop=='Maize' else 'EXPERIMENTAL'},None,['crop_state'],'Contexto de cultivo simulado; no implica calibración del motor para este cultivo.'),
        ]
        for number,(kind,payload,constraint,affects,rationale) in enumerate(knowledge,1):
            data['knowledge'].append(dict(id=f'{pid}-FK{number}',parcel_id=pid,knowledge_type=kind,source_id=f'DEMO-PERSONA-{index}',source_role='FARMER',payload=payload,created_at=end.isoformat(),valid_from=start.isoformat(),valid_until=(end+timedelta(days=90)).isoformat(),reported_confidence=.8,validation_status='UNVERIFIED',constraint_type=constraint,affects=affects,rationale=rationale,metadata=meta))
    return data


def add_engine_traces(data):
    """Run the application's real demonstration reasoning; never invent a dose."""
    from types import SimpleNamespace
    from database.adapters.evidence_adapter import EvidenceAdapter
    from database.adapters.farmer_knowledge_adapter import FarmerKnowledgeAdapter
    from database.adapters.decision_trace_adapter import DecisionTraceAdapter
    from engines.reasoning_orchestrator import ReasoningOrchestrator
    from engines.decision_trace_engine import DecisionTraceEngine
    from experiments.case_factory import ExperimentalCaseFactory
    from twin.experiment import ExperimentCondition
    scenario_case = ExperimentalCaseFactory().build(ExperimentCondition.COMPLETE)
    for parcel in data['parcels']:
        pid=parcel['id']
        rows=[e for e in data['evidence'] if e['parcel_id']==pid and e['observed_at']==data['end']]
        def model(row):
            obj=dict(row)
            for key in ('created_at','observed_at','valid_from','valid_until'):
                if obj.get(key): obj[key]=datetime.fromisoformat(obj[key])
            obj['metadata_json']=obj.pop('metadata',{})
            return SimpleNamespace(**obj)
        evidence=[EvidenceAdapter.from_model(model(row)) for row in rows]
        knowledge=[FarmerKnowledgeAdapter.from_model(model(row)) for row in data['knowledge'] if row['parcel_id']==pid]
        result=ReasoningOrchestrator().run(scenarios=scenario_case.scenarios,evidence=evidence,farmer_knowledge=knowledge)
        trace=DecisionTraceEngine().build_trace(reasoning_result=result,evidence=evidence,farmer_knowledge=knowledge,parcel_id=pid)
        trace.trace_id=f'{pid}-TRACE1'
        trace.created_at=datetime.fromisoformat(data['end'])
        trace.metadata.update(seed_batch=BATCH,is_simulated=True,data_origin='SYNTHETIC',scenario_source='ExperimentalCaseFactory.COMPLETE',warning='Escenarios de referencia del software, no calibrados a esta parcela ni cultivo. No se ejecutó riego real.')
        row=DecisionTraceAdapter.to_model_dict(trace)
        row['id']=row.pop('trace_id')
        row['created_at']=row['created_at'].isoformat()
        data['traces'].append(row)


def literal(value, json_value=False):
    if value is None: return 'NULL'
    if json_value: return "'"+json.dumps(value,ensure_ascii=False,separators=(',',':')).replace("'","''")+"'::json"
    if isinstance(value,bool): return 'TRUE' if value else 'FALSE'
    if isinstance(value,(int,float)): return str(value)
    return "'"+str(value).replace("'","''")+"'"


def render_sql(data):
    lines=["-- AgroTwin: SOLO DATOS SIMULADOS. Lote "+BATCH,
           '-- Carga aditiva e idempotente. No modifica usuarios, contraseñas ni registros existentes.',
           '-- Ejecútese sobre el esquema migrado de AgroTwin con PostGIS disponible.',
           'BEGIN;', "SET LOCAL lock_timeout = '10s';", "SET LOCAL statement_timeout = '120s';",
           "DO $$ BEGIN IF NOT EXISTS (SELECT 1 FROM users WHERE email='farmer@test.com' AND system_role='ADMIN' AND status='ACTIVE') THEN RAISE EXCEPTION 'Se requiere el ADMIN existente'; END IF; END $$;"]
    def insert(table,row,json_keys=()):
        lines.append(f"INSERT INTO {table} ({','.join(row)}) VALUES ({','.join(literal(v,k in json_keys) for k,v in row.items())}) ON CONFLICT DO NOTHING;")
    for p in data['parcels']:
        geom="ST_SetSRID(ST_GeomFromGeoJSON("+literal(json.dumps(p['geometry']))+"),4326)"
        lines.append(f"INSERT INTO parcels(id,name,crop_type,area_ha,geometry,created_at) VALUES ({literal(p['id'])},{literal(p['name'])},{literal(p['crop_type'])},ST_Area(({geom})::geography)/10000,{geom},{literal(p['created_at'])}) ON CONFLICT DO NOTHING;")
        lines.append("INSERT INTO parcel_memberships(id,parcel_id,user_id,role,created_at,metadata_json) SELECT '"+p['id']+"-MEM-'||u.id,"+literal(p['id'])+",u.id,CASE u.email WHEN 'farmer@test.com' THEN 'OWNER' WHEN 'agricultor@test.com' THEN 'FARMER' WHEN 'agronomo@test.com' THEN 'AGRONOMIST' ELSE 'VIEWER' END,"+literal(data['end'])+"::timestamptz,"+literal({'seed_batch':BATCH,'is_simulated':True},True)+" FROM users u WHERE u.email IN ('farmer@test.com','agricultor@test.com','agronomo@test.com','investigador@test.com','user@test.com') ON CONFLICT DO NOTHING;")
        insert('data_consents',dict(id=p['id']+'-CONSENT',parcel_id=p['id'],subject_id='USER-INITIAL-ADMIN',purposes=['DIGITAL_TWIN_OPERATION','RECOMMENDATION','RESEARCH','EXPORT'],permissions=['READ','WRITE','PROCESS','EXPORT'],allowed_data_categories=['PARCEL_DATA','MACHINE_EVIDENCE','FARMER_KNOWLEDGE','DECISION_TRACE'],created_at=data['end'],valid_until=None,status='ACTIVE',metadata_json={'seed_batch':BATCH,'is_simulated':True,'note':'Política de exportación para datos ficticios, no consentimiento de una persona participante.'}),('purposes','permissions','allowed_data_categories','metadata_json'))
    for row in data['sensors']: insert('sensors',row,('variables','metadata'))
    for row in data['evidence']: insert('machine_evidence',row,('value','uncertainty','provenance','metadata'))
    for row in data['knowledge']: insert('farmer_knowledge',row,('payload','affects','metadata'))
    for row in data['traces']: insert('decision_traces',row,('evidence_ids','knowledge_ids','conflict_ids','transformation_ids','feasible_scenarios','rejected_scenarios','ranking','provisional_recommendation','farmer_response','outcome','metadata'))
    for p in data['parcels']:
        insert('data_audit_events',dict(id=p['id']+'-AUDIT-SEED',parcel_id=p['id'],actor_id='USER-INITIAL-ADMIN',action='DEMO_DATA_SEED',allowed=True,consent_id=p['id']+'-CONSENT',purpose='RESEARCH',data_category='PARCEL_DATA',created_at=data['end'],details={'seed_batch':BATCH,'is_simulated':True,'action_note':'Carga autorizada de datos simulados para demostración.'}),('details',))
    lines.append('COMMIT;')
    return '\n'.join(lines)+'\n'


if __name__=='__main__':
    parser=argparse.ArgumentParser()
    parser.add_argument('--end')
    args=parser.parse_args()
    selected_end=datetime.fromisoformat(args.end) if args.end else DEFAULT_END
    if selected_end != DEFAULT_END:
        parser.error('Este lote está congelado. Un periodo diferente requiere otro lote e identificadores.')
    out=ROOT/'artifacts'/'demo_publicacion'
    out.mkdir(parents=True,exist_ok=True)
    dataset_path=out/'demo_dataset.json'
    sql_path=out/'seed_demo_agrotwin.sql'
    if dataset_path.exists() or sql_path.exists():
        if not dataset_path.exists() or not sql_path.exists():
            parser.error('Snapshot incompleto; restaura ambos archivos antes de continuar.')
        data=json.loads(dataset_path.read_text(encoding='utf-8'))
        if data['batch'] != BATCH or datetime.fromisoformat(data['end']) != DEFAULT_END or sql_path.read_text(encoding='utf-8') != render_sql(data):
            parser.error('El snapshot no coincide con el lote congelado; no se sobrescribió.')
        print(json.dumps({'snapshot_reused':True,'end':data['end'],**{key:len(data[key]) for key in ('parcels','sensors','evidence','knowledge','traces')}}))
        raise SystemExit(0)
    data=build_dataset(selected_end)
    add_engine_traces(data)
    (out/'seed_demo_agrotwin.sql').write_text(render_sql(data),encoding='utf-8')
    (out/'demo_dataset.json').write_text(json.dumps(data,ensure_ascii=False,indent=2),encoding='utf-8')
    print(json.dumps({key:len(data[key]) for key in ('parcels','sensors','evidence','knowledge','traces')}))

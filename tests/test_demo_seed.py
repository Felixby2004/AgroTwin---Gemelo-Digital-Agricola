from datetime import datetime, timezone
from scripts.generate_demo_seed import build_dataset, render_sql


def test_demo_is_deterministic_and_clearly_synthetic():
    end = datetime(2026, 10, 20, 12, tzinfo=timezone.utc)
    data = build_dataset(end)
    assert data == build_dataset(end)
    assert len(data['parcels']) == 4
    assert len(data['sensors']) == 12
    assert len(data['evidence']) == 4 * 337 * 5
    assert len(data['knowledge']) == 24
    assert all(e['provenance']['source_type'] == 'SYNTHETIC' for e in data['evidence'])
    assert all(p['name'].startswith('DEMO -') for p in data['parcels'])
    assert all(0.10 <= e['value']['soil_moisture'] <= .45 for e in data['evidence'] if e['variable'] == 'soil_water_state')
    sql = render_sql(data)
    assert 'ON CONFLICT' in sql
    assert 'DELETE FROM' not in sql and 'TRUNCATE' not in sql and 'UPDATE users' not in sql
    assert 'password_hash' not in sql


def test_publication_includes_canonical_soil_moisture():
    from services.publication_service import PublicationService
    report = {'evidence': [{'variable':'soil_water_state','value':{'soil_moisture':.245}, 'unit':'m3/m3', 'observed_at':'2026-10-20T12:00:00+00:00'}]}
    figures = PublicationService().describe(report)['figures']
    assert figures[0]['points'][0]['value'] == .245


def test_fixed_seed_batch_has_frozen_timestamp():
    from scripts.generate_demo_seed import DEFAULT_END
    import json
    from pathlib import Path
    snapshot=json.loads(Path('artifacts/demo_publicacion/demo_dataset.json').read_text(encoding='utf-8'))
    assert datetime.fromisoformat(snapshot['end']) == DEFAULT_END

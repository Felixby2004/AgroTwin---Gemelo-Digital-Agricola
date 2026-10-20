import { useEffect, useState } from 'react';
import { useAuth } from '../../auth/AuthContext';
import { api } from '../../api/client';
import { saveFile } from './exportUtils';
import './publication.css';

interface FigureInfo { id: string; title: string; interpretation: string; explanation: string; limitations: string; points: { time: string; value: number }[] }

function EvidenceFigure({ figure }: { figure: FigureInfo }) {
  const values = figure.points.map(p => p.value);
  const min = Math.min(...values), max = Math.max(...values);
  const times = figure.points.map(p => Date.parse(p.time));
  const start = Math.min(...times), end = Math.max(...times);
  const coords = figure.points.map((p, i) => `${55 + (times[i] - start) / (end - start || 1) * 360},${155 - (p.value - min) / (max - min || 1) * 110}`);
  return <svg viewBox="0 0 460 215" role="img" aria-label={figure.title} data-interpretation={figure.interpretation} data-explanation={`${figure.explanation} ${figure.limitations}`} style={{ width: '100%', maxWidth: 600, background: 'white' }}>
    <title>{figure.title}</title><desc>{figure.interpretation} {figure.explanation} {figure.limitations}</desc>
    <text x="55" y="18" fill="#222" fontSize="12">{figure.title}</text>
    <path d="M55 35V160H420" fill="none" stroke="#555" />
    <text x="4" y="48" fill="#222" fontSize="11">{max.toPrecision(4)}</text>
    <text x="4" y="158" fill="#222" fontSize="11">{min.toPrecision(4)}</text>
    <polyline points={coords.join(' ')} stroke="#126b80" strokeWidth="2" fill="none" />
    {coords.map((point, i) => { const [cx, cy] = point.split(','); return <circle key={i} cx={cx} cy={cy} r="3" fill="#126b80"><title>{figure.points[i].time}: {figure.points[i].value}</title></circle>; })}
    <text x="55" y="185" fill="#222" fontSize="10">{figure.points[0]?.time.slice(0, 10)}</text>
    <text x="350" y="185" fill="#222" fontSize="10">{figure.points.at(-1)?.time.slice(0, 10)}</text>
    <text x="170" y="205" fill="#222" fontSize="11">Fecha de observación (UTC)</text>
  </svg>;
}

function ParcelPublicationPanel({ parcelId }: { parcelId: string }) {
  const [figures, setFigures] = useState<FigureInfo[]>([]);
  const [width, setWidth] = useState(85);
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(true);
  useEffect(() => {
    const controller = new AbortController();
    api.get(`/reports/parcels/${encodeURIComponent(parcelId)}/publication`, { signal: controller.signal })
      .then(response => setFigures(response.data.figures))
      .catch(() => { if (!controller.signal.aborted) setError('No se pudo cargar la información científica.'); })
      .finally(() => { if (!controller.signal.aborted) setLoading(false); });
    return () => controller.abort();
  }, [parcelId]);
  async function download() {
    setBusy(true); setError('');
    try {
      const response = await api.get(`/reports/parcels/${encodeURIComponent(parcelId)}/publication.zip`, { params: { width_mm: width }, responseType: 'blob' });
      saveFile(response.data, 'agritwin-publicacion.zip');
    } catch { setError('No se pudo exportar. Verifica la conexión, los permisos y el consentimiento de exportación de la parcela.'); }
    finally { setBusy(false); }
  }
  return <section className="publication-panel">
    <h2>Publicación científica · ADMIN</h2>
    <p>Figuras para una columna de revista: 85 mm como referencia. Ajusta el ancho según sus normas. SVG y PDF vectoriales, PNG a 600 dpi, tablas CSV/Excel y notas con interpretación, método y limitaciones.</p>
    <label>Ancho (mm) <input type="number" min={60} max={180} value={width} onChange={e => setWidth(Number(e.target.value))} /></label>
    <button disabled={busy || loading || width < 60 || width > 180} onClick={() => void download()}>{busy ? 'Generando…' : 'Descargar paquete científico ZIP'}</button>
    {error && <p role="alert">{error}</p>}
    {loading ? <p>Cargando evidencias…</p> : figures.length === 0 ? <p>Sin evidencias numéricas con fecha válida para graficar. El paquete conserva las tablas disponibles.</p> : figures.map(figure => <article className="publication-figure" key={figure.id}>
      <h3>{figure.title}</h3><EvidenceFigure figure={figure} />
      <p><b>Interpretación:</b> {figure.interpretation}</p>
      <p><b>Explicación:</b> {figure.explanation}</p>
      <p><b>Limitaciones:</b> {figure.limitations}</p>
    </article>)}
    <p>Inserta la figura vectorial o el PNG al ancho elegido y utiliza captions.txt para el pie y las notas. Las tablas de tables.xlsx son editables. El formato exacto y la sustitución dentro del manuscrito requieren las normas y el archivo del artículo.</p>
  </section>;
}

export function PublicationPanel({ parcelId }: { parcelId: string }) {
  const { user } = useAuth();
  if (user?.system_role !== 'ADMIN' || !parcelId) return null;
  return <ParcelPublicationPanel key={parcelId} parcelId={parcelId} />;
}

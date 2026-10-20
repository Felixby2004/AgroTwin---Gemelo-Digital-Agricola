import { useEffect, useState } from 'react';
import { createPortal } from 'react-dom';
import { useAuth } from '../../auth/AuthContext';
import { exportPNG, saveFile, scientificSVG, tableCSV } from './exportUtils';
import './publication.css';

type Target = HTMLTableElement | SVGSVGElement;

function Controls({ target }: { target: Target }) {
  const [width, setWidth] = useState(85);
  const [error, setError] = useState('');
  const [busy, setBusy] = useState(false);
  const isTable = target instanceof HTMLTableElement;
  const headers = isTable ? Array.from(target.rows[0]?.cells || []).map(c => c.textContent?.trim()).join(', ') : '';
  const count = isTable ? Math.max(0, target.rows.length - 1) : 0;
  const title = isTable ? `Tabla: ${headers}` : target.getAttribute('aria-label') || 'Figura AgriTwin';
  const note = target.closest('.ml-history-chart')?.querySelector('.ml-history-chart-note')?.textContent?.trim() || '';
  const interpretation = target.getAttribute('data-interpretation') || (isTable
    ? `${count} filas visibles. Columnas: ${headers}. Cada fila representa un registro; los valores ausentes no equivalen a cero.`
    : 'La línea continua representa humedad observada; el tramo de pronóstico, si está disponible, muestra la estimación complementaria a 24 h. Compare la evolución y la amplitud del intervalo P10–P90.');
  const explanation = target.getAttribute('data-explanation') || (isTable
    ? 'Se exportan las celdas visibles, sin controles de acciones. La tabla conserva el orden y los filtros actuales; no representa necesariamente todos los registros de la base de datos.'
    : `Fuente: histórico persistido y pronóstico RF complementario. P10–P90 describe la dispersión del pronóstico, no demuestra causalidad ni garantiza el valor futuro. ${note}`);
  const caption = `${title}\nInterpretación: ${interpretation}\nExplicación: ${explanation}`;

  async function download(format: 'svg' | 'png' | 'csv' | 'html' | 'txt') {
    setError(''); setBusy(true);
    try {
      if (format === 'txt') { saveFile(new Blob([caption], { type: 'text/plain;charset=utf-8' }), 'agritwin-notas.txt'); return; }
      if (isTable) {
        if (format === 'csv') saveFile(new Blob([tableCSV(target)], { type: 'text/csv;charset=utf-8' }), 'agritwin-tabla.csv');
        else {
          const clone = target.cloneNode(true) as HTMLTableElement;
          clone.querySelectorAll('button,input,select').forEach(node => node.remove());
          const doc = document.implementation.createHTMLDocument(title);
          const style = doc.createElement('style');
          style.textContent = `body{font:8pt Arial;width:${width}mm;margin:10mm}table{border-collapse:collapse;width:100%;table-layout:fixed}th,td{border-bottom:1px solid #999;padding:3px;overflow-wrap:anywhere}p{white-space:pre-wrap}`;
          doc.head.append(style);
          const p = doc.createElement('p'); p.textContent = caption;
          doc.body.append(clone, p);
          saveFile(new Blob(['<!doctype html>' + doc.documentElement.outerHTML], { type: 'text/html;charset=utf-8' }), 'agritwin-tabla.html');
        }
      } else {
        const svg = scientificSVG(target, width, caption);
        saveFile(format === 'png' ? await exportPNG(svg.text, width, svg.ratio) : new Blob([svg.text], { type: 'image/svg+xml' }), `agritwin-figura.${format}`);
      }
    } catch (e) { setError(e instanceof Error ? e.message : 'Error de exportación.'); }
    finally { setBusy(false); }
  }

  return <aside className="publication-controls" aria-label="Publicación científica ADMIN">
    <strong>Publicación científica · ADMIN</strong>
    <p><b>Interpretación:</b> {interpretation}</p>
    <p><b>Explicación:</b> {explanation}</p>
    <label>Ancho de columna <select value={width} onChange={e => setWidth(Number(e.target.value))}>
      <option value={85}>85 mm · una columna</option><option value={90}>90 mm</option><option value={180}>180 mm · dos columnas</option>
    </select></label>
    <div className="publication-actions">{(isTable ? ['csv', 'html', 'txt'] as const : ['svg', 'png', 'txt'] as const).map(format =>
      <button key={format} disabled={busy} onClick={() => void download(format)}>{format === 'png' ? 'PNG · 600 dpi' : format === 'html' ? 'Tabla editable / imprimir' : format === 'txt' ? 'Notas explicativas' : format.toUpperCase()}</button>)}</div>
    {error && <p role="alert">{error}</p>}
  </aside>;
}

// Attach to actual data tables and labelled figures, excluding decorative icons.
export function AdminPublicationTools() {
  const { user } = useAuth();
  const [targets, setTargets] = useState<{ target: Target; slot: HTMLElement }[]>([]);
  useEffect(() => {
    if (user?.system_role !== 'ADMIN') return;
    const slots = new Map<Target, HTMLElement>();
    const scan = (refresh = false) => {
      let changed = false;
      for (const [target, slot] of slots) if (!target.isConnected) { slot.remove(); slots.delete(target); changed = true; }
      document.querySelectorAll<Target>('main table, main svg[role="img"]').forEach(target => {
        if (slots.has(target)) return;
        const slot = document.createElement('div');
        slot.className = 'publication-slot';
        target.parentNode?.insertBefore(slot, target.nextSibling);
        slots.set(target, slot); changed = true;
      });
      if (changed || refresh) setTargets(Array.from(slots, ([target, slot]) => ({ target, slot })));
    };
    scan();
    const observer = new MutationObserver(records => {
      if (records.some(r => !(r.target instanceof Element && r.target.closest('.publication-slot')))) scan(true);
    });
    observer.observe(document.querySelector('main') || document.body, { childList: true, subtree: true });
    return () => { observer.disconnect(); slots.forEach(slot => slot.remove()); };
  }, [user?.system_role]);
  if (user?.system_role !== 'ADMIN') return null;
  return <>{targets.map(({ target, slot }, i) => createPortal(<Controls target={target} />, slot, String(i)))}</>;
}

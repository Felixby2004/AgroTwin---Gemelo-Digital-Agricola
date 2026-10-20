"""Publication exports built from the same evidence as the parcel report."""
import csv
import json
import math
from collections import defaultdict
from datetime import datetime, timezone
from io import BytesIO, StringIO
from zipfile import ZipFile, ZIP_DEFLATED
from threading import Lock

from matplotlib.figure import Figure
from matplotlib.backends.backend_agg import FigureCanvasAgg
from openpyxl import Workbook

_RENDER_LOCK = Lock()


def safe_cell(value):
    if isinstance(value, (int, float, bool)):
        return value
    text = '' if value is None else str(value)
    return "'" + text if text.lstrip().startswith(('=', '+', '-', '@')) else text


class PublicationService:
    def describe(self, report):
        groups = defaultdict(list)
        for item in report.get('evidence', []):
            value = item.get('value')
            if item.get('variable') == 'soil_water_state' and isinstance(value, dict):
                value = value.get('soil_moisture')
            elif isinstance(value, dict) and set(value) == {'value'}:
                value = value['value']
            if isinstance(value, bool) or not isinstance(value, (int, float)) or not math.isfinite(value):
                continue
            try:
                timestamp = datetime.fromisoformat(str(item.get('observed_at')).replace('Z', '+00:00'))
            except (ValueError, TypeError):
                continue
            timestamp = timestamp.replace(tzinfo=timezone.utc) if timestamp.tzinfo is None else timestamp.astimezone(timezone.utc)
            groups[(str(item.get('variable', 'Variable')), str(item.get('unit') or 'sin unidad'))].append((timestamp, value, item))
        figures = []
        for (variable, unit), points in groups.items():
            points.sort(key=lambda point: point[0].timestamp())
            values = [point[1] for point in points]
            figures.append({
                'id': f'figure-{len(figures) + 1}', 'title': f'{variable} ({unit})',
                'variable': variable, 'unit': unit, 'count': len(points),
                'points': [{'time': p[0].isoformat(), 'value': p[1]} for p in points],
                'interpretation': f'{len(points)} observaciones. Mínimo {min(values):.4g}; máximo {max(values):.4g}; primera {values[0]:.4g}; última {values[-1]:.4g} {unit}.',
                'explanation': 'Serie de evidencias registradas, ordenadas por fecha. Se separan variables y unidades; no se interpolan ni normalizan valores. Fuente: registro de evidencias de AgriTwin.',
                'limitations': 'Descripción de datos, no inferencia causal ni validación del modelo. Incluye estados históricos; revisar calidad, vigencia y procedencia en la tabla. Los valores ausentes, no numéricos y fechas inválidas se excluyen del gráfico. No se estima incertidumbre adicional.',
            })
        return {'parcel_id': report.get('parcel_id'), 'generated_at': str(report.get('generated_at')), 'figures': figures}

    def generate(self, report, width_mm=85):
        if not 60 <= width_mm <= 180:
            raise ValueError('El ancho debe estar entre 60 y 180 mm.')
        metadata = self.describe(report)
        metadata.update(width_mm=width_mm, dpi=600, font='DejaVu Sans', font_pt=8)
        output = BytesIO()
        columns = ['variable', 'value', 'unit', 'observed_at', 'status', 'quality_score', 'uncertainty', 'provenance']
        captions = ['AgriTwin — figuras y tablas para publicación', f"Parcela: {metadata['parcel_id']}. Generado: {metadata['generated_at']}.",
                    'Tabla 1. Evidencias registradas. Cada fila conserva valor, unidad, fecha, estado, calidad, incertidumbre y procedencia; celdas vacías indican datos no disponibles. No mezclar unidades ni interpretar ausencia como cero.']
        workbook = Workbook()
        sheet = workbook.active
        sheet.title = 'Evidencias'
        sheet.append(columns)
        csv_buffer = StringIO(newline='')
        writer = csv.writer(csv_buffer)
        writer.writerow(columns)
        for item in report.get('evidence', []):
            row = [safe_cell(json.dumps(item.get(c), ensure_ascii=False, default=str) if isinstance(item.get(c), (dict, list)) else item.get(c)) for c in columns]
            writer.writerow(row)
            sheet.append(row)
        sheet.freeze_panes = 'A2'
        sheet.auto_filter.ref = sheet.dimensions
        for column in sheet.columns:
            sheet.column_dimensions[column[0].column_letter].width = 23
        notes = workbook.create_sheet('Interpretación')
        notes.append(['Elemento', 'Interpretación', 'Explicación', 'Limitaciones'])
        notes.append(['Tabla 1', captions[-1], 'Registro original de evidencias; sin agregaciones.', 'Los datos pueden contener estados históricos y calidad variable.'])
        with ZipFile(output, 'w', ZIP_DEFLATED) as archive:
            for index, item in enumerate(metadata['figures'], 1):
                caption = f"Figura {index}. {item['title']}. {item['interpretation']} {item['explanation']} {item['limitations']}"
                captions.append(caption)
                notes.append([safe_cell(item['title']), item['interpretation'], item['explanation'], item['limitations']])
                with _RENDER_LOCK:
                    fig = Figure(figsize=(width_mm / 25.4, width_mm / 25.4 * .78), layout='constrained')
                    FigureCanvasAgg(fig)
                    ax = fig.subplots()
                    dates = [datetime.fromisoformat(p['time']) for p in item['points']]
                    ax.plot(dates, [p['value'] for p in item['points']], color='#126b80', marker='o', markersize=3, linewidth=1)
                    ax.set_ylabel(item['unit'], fontsize=8)
                    ax.set_xlabel('Fecha de observación (UTC)', fontsize=8)
                    ax.tick_params(labelsize=7)
                    ax.grid(alpha=.2)
                    import matplotlib.dates as mdates
                    locator = mdates.AutoDateLocator(minticks=2, maxticks=4)
                    ax.xaxis.set_major_locator(locator)
                    ax.xaxis.set_major_formatter(mdates.ConciseDateFormatter(locator))
                    for fmt in ('svg', 'png', 'pdf'):
                        buffer = BytesIO()
                        fig.savefig(buffer, format=fmt, dpi=600, facecolor='white')
                        archive.writestr(f"{item['id']}.{fmt}", buffer.getvalue())
                    fig.clear()
            excel = BytesIO()
            workbook.save(excel)
            archive.writestr('tables.xlsx', excel.getvalue())
            archive.writestr('evidence.csv', '\ufeff' + csv_buffer.getvalue())
            archive.writestr('captions.txt', '\n\n'.join(captions))
            archive.writestr('manifest.json', json.dumps(metadata, ensure_ascii=False, indent=2))
        return output.getvalue()


def table_explanation(headers, count):
    """Describe the actual columns without inventing agronomic conclusions."""
    labels = ', '.join(str(value) for value in headers)
    text = (f'Interpretación: tabla con {count} filas de datos; columnas: {labels}. '
            'Cada fila corresponde a un registro o indicador del informe. '
            'Explicación: datos del reporte de parcela, sin inferencia causal. '
            'Los valores ausentes se muestran vacíos o con guion y no equivalen a cero. ')
    lower = labels.lower()
    if any(word in lower for word in ('quality', 'calidad', 'uncertainty', 'incertidumbre', 'evidencia', 'variable')):
        text += 'Verifique unidad, fecha, calidad y procedencia antes de comparar; calidad no equivale a probabilidad de acierto. '
    if any(word in lower for word in ('ml', 'predict', 'pron', 'confidence', 'confianza', 'irrigation', 'riego')):
        text += 'Las predicciones y recomendaciones dependen de los datos y supuestos del modelo; no son mediciones futuras ni garantías de resultado. '
    if any(word in lower for word in ('consent', 'audit', 'permiso', 'status', 'estado')):
        text += 'Los estados y permisos describen la situación registrada al generar el reporte, que puede cambiar posteriormente. '
    return text

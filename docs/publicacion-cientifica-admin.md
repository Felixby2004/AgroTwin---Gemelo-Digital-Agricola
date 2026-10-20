# Publicación científica para ADMIN

## Dónde probar

1. Reinicia el backend con `.venv\Scripts\python.exe -m uvicorn api.main:app --reload` desde la raíz del proyecto. Mantén la configuración habitual de base de datos y servicios.
2. Desde `digital_twin_frontend`, ejecuta `npm run dev` y abre la dirección que indique Vite. Conserva tu `VITE_API_URL` habitual.
3. Inicia sesión con un usuario cuyo `system_role` sea `ADMIN`.
4. En **Reportes**, selecciona una parcela con evidencias numéricas fechadas. Aparece **Publicación científica · ADMIN**.
5. Revisa las figuras, su interpretación, explicación y limitaciones. Se separan por variable y unidad. Los estados históricos se conservan; comprueba estado y calidad antes de publicar.
6. Deja **85 mm** para una columna de revista, o cambia el ancho entre 60 y 180 mm. Descarga **paquete científico ZIP**. Requiere permiso de exportación y consentimiento vigente de la parcela, igual que los reportes existentes.
7. Descomprime: `figure-N.svg`, `figure-N.pdf`, `figure-N.png`, `evidence.csv`, `tables.xlsx`, `captions.txt`, `manifest.json`. El PNG contiene 600 dpi y mide aproximadamente 2008 píxeles de ancho a 85 mm. SVG/PDF son vectoriales. Excel conserva los valores numéricos.
8. En **detalle de parcela / histórico de humedad**, y en el pronóstico complementario cuando tiene histórico, revisa los controles bajo el gráfico: SVG, PNG a 600 dpi y notas TXT.
9. En **Sensores / detalle / historial de lecturas** y **Usuarios**, las tablas tienen controles CSV, tabla HTML editable e imprimible y notas TXT. Se exportan las filas visibles. Abre el HTML para imprimirlo o copiar la tabla a Word; descarga también las notas para acompañar el CSV.
10. En **Reportes**, descarga los reportes habituales PDF, Word y Excel: las tablas incorporan interpretación y explicación cuando los solicita un ADMIN. La vista previa PDF también las incluye.
11. Repite con otro rol: los controles científicos deben desaparecer. Las rutas nuevas deben rechazarlo con HTTP 403.
12. Comprueba una parcela sin evidencias: debe avisar que no hay series válidas y permitir guardar las tablas disponibles si la política de exportación lo permite.

## Uso en el artículo

85 mm es una referencia estimada a partir de la imagen facilitada, no una norma verificada de la revista. Inserta SVG o PDF vectorial si el editor lo admite; usa PNG a 600 dpi en caso contrario. Fija el ancho de inserción al ancho elegido, conserva la relación de aspecto y añade el pie de `captions.txt`. Copia las tablas editables desde Excel o HTML y aplica el estilo de la revista. El paquete usa fuentes de 8 puntos para ejes y 7 para marcas, ajustables posteriormente en el SVG.

La aplicación genera resultados de la parcela; no inventa las métricas de validación del artículo de ejemplo ni modifica automáticamente el manuscrito. Para una sustitución exacta se necesita el archivo del artículo y las normas editoriales.

Los controles cubren gráficos de datos SVG y tablas HTML de la aplicación; las vistas cartográficas y el gemelo 3D no se convierten en figuras científicas mediante estos controles.

## Rutas y archivos

- `GET /reports/parcels/{parcel_id}/publication`: series y explicaciones, solo ADMIN y permiso VIEW.
- `GET /reports/parcels/{parcel_id}/publication.zip?width_mm=85`: paquete, solo ADMIN, permiso EXPORT_DATA y consentimiento.
- Backend: `services/publication_service.py`, `api/routers/reports.py` y los tres servicios `report_*_service.py`.
- Frontend: `digital_twin_frontend/src/components/publication/`, integrado desde `Layout.tsx` y `ReportsPage.tsx`.

## Verificación automatizada

Desde la raíz: `.venv\Scripts\python.exe -m pytest tests/test_publication.py tests/test_report_generation.py -q`.
Desde frontend: `npm run build`, `npx eslint src/components/publication` y `node --test tests/publication-export.test.cjs`. Las pruebas del frontend comprueban columnas CSV, metadatos PNG únicos y dimensiones/tamaño mínimo de letra SVG.
Las pruebas cubren dimensiones y metadatos PNG, archivos vectoriales, unidades separadas, datos ausentes, números Excel, escape de fórmulas, permisos, consentimiento y notas en reportes. No requieren la base de datos real.

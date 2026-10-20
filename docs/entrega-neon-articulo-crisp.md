# Entrega de datos simulados y artículo CRISP DM

Se completó la carga autorizada en Neon el 20 de octubre de 2026. El lote es `AGROTWIN-DEMO-20261020-V1` y su cierre horario es 2026-10-20 13:00 UTC (08:00, Lima). El SQL conserva las cuentas existentes y usa `ON CONFLICT DO NOTHING`; no borra datos ni cambia contraseñas.

Conteos: 4 parcelas, 20 membresías, 12 sensores, 6740 evidencias horarias de 14 días, 24 aportes de conocimiento, 4 trazas calculadas por el motor, 4 políticas de consentimiento para datos ficticios y 4 eventos de carga. Todos los registros demostrativos tienen identificadores `DEMO26-…` y procedencia sintética. Las parcelas aparecen como `DEMO - … (simulado)`.

Cultivos: maíz, cebolla, palta y papa. Cebolla, palta y papa conservan su condición experimental en el catálogo del software. Los escenarios de las trazas proceden de `ExperimentalCaseFactory.COMPLETE`, como el flujo actual de razonamiento de la aplicación: no son resultados calibrados a esos cultivos ni ensayos de campo.

## Cómo comprobarlo en la aplicación

1. Ingresa con el ADMIN habitual y recarga **Parcelas**. Deben aparecer cuatro parcelas con prefijo DEMO.
2. Abre una parcela y revisa mapa, sensores, histórico, conocimiento del agricultor, miembros y trazas.
3. Revisa **Reportes** para la parcela seleccionada. Las funciones de exportación añadidas al software necesitan que el backend y el frontend se desplieguen con los cambios locales de esta conversación; la carga de datos de Neon ya está aplicada.
4. El laboratorio de evaluación científica se encuentra en `app_streamlit`, pestaña **CRISP-DM**. Utiliza los datos NOAA y sus artefactos guardados, independientemente del dataset demostrativo de Neon.

## Archivos finales

- `artifacts/AgroTwin_ESPANOL_CRISP_DM_actualizado.docx`: Word de once páginas, con estructura y referencias originales conservadas.
- `artifacts/demo_publicacion/seed_demo_agrotwin.sql`: SQL efectivamente aplicado y reutilizable.
- `artifacts/demo_publicacion/demo_dataset.json`: snapshot exacto de la carga.
- `artifacts/demo_publicacion/neon_seed_receipt.json`: comprobante de conteos y huella del SQL, sin credenciales.
- `artifacts/AgroTwin_figuras_CRISP_DM.zip`: PNG a 600 dpi y 85 mm, SVG y PDF vectoriales, tablas CSV y manifiesto con procedencia.

## Cambios del artículo

Se reemplazaron las figuras 4 y 5 con salidas regeneradas de comparación de modelos y bootstrap. Se añadieron la figura 6 (serie observada y predicha de 2025), figura 7 (permutación), figura 8 (SHAP global) y una tabla VI SHAP local editable. La antigua figura 6 pasa a 9 y la tabla VI sintética a VII. Se añadieron interpretación, método y límites en los pies. Se mantuvieron las figuras de arquitectura y de estabilidad sintética que no pertenecen al laboratorio CRISP-DM.

Las figuras CRISP-DM proceden de las funciones `ml.reporting` utilizadas en `app_streamlit.crisp_dm_panel`, con el modelo guardado y los datos NOAA existentes. Permutación se recalculó con 3000 observaciones, 10 repeticiones y semilla 42; SHAP con 500 observaciones reservadas de 2025 y semilla 42. Se conservaron el entrenamiento y las particiones originales. Los datos ficticios de Neon no se utilizaron para las métricas del manuscrito.

## Configuración

`DATABASE_URL` del `.env` raíz quedó apuntando a la conexión Neon proporcionada. El archivo sigue excluido de Git. `VITE_API_URL`, en la configuración del frontend, debe seguir apuntando a la URL pública del backend; nunca a PostgreSQL. No se requieren cambios en las claves de JWT, NASA, Copernicus ni Langflow para usar este lote.

## Reproducción

- Validar sin guardar: `.venv\Scripts\python.exe scripts/apply_demo_seed.py`. Por defecto usa una transacción con `rollback()` y comprueba los datos frente al snapshot.
- Reaplicar sin duplicar: `.venv\Scripts\python.exe scripts/apply_demo_seed.py --apply`.
- `scripts/generate_demo_seed.py` reutiliza el snapshot congelado y no lo sobrescribe con nuevas fechas.
- Recalcular los gráficos desde los artefactos reales: `.venv\Scripts\python.exe scripts/export_crisp_publication.py`. `--reuse-xai` reutiliza las tablas de permutación/SHAP ya calculadas.
- Pruebas: `.venv\Scripts\python.exe -m pytest tests/test_demo_seed.py tests/test_publication.py tests/test_report_generation.py -q`.

El documento original no se modificó. La revisión visual se realizó sobre las once páginas exportadas con Word instalado; los PDF y PNG de revisión son archivos internos y no forman parte de la entrega solicitada.

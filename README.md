# AgroTwin — Gemelo Digital Participativo para Agricultura de Precisión

AgroTwin es una plataforma de gemelo digital agrícola orientada al apoyo de decisiones de riego de precisión en parcelas de pequeña y mediana escala. Integra sensores IoT, información ambiental y edáfica, simulación agronómica, conocimiento contextual del agricultor, trazabilidad de decisiones, gobernanza de datos e inteligencia artificial explicable.

> **Principio arquitectónico:** el motor de inferencia y decisión constituye el núcleo de AgroTwin. El módulo de Machine Learning es complementario: predice humedad del suelo a +24 h, pero no modifica `TrustedState`, no selecciona directamente el riego y no tiene autoridad decisional.

---

## Funcionalidades

### Gestión de parcelas

- Creación y edición de parcelas.
- Delimitación geográfica mediante polígonos.
- Cálculo automático del área mediante PostGIS.
- Conversión automática a hectáreas.
- Vista Mapa, Terreno y Satélite.
- Membresías, roles y permisos por parcela.

### Sensores IoT

- Registro de sensores.
- Asignación a parcelas.
- Humedad del suelo.
- Temperatura del aire.
- Humedad relativa.
- Precipitación.
- Caudal.
- Historial de lecturas.
- Estado operacional.
- Integración como evidencia de máquina.

Un sensor recién registrado puede permanecer en estado `NO_DATA` hasta recibir una lectura real.

### Gemelo digital

- Estado dinámico de la parcela.
- Visualización territorial.
- Representación 3D.
- Capas agronómicas.
- Datos temporales.
- Evidencia ambiental y edáfica.
- Integración de sensores.

### Motor de inferencia y decisión

El núcleo decisional integra:

1. evidencia;
2. construcción de `TrustedState`;
3. calidad de evidencia;
4. conocimiento del agricultor;
5. detección de conflictos;
6. restricciones y preferencias;
7. simulación de escenarios;
8. evaluación agronómica;
9. ranking multicriterio;
10. recomendación;
11. `DecisionTrace`;
12. participación humana mediante `ACCEPT`, `MODIFY` y `REJECT`.

### Integraciones científicas

AgroTwin incorpora, según configuración:

- NASA POWER;
- SoilGrids;
- Copernicus / Sentinel-2;
- FAO-56 / ET0;
- propiedades hidráulicas del suelo;
- AquaCrop;
- simulación de escenarios de riego.

### Machine Learning complementario

El módulo predictivo se mantiene separado del motor de decisión.

El laboratorio CRISP-DM incluye:

- EDA;
- preparación;
- entrenamiento;
- selección de modelos;
- validación cruzada temporal;
- pruebas estadísticas;
- evaluación final;
- interpretabilidad;
- SHAP;
- reportes.

Dataset experimental:

- NOAA USCRN;
- estación `AZ_Yuma_27_ENE`;
- 2022–2025;
- horizonte +24 h.

Modelos evaluados:

- Ridge;
- Random Forest;
- Extra Trees;
- Hist Gradient Boosting;
- Persistence como benchmark.

Métricas y métodos:

- MAE;
- RMSE;
- R²;
- Friedman;
- Wilcoxon;
- Holm;
- Diebold-Mariano;
- bootstrap por bloques;
- análisis de residuos;
- Permutation Importance;
- SHAP.

---

## Arquitectura

```text
React Frontend
      │
      ▼
FastAPI
      │
      ├──────── Motor de inferencia y decisión
      │         ├─ TrustedState
      │         ├─ restricciones
      │         ├─ escenarios
      │         ├─ recomendación
      │         └─ HITL
      │
      ├──────── ML complementario
      │         └─ predicción +24 h / CRISP-DM / XAI
      │
      ├──────── Servicios externos
      │         ├─ NASA POWER
      │         ├─ SoilGrids
      │         └─ Copernicus
      │
      ▼
PostgreSQL + PostGIS

Streamlit
└─ Laboratorio del Motor IA / CRISP-DM
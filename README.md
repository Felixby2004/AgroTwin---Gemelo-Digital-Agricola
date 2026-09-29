Guion de exposición con demostración del sistema — AgroTwin

Duración total sugerida: 5 minutos aprox.
Enfoque: introducción breve + recorrido por módulos del sistema

1. Introducción rápida — 30 a 40 segundos

Buenos días. Mi proyecto se llama AgroTwin, un gemelo digital agrícola participativo orientado al manejo de riego de precisión.

La idea principal es representar digitalmente el estado de una parcela y combinar información del suelo, clima, sensores, datos satelitales, modelos científicos, Machine Learning y conocimiento del agricultor para generar recomendaciones de riego explicables y trazables.

La arquitectura se divide en cuatro bloques: un frontend en React, un backend en FastAPI, una base de datos PostgreSQL con PostGIS y un motor científico e IA.

La lógica central del sistema es:

el ML predice, el motor científico evalúa, el motor de decisión recomienda y el agricultor participa.

A partir de aquí, voy a mostrar directamente cómo está organizado el sistema.

2. Vista General / Dashboard — 30 a 40 segundos

En la Vista General se resume el estado del sistema.

Aquí se muestran indicadores principales de las parcelas, estado del gemelo digital, nivel de riesgo y recomendación actual.

La idea de esta vista es que el usuario pueda saber rápidamente si una parcela está estable, si existen alertas o si hay una recomendación pendiente.

También sirve como punto de entrada al resto de módulos.

3. Mapa de Parcelas — 30 a 40 segundos

En la vista de Parcelas se visualizan las parcelas registradas y su información principal.

El sistema utiliza PostGIS para almacenar la geometría real de cada parcela.

Desde esta sección se puede crear o editar la geometría del terreno directamente en el mapa.

Cada parcela puede tener su propio cultivo, área, ubicación y estado digital asociado.

Al ingresar a una parcela se accede a su gemelo digital detallado.

4. Detalle de parcela / Gemelo Digital — 50 a 60 segundos

Esta es una de las vistas principales del sistema.

Aquí se presenta el TwinState, es decir, el estado digital actual de la parcela.

Se muestran variables como:

humedad del suelo;

temperatura;

NDVI;

NDMI;

calidad y confianza de los datos;

nivel de riesgo;

recomendación de riego.

También existe una representación 3D de la parcela, que permite visualizar el estado del gemelo digital de forma más intuitiva.

En esta misma vista se integra la recomendación de riego y la explicación de por qué fue generada.

La recomendación no se basa únicamente en una predicción, sino en escenarios, restricciones, evidencia y criterios técnicos.

5. Motor de recomendación y conocimiento del agricultor — 45 a 55 segundos

Dentro del detalle de la parcela también se encuentra la parte participativa.

El agricultor puede registrar:

observaciones;

eventos;

restricciones;

preferencias;

conocimiento local.

Esta información no reemplaza directamente los datos del sistema.

Por ejemplo, una restricción como “máximo 20 milímetros de riego” puede limitar los escenarios que el motor considera válidos.

El usuario también puede interactuar con una recomendación mediante:

aceptar, modificar o rechazar.

Esto corresponde al enfoque Human-in-the-Loop.

6. Sensores — 25 a 35 segundos

En el módulo de Sensores se registran los dispositivos físicos asociados a las parcelas.

Aquí se puede consultar:

tipo de sensor;

estado;

ubicación o parcela asociada;

historial de lecturas;

variables medidas.

Los sensores funcionan como una de las fuentes de evidencia que alimentan el gemelo digital.

7. Predicción con Machine Learning — 30 a 40 segundos

El sistema también incluye un modelo de Random Forest para predicción de humedad del suelo.

Este modelo es complementario y no reemplaza al motor científico.

La predicción incluye además un rango de incertidumbre mediante valores P10 y P90.

También se utiliza SHAP para explicar qué variables influyeron más en la predicción.

La idea es separar claramente:

predicción de decisión.

8. Gobernanza y trazabilidad — 25 a 35 segundos

En la sección de Gobernanza se gestiona la parte relacionada con procedencia, consentimiento, acceso y soberanía de los datos.

El sistema registra de dónde provienen los datos y cómo fueron utilizados.

Esto permite mantener trazabilidad y transparencia dentro del proceso de decisión.

9. Reportes — 20 a 30 segundos

En el módulo de Reportes se pueden generar salidas del sistema en distintos formatos.

Se han trabajado reportes en:

PDF;

Word;

Excel.

También existe una vista previa para revisar el contenido antes de exportarlo.

10. Usuarios, roles y perfiles — 25 a 35 segundos

El sistema también incorpora autenticación y control de acceso.

A nivel global existen los roles:

ADMIN y USER.

Y dentro de cada parcela existen roles como:

OWNER, FARMER, AGRONOMIST y VIEWER.

Cada rol posee permisos diferentes para ver, editar, ejecutar razonamiento, responder recomendaciones, exportar datos o gestionar miembros.

También existe una vista de perfil personal y gestión de usuarios.

11. Glosario y ayudas — 15 a 20 segundos

El sistema cuenta además con un Glosario y diferentes ayudas contextuales.

Esto permite explicar términos técnicos como NDVI, NDMI, confianza, riesgo o recomendación sin obligar al usuario a conocer previamente todos los conceptos.

12. Streamlit — Laboratorio del motor IA — 35 a 45 segundos

Finalmente, utilizo Streamlit como laboratorio para mostrar cómo funciona internamente el motor.

Aquí se pueden configurar variables del cultivo, suelo y clima, ejecutar diferentes escenarios de riego y observar cómo cambian:

el estrés hídrico;

la humedad final;

el drenaje;

la recomendación.

También se muestran las razones de la decisión y la procedencia de los datos.

Esta vista es útil principalmente para demostrar la lógica del motor y validar que el comportamiento sea coherente.

13. Cierre — 15 a 20 segundos

En resumen, AgroTwin no busca ser solo un sistema de predicción.

Busca integrar datos, modelos científicos, Machine Learning, conocimiento del agricultor, explicabilidad y participación humana dentro de un mismo gemelo digital.

La idea central se resume así:

El ML predice. El motor científico evalúa. El motor de decisión recomienda. Y el agricultor participa.
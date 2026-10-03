# Primera entrega del proyecto de Nueva York

**Fecha límite:** 2 de octubre de 2026. **Corte del trabajo:** 30 de septiembre de 2026 (hora de Bogotá).

## Archivos

- `Informe_primera_entrega_NYC.pdf`: informe de 9 páginas para lectura.
- `Informe_primera_entrega_NYC.docx`: versión editable.
- `Exploracion_NYC_PySpark.ipynb`: diez bloques ejecutados de exploración, calidad y transformaciones.
- `Presentacion_ejecutiva_NYC.pptx`: diez diapositivas, con notas para unos 15 minutos.
- `datos/`: extractos JSON Lines, metadatos y `manifest.json` con recuentos del API, fecha de consulta y SHA-256.

## Cómo ejecutar el notebook

Abra el notebook desde esta carpeta y ejecute las celdas en orden en un entorno con PySpark 4.x y Java compatible. El notebook busca `datos/` desde esta carpeta y también acepta ejecutarse desde el directorio superior del proyecto. No requiere un clúster específico. Los resultados guardados en el notebook corresponden a una ejecución local de los extractos entregados.

Los extractos ordenados por identificador **no son muestras aleatorias**: 10 000 arrestos, 3 000 registros de vehículos, 3 000 registros de pobreza y las 478 filas de SAT 2012 disponibles. Los recuentos del API son valores observados en el momento de descarga y pueden cambiar. No se deben extrapolar los resultados del extracto a toda la ciudad. El archivo de vehículos tiene una fila por vehículo; `collision_id` identifica el siniestro representado.

El informe SAT estatal 2024 se usó como contexto y se consulta en su [fuente oficial](https://reports.collegeboard.org/media/pdf/2024-new-york-sat-suite-of-assessments-annual-report-ADA.pdf). Su descarga automática devolvió 403; no se incluye copia local. Las otras fuentes se consultaron en [arrestos](https://data.cityofnewyork.us/Public-Safety/NYPD-Arrest-Data-Year-to-Date-/uip8-fykc/about_data), [pobreza](https://data.cityofnewyork.us/City-Government/NYCgov-Poverty-Measure-Data-2018-/cts7-vksw/about_data), [vehículos](https://data.cityofnewyork.us/Public-Safety/Motor-Vehicle-Collisions-Vehicles/bm4k-52h4/about_data) y [SAT 2012](https://data.cityofnewyork.us/Education/2012-SAT-Results/f9bf-2cp4/about_data).

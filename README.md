# Plan analítico para arrestos y seguridad vial en Nueva York

Primera entrega del proyecto de Big Data. Fecha límite: **2 de octubre de 2026, 23:59 (Bogotá)**.

## Entregables

- [Informe en PDF](Informe_primera_entrega_NYC.pdf): 16 páginas, incluidas portada, **nueve páginas de contenido**, referencias y anexos con el significado de los atributos.
- [Informe editable](Informe_primera_entrega_NYC.docx).
- [Notebook PySpark](Exploracion_NYC_PySpark.ipynb): diez elementos exploratorios, dos gráficas, revisión de calidad y transformaciones iniciales. Todas las celdas de código incluyen comentarios.
- [Presentación ejecutiva](Presentacion_ejecutiva_NYC.pptx): diez diapositivas con notas que suman aproximadamente 15 minutos.
- [Diccionario de atributos](Diccionario_atributos.csv): descripción y procedencia de los 111 campos de las cuatro tablas.
- [`datos/`](datos): extractos JSON Lines, metadatos, manifiesto de descarga y el diccionario adjunto oficial de pobreza.
- [`figuras/`](figuras): imágenes reproducibles creadas por el notebook.

## Reproducir el análisis en VS Code

1. Abra esta carpeta en VS Code y seleccione un intérprete de Python con las dependencias de [`requirements.txt`](requirements.txt).
2. Instale las dependencias con `python -m pip install -r requirements.txt` si aún no están disponibles. Se requiere una instalación de Java compatible con PySpark.
3. Abra `Exploracion_NYC_PySpark.ipynb` y ejecute las celdas en orden desde la raíz del repositorio.
4. Compare los archivos con los SHA-256 del [`manifest.json`](datos/manifest.json) antes de interpretar las salidas.

La ejecución comprobada se hizo en **Spark 4.0.1, modo `local[*]`, paralelismo informado de 16, Python 3.12.14 y Java 22**. La memoria del driver no se configuró explícitamente. La primera celda imprime las propiedades de cada nueva sesión. Esas características describen la ejecución local de los extractos y no un clúster remoto.

## Alcance de los datos

Los cuatro archivos obligatorios son [arrestos](https://data.cityofnewyork.us/Public-Safety/NYPD-Arrest-Data-Year-to-Date-/uip8-fykc/about_data), [pobreza 2018](https://data.cityofnewyork.us/City-Government/NYCgov-Poverty-Measure-Data-2018-/cts7-vksw/about_data), [vehículos implicados en colisiones](https://data.cityofnewyork.us/Public-Safety/Motor-Vehicle-Collisions-Vehicles/bm4k-52h4/about_data) y [SAT 2012](https://data.cityofnewyork.us/Education/2012-SAT-Results/f9bf-2cp4/about_data). El [informe SAT estatal 2024](https://reports.collegeboard.org/media/pdf/2024-new-york-sat-suite-of-assessments-annual-report-ADA.pdf) se usa como contexto y no como microdatos de escuelas de la ciudad.

Los extractos disponibles contienen 10 000 arrestos, 3 000 vehículos, 3 000 registros de pobreza y 478 escuelas. Fueron ordenados por identificador interno y **no son muestras aleatorias**; los resultados del notebook no se extrapolan a toda Nueva York. Vehicles contiene una fila por vehículo. El total de siniestros requiere contar `collision_id` distintos y, para geografía y lesiones, incorporar la tabla *Crashes* en una fase posterior.

El informe plantea ocho preguntas de negocio para la entrega final **sin responderlas todavía**, conforme a la consigna. Las intervenciones son propuestas sujetas a validación con datos completos.

# Plan analítico para arrestos y seguridad vial en Nueva York
![](https://images.seeklogo.com/logo-png/11/1/pontificia-universidad-javeriana-logo-png_seeklogo-110703.png)

Primera entrega del proyecto de Big Data. Fecha límite: **2 de octubre de 2026, 23:59 (Bogotá)**.

## Entregables

- [Informe en PDF](Informe_primera_entrega_NYC.pdf): 18 páginas, incluidas portada, **nueve páginas de contenido**, referencias, diccionario resumido y anexo del bono.
- [Informe editable](Informe_primera_entrega_NYC.docx).
- [Notebook PySpark](Exploracion_NYC_PySpark.ipynb): diez elementos exploratorios principales y el bono, cuatro gráficas, revisión de calidad y transformaciones iniciales. Todas las celdas de código incluyen comentarios.
- [Presentación ejecutiva](Presentacion_ejecutiva_NYC.pptx): doce diapositivas con notas que suman 15 minutos.
- [Diccionario de atributos](Diccionario_atributos.csv): descripción y procedencia de los 111 campos de las cuatro tablas.
- [`datos/`](datos): extractos JSON Lines, metadatos, manifiesto de descarga y el diccionario adjunto oficial de pobreza.
- [`figuras/`](figuras): imágenes reproducibles creadas por el notebook.
- [`scripts/bono_fuentes.py`](scripts/bono_fuentes.py): extracción de población del sitio actualizado del Departamento de Salud, consulta climática y dos gráficos del bono.

## Reproducir el análisis en VS Code

1. Abra esta carpeta en VS Code y seleccione un intérprete de Python con las dependencias de [`requirements.txt`](requirements.txt).
2. Instale las dependencias con `python -m pip install -r requirements.txt` si aún no están disponibles. Se requiere una instalación de Java compatible con PySpark.
3. Abra `Exploracion_NYC_PySpark.ipynb` y ejecute las celdas en orden desde la raíz del repositorio.
4. Compare los archivos con los SHA-256 del [`manifest.json`](datos/manifest.json) antes de interpretar las salidas.
5. Para actualizar el bono, ejecute `python scripts/bono_fuentes.py`. Este paso necesita acceso a Internet; actualiza las tablas, los gráficos y [`bono_manifest.json`](datos/bono_manifest.json). El notebook lee esas tablas con PySpark.

La ejecución comprobada se hizo en **Spark 4.0.1, modo `local[*]`, paralelismo informado de 16, Python 3.12.14 y Java 22**. La memoria del driver no se configuró explícitamente. La primera celda imprime las propiedades de cada nueva sesión. Esas características describen la ejecución local de los extractos y no un clúster remoto.

## Alcance de los datos

Los cuatro archivos obligatorios son [arrestos](https://data.cityofnewyork.us/Public-Safety/NYPD-Arrest-Data-Year-to-Date-/uip8-fykc/about_data), [pobreza 2018](https://data.cityofnewyork.us/City-Government/NYCgov-Poverty-Measure-Data-2018-/cts7-vksw/about_data), [vehículos implicados en colisiones](https://data.cityofnewyork.us/Public-Safety/Motor-Vehicle-Collisions-Vehicles/bm4k-52h4/about_data) y [SAT 2012](https://data.cityofnewyork.us/Education/2012-SAT-Results/f9bf-2cp4/about_data). El [informe SAT estatal 2024](https://reports.collegeboard.org/media/pdf/2024-new-york-sat-suite-of-assessments-annual-report-ADA.pdf) se usa como contexto y no como microdatos de escuelas de la ciudad.

Los extractos disponibles contienen 10 000 arrestos, 3 000 vehículos, 3 000 registros de pobreza y 478 escuelas. Fueron ordenados por identificador interno y **no son muestras aleatorias**; los resultados del notebook no se extrapolan a toda Nueva York. Vehicles contiene una fila por vehículo. El total de siniestros requiere contar `collision_id` distintos y, para geografía y lesiones, incorporar la tabla *Crashes* en una fase posterior.

El informe plantea ocho preguntas de negocio para la entrega final **sin responderlas todavía**, conforme a la consigna. Las intervenciones son propuestas sujetas a validación con datos completos.

## Estado del bono

El enlace de población `neighborhoodpop.htm` del PDF ya no está disponible. El extractor localizó el tablero incrustado en la [página vigente del Departamento de Salud](https://www.health.ny.gov/statistics/cancer/registry/population.htm) y obtuvo 195 filas. La [tabla de los cinco boroughs](datos/bono_poblacion_nyc.csv) y [su gráfico](figuras/bono_poblacion_nyc.png) corresponden a la población media anual **2019–2023**. El [manifiesto del bono](datos/bono_manifest.json) conserva la ruta de exportación y el hash del CSV original.
El primer bono que se mencionaba en los requerimientos del proyecto, el link no remitía a una página que funcionara, por ende hicimos el de arriba

La [gráfica climática](figuras/bono_clima_mensual.png) procede de una extracción **real** de 1 826 días de la [API histórica de Open-Meteo](https://open-meteo.com/en/docs/historical-weather-api), modelo ERA5, 2021–2025. El enlace del PDF a [OpenWeatherMap](https://openweathermap.org) requiere una clave para usar su API. El extractor incluye la consulta a Current Weather Data, pero **no se ejecutó** porque no hay clave configurada. Si se dispone de una, configure `OPENWEATHER_API_KEY` como variable de entorno y vuelva a ejecutar el script; la respuesta se guardará en `datos/bono_openweather_actual.csv`. Esa observación actual no reemplaza la serie climática histórica ni se atribuye a ella.

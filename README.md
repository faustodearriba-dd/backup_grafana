# Script para hacer backup completo a Grafana

## Requisitos

Definir un archivo .env con las siguientes variables:

GRAFANA_URL=
GRAFANA_TOKEN=

El archivo tiene que estar en la misma carpeta en donde está el script

## Ejecución

1. Generar el entorno virtual con:

python -m venv venv

2. Activar el entorno virtual con:

source venv/bin/activate

3. Instalar el requirements.txt con:

pip install -r requirements.txt

4. Ejecutar el script:

python main_csv.py (o python3 main_csv.py)

El script va a generar:

1. Archivo csv con los dashboards obtenidos
2. Carpeta ./backup/ con los JSON de todos los dashboards que consiguió
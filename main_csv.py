import os
import json
import csv
import requests
from dotenv import load_dotenv

def main():
    # Cargar las variables de entorno desde el archivo .env si existe
    load_dotenv()

    # 1. Obtener variables de entorno
    grafana_url = os.getenv("GRAFANA_URL")
    grafana_token = os.getenv("GRAFANA_TOKEN")

    # Validaciones iniciales de entorno
    if not all([grafana_url, grafana_token]):
        print("❌ Error: Faltan variables de entorno obligatorias.")
        print("Asegúrate de que el archivo .env exista y contenga:")
        print("  - GRAFANA_URL")
        print("  - GRAFANA_TOKEN")
        return

    # Normalizar la URL de Grafana
    grafana_url = grafana_url.rstrip("/")

    # 2. Configurar headers de autenticación para la API de Grafana
    headers = {
        "Authorization": f"Bearer {grafana_token}",
        "Content-Type": "application/json"
    }

    # 3. Crear el directorio de backups local si no existe
    dir_backups = "backups"
    os.makedirs(dir_backups, exist_ok=True)

    # 4. Obtener el listado de todos los dashboards de tipo DB en Grafana
    print("🔄 Buscando dashboards en Grafana...")
    search_url = f"{grafana_url}/api/search?type=dash-db"
    try:
        response = requests.get(search_url, headers=headers)
        response.raise_for_status()
        dashboards_summary = response.json()
    except Exception as e:
        print(f"❌ Error al consultar el listado de Grafana: {e}")
        return

    print(f"📊 Se encontraron {len(dashboards_summary)} dashboards. Iniciando procesamiento...")

    rows_to_write = []

    # 5. Recorrer cada dashboard para extraer detalles y guardar su JSON de backup
    for dash in dashboards_summary:
        uid = dash.get("uid")
        if not uid:
            continue

        dash_detail_url = f"{grafana_url}/api/dashboards/uid/{uid}"
        try:
            dash_resp = requests.get(dash_detail_url, headers=headers)
            if dash_resp.status_code != 200:
                print(f"⚠️ No se pudo obtener el detalle del dashboard UID {uid}. Status: {dash_resp.status_code}")
                continue

            dash_data = dash_resp.json()
            meta = dash_data.get("meta", {})
            dashboard_content = dash_data.get("dashboard", {})

            # a. Nombre del Dashboard
            nombre = dashboard_content.get("title", dash.get("title", "Sin título"))
            
            # b. UUID = uid
            
            # c. Construir el link absoluto al Dashboard
            meta_url = meta.get("url", f"/d/{uid}")
            link = f"{grafana_url}{meta_url}"
            
            # d. Fecha de la última modificación
            ultima_modificacion = meta.get("updated", "N/A")

            # Estructurar la fila
            rows_to_write.append([nombre, uid, link, ultima_modificacion])

            # Sanitizar el nombre del archivo JSON
            filename_clean = "".join(c for c in nombre if c.isalnum() or c in (" ", "_", "-")).rstrip()
            filepath = os.path.join(dir_backups, f"{filename_clean}_{uid}.json")

            # Guardar el JSON del backup completo
            with open(filepath, "w", encoding="utf-8") as f:
                json.dump(dashboard_content, f, indent=4, ensure_ascii=False)

        except Exception as e:
            print(f"❌ Error inesperado procesando el dashboard UID {uid}: {e}")

    # Preparar los datos finales (Cabecera + Filas)
    headers_row = ["Nombre de DB", "UUID", "Link", "Última modificación"]
    all_data = [headers_row] + rows_to_write

    # 6. Guardar los metadatos en un archivo CSV local de forma preventiva
    csv_filename = "dashboards_metadata.csv"
    print(f"💾 Guardando metadatos localmente en '{csv_filename}'...")
    try:

        with open(csv_filename, mode="w", newline="", encoding="utf-8-sig") as f:
            writer = csv.writer(f, delimiter=";")  
            writer.writerows(all_data)
        print(f"✅ Archivo CSV local guardado con éxito: {os.path.abspath(csv_filename)}")
    except Exception as e:
        print(f"❌ Error al guardar el archivo CSV local: {e}")

if __name__ == "__main__":
    main()
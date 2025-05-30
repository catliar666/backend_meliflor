from .auth import obtener_token_acceso
import requests

def fetch_document_by_reference(ref_url):
    token = obtener_token_acceso()
    url = f"https://firestore.googleapis.com/v1/{ref_url}"

    headers = {
        "Authorization": f"Bearer {token}"
    }

    response = requests.get(url, headers=headers)

    if response.status_code == 200:
        return response.json()
    else:
        raise Exception(f"Error al obtener {ref_url}: {response.status_code} - {response.text}")
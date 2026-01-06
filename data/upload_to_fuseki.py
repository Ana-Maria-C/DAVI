import requests
import os

FUSEKI_URL = "http://localhost:3030"
DATASET_NAME = "movielens"
DATA_FILE = "movielens_graph.ttl"

def create_dataset():
    """Creates the dataset if it doesn't exist."""
    AUTH = ('admin', 'admin')

    url_create = f"{FUSEKI_URL}/$/datasets"
    payload = {
        "dbName": DATASET_NAME,
        "dbType": "mem" 
    }
    try:
        r = requests.post(url_create, data=payload, auth=AUTH)
        if r.status_code == 200:
            print(f"Dataset '{DATASET_NAME}' created.")
        elif r.status_code == 409:
             print(f"Dataset '{DATASET_NAME}' already exists (409).")
        else:
            print(f"Dataset creation response: {r.status_code} - {r.text}")
    except Exception as e:
        print(f"Error creating dataset: {e}")

def upload_data():
    file_path = os.path.join(os.path.dirname(__file__), DATA_FILE)
    if not os.path.exists(file_path):
        print(f"File not found: {file_path}")
        return

    url = f"{FUSEKI_URL}/{DATASET_NAME}/data?default"
    headers = {"Content-Type": "text/turtle;charset=utf-8"}
    AUTH = ('admin', 'admin')
    
    try:
        print(f"Uploading {DATA_FILE}...")
        headers = {"Content-Type": "text/turtle;charset=utf-8"}
        with open(file_path, "rb") as f:
            data = f.read()
            r = requests.put(url, data=data, headers=headers, auth=AUTH)
            if r.status_code in [200, 201, 204]:
                print("Data uploaded successfully!")
            else:
                print(f"Error uploading data: {r.status_code} {r.text}")

        schema_path = os.path.join(os.path.dirname(__file__), "../ontology/schema.ttl")
        if os.path.exists(schema_path):
            print(f"Uploading schema from {schema_path}...")
            with open(schema_path, "rb") as f:
                schema_data = f.read()
                r_schema = requests.post(url, data=schema_data, headers=headers, auth=AUTH)
                if r_schema.status_code in [200, 201, 204]:
                    print("Ontology Schema uploaded successfully!")
                else:
                    print(f"Error uploading schema: {r_schema.status_code} {r_schema.text}")
        else:
            print("Warning: schema.ttl not found, skipping schema upload.")

    except Exception as e:
        print(f"Failed to connect to Fuseki: {e}")

if __name__ == "__main__":
    print("Ensure Fuseki is running...")
    create_dataset()
    upload_data()

import logging
import azure.functions as func
from azure.storage.blob import BlobServiceClient
import pandas as pd
import io, os, json

# Azurite connection using default Azure account
CONNECTION_STRING = (
    "DefaultEndpointsProtocol=http;"
    "AccountName=devstoreaccount1;"
    "AccountKey=Eby8vdM02xNOcqFlqUwJPLlmEtlCDXJ1OUzFT50uSRZ6IFsuFq2UVErCz4I6tq/K1SZFPTOtr/KBHBeksoGMGw==;"
    "BlobEndpoint=http://127.0.0.1:10000/devstoreaccount1;"
)

CONTAINER_NAME = "dataset" 
BLOB_NAME = "All_Diets.csv"
LOCAL_CSV_PATH = os.path.join("function_app", "local_csv", BLOB_NAME)
RESULTS_PATH = os.path.join("function_app", "simulated_nosql", "results.json")

def main(req: func.HttpRequest) -> func.HttpResponse:
    logging.info("HTTP trigger function processed a request.")

    try:
        # Connect to Azurite
        blob_service_client = BlobServiceClient.from_connection_string(CONNECTION_STRING)
        container_client = blob_service_client.get_container_client(CONTAINER_NAME)

        try:
            container_client.create_container()
        except Exception:
            pass  # container already exists

        # Upload CSV if missing
        blob_client = container_client.get_blob_client(BLOB_NAME)
        try:
            blob_client.get_blob_properties()
        except Exception:
            with open(LOCAL_CSV_PATH, "rb") as f:
                blob_client.upload_blob(f)

        # Download CSV and process
        stream = blob_client.download_blob().readall()
        df = pd.read_csv(io.BytesIO(stream))

        avg_macros = df.groupby("Diet_type")[["Protein(g)", "Carbs(g)", "Fat(g)"]].mean()
        result = avg_macros.reset_index().to_dict(orient="records")

        os.makedirs(os.path.dirname(RESULTS_PATH), exist_ok=True)
        with open(RESULTS_PATH, "w") as f:
            json.dump(result, f, indent=4)

        return func.HttpResponse(
            json.dumps({"message": "Data processed successfully.", "result": result}),
            mimetype="application/json"
        )

    except Exception as e:
        return func.HttpResponse(json.dumps({"error": str(e)}), status_code=500)

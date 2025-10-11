# function_app/__init__.py (optimized version for Task 5)
import logging
import azure.functions as func
from azure.storage.blob import BlobServiceClient
import pandas as pd
import io, os, json, time

# Azurite connection (same as before)
CONNECTION_STRING = (
    "DefaultEndpointsProtocol=http;"
    "AccountName=devstoreaccount1;"
    "AccountKey=Eby8vdM02xNOcqFlqUwJPLlmEtlCDXJ1OUzFT50uSRZ6IFsuFq2UVErCz4I6tq/K1SZFPTOtr/KBHBeksoGMGw==;"
    "BlobEndpoint=http://127.0.0.1:10000/devstoreaccount1;"
)

CONTAINER_NAME = "dataset"
BLOB_NAME = "All_Diets.csv"
LOCAL_CSV_PATH = os.path.join("function_app", "local_csv", BLOB_NAME)
RESULTS_PATH = os.path.join("function_app", "simulated_nosql", "results_optimized.json")

def main(req: func.HttpRequest) -> func.HttpResponse:
    logging.info("HTTP trigger function processed a request (optimized version).")
    start_time = time.time()

    try:
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

        # Download and process optimized
        stream = blob_client.download_blob().readall()
        use_cols = ["Diet_type", "Protein(g)", "Carbs(g)", "Fat(g)"]
        df = pd.read_csv(io.BytesIO(stream), usecols=use_cols)

        # Drop nulls and use lighter dtype
        df = df.dropna().astype({
            "Protein(g)": "float32",
            "Carbs(g)": "float32",
            "Fat(g)": "float32"
        })

        # Faster groupby
        avg_macros = df.groupby("Diet_type", observed=True).mean()

        result = avg_macros.reset_index().to_dict(orient="records")

        os.makedirs(os.path.dirname(RESULTS_PATH), exist_ok=True)
        with open(RESULTS_PATH, "w") as f:
            json.dump(result, f, indent=None, separators=(",", ":"))

        elapsed = round(time.time() - start_time, 2)
        msg = {"message": f"Optimized data processed successfully in {elapsed} seconds.", "result": result}

        return func.HttpResponse(json.dumps(msg), mimetype="application/json")

    except Exception as e:
        return func.HttpResponse(json.dumps({"error": str(e)}), status_code=500)

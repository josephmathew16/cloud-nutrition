import logging
import azure.functions as func
from azure.storage.blob import BlobServiceClient
import pandas as pd
import io, os, json, time

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

# Blob client and cache initialized once
blob_service_client = BlobServiceClient.from_connection_string(CONNECTION_STRING)
container_client = blob_service_client.get_container_client(CONTAINER_NAME)

# Cache for previously processed data
CACHE = {"result": None, "last_updated": None}


def main(req: func.HttpRequest) -> func.HttpResponse:
    start_time = time.time()
    logging.info("Function execution started.")

    try:
        #Check if container exists (only once)
        try:
            container_client.create_container()
        except Exception:
            pass

        blob_client = container_client.get_blob_client(BLOB_NAME)

        #Reuse cached result if available (simulate caching)
        if CACHE["result"] is not None:
            logging.info("Using cached result (warm execution).")
            result = CACHE["result"]
        else:
            logging.info("Downloading and processing new blob data (cold execution).")

            # Upload CSV if missing
            try:
                blob_client.get_blob_properties()
            except Exception:
                with open(LOCAL_CSV_PATH, "rb") as f:
                    blob_client.upload_blob(f)

            # Download and process CSV
            stream = blob_client.download_blob().readall()
            df = pd.read_csv(io.BytesIO(stream))

            avg_macros = df.groupby("Diet_type")[["Protein(g)", "Carbs(g)", "Fat(g)"]].mean()
            result = avg_macros.reset_index().to_dict(orient="records")

            # Save result to JSON (simulate NoSQL)
            os.makedirs(os.path.dirname(RESULTS_PATH), exist_ok=True)
            with open(RESULTS_PATH, "w") as f:
                json.dump(result, f, indent=4)

            # Store result in cache
            CACHE["result"] = result
            CACHE["last_updated"] = time.strftime("%Y-%m-%d %H:%M:%S")

        # Step 3: Measure total execution time
        end_time = time.time()
        execution_time = round(end_time - start_time, 3)

        # Simulated increased memory allocation (for testing only)
        os.environ["FUNCTION_MEMORY_MB"] = "512"  # Pretend this is the allocated memory

        logging.info(f"Function executed in {execution_time} seconds.")

        return func.HttpResponse(
            json.dumps({
                "message": "Data processed successfully.",
                "execution_time_sec": execution_time,
                "cached_result": CACHE["last_updated"] is not None,
                "result": result
            }),
            mimetype="application/json"
        )

    except Exception as e:
        logging.error(f"Error: {str(e)}")
        return func.HttpResponse(json.dumps({"error": str(e)}), status_code=500)

import os, json, io, logging
import pandas as pd
import azure.functions as func
from azure.storage.blob import BlobServiceClient

CONNECTION_STRING = os.environ["AzureWebJobsStorage"]
CONTAINER_NAME = "dataset"
BLOB_NAME = "All_Diets.csv"

def main(req: func.HttpRequest) -> func.HttpResponse:
    logging.info("Processing request in Azure Function.")

    try:
        # Connect to Azure Blob Storage
        blob_service_client = BlobServiceClient.from_connection_string(CONNECTION_STRING)
        container_client = blob_service_client.get_container_client(CONTAINER_NAME)

        # Ensure container exists
        try:
            container_client.create_container()
        except Exception:
            pass

        # Access CSV blob
        blob_client = container_client.get_blob_client(BLOB_NAME)
        blob_data = blob_client.download_blob().readall()

        df = pd.read_csv(io.BytesIO(blob_data))
        avg_macros = df.groupby("Diet_type")[["Protein(g)", "Carbs(g)", "Fat(g)"]].mean()
        result = avg_macros.reset_index().to_dict(orient="records")

        # Upload results to blob storage
        output_blob = container_client.get_blob_client("results.json")
        output_blob.upload_blob(json.dumps(result, indent=4), overwrite=True)

        return func.HttpResponse(
            json.dumps({"message": "Data processed successfully!", "result": result}),
            mimetype="application/json"
        )

    except Exception as e:
        logging.error(f"Error: {e}")
        return func.HttpResponse(json.dumps({"error": str(e)}), status_code=500)

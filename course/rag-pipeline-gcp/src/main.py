import functions_framework
from flask import Request, jsonify
from cloudevents.http import from_http, CloudEvent
from google.cloud import storage
from rag.rag_pipeline import process_rag_corpus
import json
import logging
from datetime import datetime

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


#  Shared utility: Process files using config
def process_documents(config: dict) -> dict:
    storage_client = storage.Client()
    process_bucket = config.get("PROCESS_BUCKET")
    audit_bucket = config.get("AUDIT_BUCKET")
    display_name = config.get("DISPLAY_NAME")

    if not process_bucket or not audit_bucket or not display_name:
        return {"error": "Missing required fields in config"}

    blobs = list(storage_client.bucket(process_bucket).list_blobs())
    for blob in blobs:
        if not blob.name.endswith(".tmp") and not blob.name.endswith("eventfile.txt"):
            logger.info(f"Processing file: {blob.name}")
            process_rag_corpus(process_bucket, blob.name, config)

    return {"status": f"Processed files in bucket: {process_bucket}"}


#  CloudEvent Utility

def handle_eventfile_upload(bucket_name: str, filename: str) -> dict:
    if not filename.endswith("eventfile.txt"):
        logger.info("Ignored: not an eventfile.txt")
        return {"status": "ignored"}

    storage_client = storage.Client()
    bucket = storage_client.bucket(bucket_name)
    blob = bucket.blob(filename)

    if not blob.exists():
        return {"error": f"{filename} not found in {bucket_name}"}

    #  Load config from eventfile.txt
    config = json.loads(blob.download_as_text())

    #  Process files to create corpus
    result = process_documents(config)

    #  Archive eventfile.txt after corpus creation
    audit_bucket_name = config.get("AUDIT_BUCKET")
    ts = datetime.utcnow().strftime("%Y-%m-%d-%H-%M-%S")
    new_filename = filename.replace(".txt", f"-{ts}.txt")

    audit_bucket = storage_client.bucket(audit_bucket_name)
    bucket.copy_blob(blob, audit_bucket, new_filename)
    blob.delete()

    #  Add status about archive
    logger.info(f"Archived eventfile.txt to {audit_bucket_name}/{new_filename}")
    result["archived"] = f"{audit_bucket_name}/{new_filename}"
    result["status"] = "Corpus processed and eventfile archived successfully"

    return result




#  Function 1: HTTP Handler (Postman, API call)

@functions_framework.http
def http_handler(request: Request):
    logger.info("HTTP function triggered")
    try:
        config = request.get_json(silent=True)
        if not config:
            return jsonify({"error": "Missing JSON config in HTTP request"}), 400

        result = process_documents(config)
        return jsonify(result), 200

    except Exception as e:
        logger.exception("HTTP handler failed")
        return jsonify({"error": str(e)}), 500



#  Function 2: CloudEvent Handler (GCS upload)
@functions_framework.cloud_event
def cloud_event_handler(cloud_event: CloudEvent):
    logger.info("CloudEvent function triggered")
    try:
        data = cloud_event.data
        bucket_name = data.get("bucket")
        filename = data.get("name")

        if not bucket_name or not filename:
            return jsonify({"error": "Missing bucket or filename"}), 400

        result = handle_eventfile_upload(bucket_name, filename)
        logger.info(f"CloudEvent processed: {result}")
        return

    except Exception as e:
        logger.exception("CloudEvent handler failed")
        raise 
from vertexai import rag
from vertexai.generative_models import GenerativeModel, Tool
import vertexai
from google.cloud import storage

def process_rag_corpus(process_bucket_name: str, filename: str, config: dict) -> None:
    """Processes a single file from the process bucket for RAG, using dynamic config."""

    # Extract config values from eventfile.txt
    project_id = config.get("PROJECT_ID")
    location = config.get("LOCATION")
    display_name = config["DISPLAY_NAME"]
    result_bucket_name = config["RESULT_BUCKET"]
    result_path = config["RESULT_PATH"]
    embedding_model = config["EMBEDDING_MODEL"]
    chunk_size = config.get("CHUNK_SIZE")
    chunk_overlap = config.get("CHUNK_OVERLAP")
    delete_previous_results = config.get("DELETE_PREVIOUS_RESULTS")
    max_requests = config.get("MAX_EMBEDDING_REQUESTS_PER_MIN")
    timestamp_suffix = config.get("TIMESTAMP_SUFFIX")

    # Initialize Vertex AI
    vertexai.init(project=project_id, location=location)

    source_gcs_path = f"gs://{process_bucket_name}/{filename}"
    final_result_path = result_path
    if timestamp_suffix:
        from datetime import datetime
        ts = datetime.now().strftime("%Y%m%d-%H%M%S")
        final_result_path = result_path.replace(".ndjson", f"-{ts}.ndjson")
    result_gcs_path = f"gs://{result_bucket_name}/{final_result_path}"

    print(f"Processing file: {source_gcs_path}")
    print(f"Result will be stored at: {result_gcs_path}")

    try:
        # Check or create corpus
        corpora = rag.list_corpora()
        existing_corpus = next((c for c in corpora if c.display_name == display_name), None)

        if existing_corpus:
            rag_corpus = existing_corpus
            print(f"Using existing corpus: {rag_corpus.name}")
        else:
            print(f"Creating new corpus: {display_name}")
            embedding_model_config = rag.RagEmbeddingModelConfig(
                vertex_prediction_endpoint=rag.VertexPredictionEndpoint(
                    publisher_model=embedding_model
                )
            )
            rag_corpus = rag.create_corpus(
                display_name=display_name,
                backend_config=rag.RagVectorDbConfig(
                    rag_embedding_model_config=embedding_model_config
                ),
            )
            print(f"Created new corpus: {rag_corpus.name}")

        # Delete previous result if allowed
        storage_client = storage.Client()
        result_bucket = storage_client.bucket(result_bucket_name)
        result_blob = result_bucket.blob(final_result_path)

        if delete_previous_results and result_blob.exists():
            print("Deleting existing result file...")
            result_blob.delete()

        # Import file into corpus
        response = rag.import_files(
            rag_corpus.name,
            paths=[source_gcs_path],
            transformation_config=rag.TransformationConfig(
                chunking_config=rag.ChunkingConfig(
                    chunk_size=chunk_size,
                    chunk_overlap=chunk_overlap,
                )
            ),
            max_embedding_requests_per_min=max_requests,
            import_result_sink=result_gcs_path,
        )

        print(f"Imported {response.imported_rag_files_count} files")
        print(f"Skipped {response.skipped_rag_files_count} files")

    except Exception as e:
        print(f"Error processing RAG corpus: {str(e)}")
        raise 
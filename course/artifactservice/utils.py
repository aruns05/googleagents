# Example of how an artifact might be represented as a types.Part
import google.genai.types as types
import os

def get_artifact_mime_type(pdf_file_path: str) -> str:
    pdf_bytes = file_to_bytes(pdf_file_path)
    
    if pdf_bytes:
        # Create an artifact from the PDF bytes using the convenience constructor
        pdf_artifact = types.Part.from_bytes(
            data=pdf_bytes, mime_type="application/pdf"
        )

    print(f"Successfully converted '{os.path.basename(pdf_file_path)}' to bytes.")
    # print(f"Artifact MIME Type: {pdf_artifact.inline_data.mime_type}")
    # print(f"Total bytes: {len(pdf_artifact.inline_data.data)}")
    # print(f"Artifact Data (first 20 bytes): {pdf_artifact.inline_data.data[:20]}...")
    
    pdf_artifact = types.Part(
        inline_data=types.Blob(
            mime_type="application/pdf",
            data=pdf_bytes
        )
    )

    # You can also use the convenience constructor:
    # image_artifact_alt = types.Part.from_bytes(data=image_bytes, mime_type="image/png")

    print(f"Artifact MIME Type: {pdf_artifact.inline_data.mime_type}")
    print(f"Artifact Data (first 100 bytes): {pdf_artifact.inline_data.data[:100]}...")
    

def file_to_bytes(file_path: str) -> bytes | None:
    """Reads a file and returns its content as bytes."""
    try:
        with open(file_path, "rb") as f:
            return f.read()
    except FileNotFoundError:
        print(f"Error: The file '{file_path}' was not found.")
        return None

# --- Example: Convert PDF to bytes ---

# NOTE: Assumes the PDF from your other script is in the expected location.
pdf_file_path = "./Bilingual_Forms_for_Office_use.pdf"

# print(f"Converting '{os.path.basename(pdf_file_path)}' to bytes...")
# get_artifact_mime_type(pdf_file_path)




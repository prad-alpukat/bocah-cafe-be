import firebase_admin
from firebase_admin import credentials, storage
from config import settings

# Initialize Firebase Admin SDK
cred = credentials.Certificate(settings.FIREBASE_SERVICE_ACCOUNT_PATH)

# Initialize app with storage bucket
firebase_admin.initialize_app(cred, {
    'storageBucket': settings.FIREBASE_STORAGE_BUCKET
})

# Get a reference to the storage service
bucket = storage.bucket()

def upload_file_to_storage(file_path: str, destination_blob_name: str) -> str:
    """
    Upload a file to Firebase Cloud Storage

    Args:
        file_path: Local path to the file
        destination_blob_name: Name for the file in Cloud Storage

    Returns:
        Public URL of the uploaded file
    """
    blob = bucket.blob(destination_blob_name)
    blob.upload_from_filename(file_path)

    # Make the blob publicly accessible
    blob.make_public()

    return blob.public_url

def upload_file_from_memory(file_content: bytes, destination_blob_name: str, content_type: str = None) -> str:
    """
    Upload file content from memory to Firebase Cloud Storage

    Args:
        file_content: File content in bytes
        destination_blob_name: Name for the file in Cloud Storage
        content_type: MIME type of the file (e.g., 'image/jpeg')

    Returns:
        Public URL of the uploaded file
    """
    blob = bucket.blob(destination_blob_name)
    blob.upload_from_string(file_content, content_type=content_type)

    # Make the blob publicly accessible
    blob.make_public()

    return blob.public_url

def delete_file_from_storage(blob_name: str) -> bool:
    """
    Delete a file from Firebase Cloud Storage

    Args:
        blob_name: Name of the file in Cloud Storage

    Returns:
        True if successful, False otherwise
    """
    try:
        blob = bucket.blob(blob_name)
        blob.delete()
        return True
    except Exception as e:
        print(f"Error deleting file: {e}")
        return False

def get_file_url(blob_name: str) -> str:
    """
    Get the public URL of a file in Firebase Cloud Storage

    Args:
        blob_name: Name of the file in Cloud Storage

    Returns:
        Public URL of the file
    """
    blob = bucket.blob(blob_name)
    blob.make_public()
    return blob.public_url

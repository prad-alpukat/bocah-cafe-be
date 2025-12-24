from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File
import uuid
from datetime import datetime
from models import Admin
from schemas import UploadResponse, MessageResponse
from auth_utils import get_current_admin
from firebase_config import upload_file_from_memory, delete_file_from_storage

router = APIRouter()

# Security: Fixed upload folder to prevent path traversal attacks
UPLOAD_FOLDER = "cafe-images"

# Allowed image types
ALLOWED_EXTENSIONS = {'image/jpeg', 'image/jpg', 'image/png', 'image/webp', 'image/gif'}
MAX_FILE_SIZE = 5 * 1024 * 1024  # 5MB


def validate_image(file: UploadFile) -> None:
    """Validate uploaded image file"""
    if file.content_type not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"File type not allowed. Allowed types: {', '.join(ALLOWED_EXTENSIONS)}"
        )


@router.post("/image", response_model=UploadResponse, status_code=status.HTTP_201_CREATED)
async def upload_image(
    file: UploadFile = File(...),
    current_admin: Admin = Depends(get_current_admin)
):
    """
    Upload image to Firebase Cloud Storage
    Admin only - requires authentication

    Args:
        file: Image file to upload (JPEG, PNG, WebP, GIF)

    Returns:
        UploadResponse: Contains image_url and file metadata
    """
    validate_image(file)

    content = await file.read()

    if len(content) > MAX_FILE_SIZE:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"File too large. Maximum size is {MAX_FILE_SIZE / 1024 / 1024}MB"
        )

    # Generate unique filename
    file_extension = file.filename.split('.')[-1] if '.' in file.filename else 'jpg'
    unique_filename = f"{uuid.uuid4()}.{file_extension}"
    destination_path = f"{UPLOAD_FOLDER}/{unique_filename}"

    try:
        image_url = upload_file_from_memory(
            file_content=content,
            destination_blob_name=destination_path,
            content_type=file.content_type
        )

        return {
            "message": "Image uploaded successfully",
            "data": {
                "image_url": image_url,
                "filename": unique_filename,
                "original_filename": file.filename,
                "size": len(content),
                "content_type": file.content_type,
                "uploaded_by": current_admin.username,
                "uploaded_at": datetime.utcnow().isoformat()
            }
        }

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to upload image: {str(e)}"
        )


@router.delete("/image", response_model=MessageResponse)
async def delete_image(
    filename: str,
    current_admin: Admin = Depends(get_current_admin)
):
    """
    Delete image from Firebase Cloud Storage
    Admin only - requires authentication

    Args:
        filename: The filename to delete (e.g., 'abc123.jpg')

    Returns:
        MessageResponse: Success message
    """
    # Security: Only allow deletion from the fixed upload folder
    blob_name = f"{UPLOAD_FOLDER}/{filename}"

    try:
        success = delete_file_from_storage(blob_name)

        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Image not found or already deleted"
            )

        return {"message": "Image deleted successfully"}

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to delete image: {str(e)}"
        )

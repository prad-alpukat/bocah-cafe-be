from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File
from typing import Optional
import uuid
from datetime import datetime
from models import Admin
from auth_utils import get_current_admin
from firebase_config import upload_file_from_memory, delete_file_from_storage

router = APIRouter()

# Allowed image types
ALLOWED_EXTENSIONS = {'image/jpeg', 'image/jpg', 'image/png', 'image/webp', 'image/gif'}
MAX_FILE_SIZE = 5 * 1024 * 1024  # 5MB

def validate_image(file: UploadFile) -> None:
    """
    Validate uploaded image file

    Args:
        file: The uploaded file

    Raises:
        HTTPException: If file is invalid
    """
    # Check content type
    if file.content_type not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"File type not allowed. Allowed types: {', '.join(ALLOWED_EXTENSIONS)}"
        )

@router.post("/image", status_code=status.HTTP_201_CREATED)
async def upload_image(
    file: UploadFile = File(...),
    folder: Optional[str] = "uploads",
    current_admin: Admin = Depends(get_current_admin)
):
    """
    Upload image to Firebase Cloud Storage
    Admin only - requires authentication

    Args:
        file: Image file to upload (JPEG, PNG, WebP, GIF)
        folder: Optional folder name in storage (default: 'uploads')

    Returns:
        dict: Contains image_url and file metadata
    """
    # Validate image
    validate_image(file)

    # Read file content
    content = await file.read()

    # Check file size
    if len(content) > MAX_FILE_SIZE:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"File too large. Maximum size is {MAX_FILE_SIZE / 1024 / 1024}MB"
        )

    # Generate unique filename
    file_extension = file.filename.split('.')[-1] if '.' in file.filename else 'jpg'
    unique_filename = f"{uuid.uuid4()}.{file_extension}"
    destination_path = f"{folder}/{unique_filename}"

    try:
        # Upload to Firebase Storage
        image_url = upload_file_from_memory(
            file_content=content,
            destination_blob_name=destination_path,
            content_type=file.content_type
        )

        return {
            "message": "Image uploaded successfully",
            "image_url": image_url,
            "filename": unique_filename,
            "original_filename": file.filename,
            "size": len(content),
            "content_type": file.content_type,
            "uploaded_by": current_admin.username,
            "uploaded_at": datetime.utcnow().isoformat()
        }

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to upload image: {str(e)}"
        )

@router.delete("/image")
async def delete_image(
    blob_name: str,
    current_admin: Admin = Depends(get_current_admin)
):
    """
    Delete image from Firebase Cloud Storage
    Admin only - requires authentication

    Args:
        blob_name: The path/name of the file in storage (e.g., 'uploads/filename.jpg')

    Returns:
        dict: Success message
    """
    try:
        success = delete_file_from_storage(blob_name)

        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Image not found or already deleted"
            )

        return {
            "message": "Image deleted successfully",
            "deleted_by": current_admin.username,
            "deleted_at": datetime.utcnow().isoformat()
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to delete image: {str(e)}"
        )

@router.post("/cafe-image", status_code=status.HTTP_201_CREATED)
async def upload_cafe_image(
    file: UploadFile = File(...),
    current_admin: Admin = Depends(get_current_admin)
):
    """
    Upload cafe image to Firebase Cloud Storage
    Specialized endpoint for cafe images with specific folder structure
    Admin only - requires authentication

    Args:
        file: Image file to upload (JPEG, PNG, WebP, GIF)

    Returns:
        dict: Contains image_url and file metadata
    """
    # Validate image
    validate_image(file)

    # Read file content
    content = await file.read()

    # Check file size
    if len(content) > MAX_FILE_SIZE:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"File too large. Maximum size is {MAX_FILE_SIZE / 1024 / 1024}MB"
        )

    # Generate unique filename with cafe prefix
    file_extension = file.filename.split('.')[-1] if '.' in file.filename else 'jpg'
    unique_filename = f"cafe_{uuid.uuid4()}.{file_extension}"
    destination_path = f"cafe-images/{unique_filename}"

    try:
        # Upload to Firebase Storage
        image_url = upload_file_from_memory(
            file_content=content,
            destination_blob_name=destination_path,
            content_type=file.content_type
        )

        return {
            "message": "Cafe image uploaded successfully",
            "image_url": image_url,
            "filename": unique_filename,
            "original_filename": file.filename,
            "size": len(content),
            "content_type": file.content_type,
            "uploaded_by": current_admin.username,
            "uploaded_at": datetime.utcnow().isoformat()
        }

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to upload cafe image: {str(e)}"
        )

import shutil
import random
import string
from b2sdk.v2 import InMemoryAccountInfo, B2Api
from tempfile import NamedTemporaryFile
from fastapi import APIRouter, File, HTTPException, UploadFile
from fastapi.responses import JSONResponse
from app.config.config import settings
from app.config.utils import generate_unique_filename

from _log_config.log_config import get_logger

b2_logger = get_logger('backblaze', 'backblaze_upload.log')



info = InMemoryAccountInfo()
b2_api = B2Api(info)
b2_api.authorize_account("production", settings.backblaze_id, settings.backblaze_key)

router = APIRouter(
    prefix="/upload-to-backblaze",
    tags=['Upload file'],
)


@router.post("/chat")
async def upload_to_backblaze(file: UploadFile = File(..., limit="25MB")):
    """
    This function handles file uploads to Backblaze B2 storage.

    Parameters:
    file (UploadFile): The file to be uploaded. The file size limit is set to 25MB.
    bucket_name (str): The name of the bucket where the file will be stored.
                        Default value is "chatall".

    Returns:
    JSONResponse: A JSON response containing the download URL of the uploaded file.
                  If an error occurs during the upload process, a HTTPException is raised.

    Raises:
    HTTPException: If an error occurs during the upload process.
    """
    try:
        # Create a temporary file to store the uploaded file
        with NamedTemporaryFile(delete=False) as temp_file:
            # Copy the uploaded file to the temporary file
            shutil.copyfileobj(file.file, temp_file)
            temp_file_path = temp_file.name

        bucket_name = "chatall"
        # Get the bucket by name
        bucket = b2_api.get_bucket_by_name(bucket_name)

        # Generate a unique filename for the uploaded file
        unique_filename = generate_unique_filename(file.filename)

        # Upload the local file to the bucket
        bucket.upload_local_file(
            local_file=temp_file_path,
            file_name=unique_filename
        )

        # Get the download URL for the uploaded file
        download_url = b2_api.get_download_url_for_file_name(bucket_name, unique_filename)
        return JSONResponse(status_code=200, content=download_url)
    except Exception as e:
        b2_logger.error(f"Error uploading file {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/list_files")
async def list_files():
    
    bucket_name = "chatall"
    
    # Get the bucket by name
    bucket = b2_api.get_bucket_by_name(bucket_name)
    
    # Get all files in the bucket
    # files = bucket.get
    
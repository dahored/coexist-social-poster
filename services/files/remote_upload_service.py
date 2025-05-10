import os
from services.files.cloudinary_service import CloudinaryService

class RemoteUploadService:
    def __init__(self):
        self.provider = os.getenv('REMOTE_UPLOAD_PROVIDER', 'cloudinary').lower()
        self.allow_remote_upload = os.getenv('ALLOW_REMOTE_UPLOAD', 'false').lower() == 'true'

        if self.provider == 'cloudinary':
            self.uploader = CloudinaryService()
        elif self.provider == 's3':
            # self.uploader = S3Service()
            raise NotImplementedError("S3Service not implemented yet")
        else:
            raise ValueError(f"Unsupported remote upload provider: {self.provider}")

    async def upload_file(self, file_path, folder="uploads"):
        if not self.allow_remote_upload:
            return "" 

        return self.uploader.upload_file(file_path, folder)

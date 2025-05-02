import cloudinary
import cloudinary.uploader
import os

class CloudinaryService:
    def __init__(self):
        cloudinary.config(
            cloud_name=os.getenv('CLOUDINARY_CLOUD_NAME'),
            api_key=os.getenv('CLOUDINARY_API_KEY'),
            api_secret=os.getenv('CLOUDINARY_API_SECRET'),
            secure=True
        )
        self.allow_remote_upload = os.getenv('ALLOW_REMOTE_UPLOAD', 'false').lower() == 'true'

    def upload_file(self, file_path, folder="uploads"):
        if not self.allow_remote_upload:
            return ""

        try:
            result = cloudinary.uploader.upload(
                file_path,
                folder=folder,
                use_filename=True,
                unique_filename=False,
                overwrite=True
            )
            secure_url = result.get('secure_url')
            if not secure_url:
                raise RuntimeError("Upload to Cloudinary failed, no secure_url returned.")
            return secure_url

        except cloudinary.exceptions.Error as e:
            # Cloudinary SDK specific error
            print(f"[CloudinaryService] Cloudinary error: {e}")
            return ""
        except Exception as e:
            # General error fallback
            print(f"[CloudinaryService] Failed to upload to Cloudinary: {e}")
            return ""

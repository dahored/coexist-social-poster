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

    def upload_file(self, file_path, folder="uploads"):
        """
        Uploads a file to Cloudinary and returns the secure URL.

        :param file_path: Path to the local file.
        :param folder: Cloudinary folder (optional, default 'uploads').
        :return: secure_url (str)
        """
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
        except Exception as e:
            raise RuntimeError(f"Failed to upload to Cloudinary: {e}")

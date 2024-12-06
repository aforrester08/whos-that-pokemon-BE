from PIL import Image
from io import BytesIO
import base64
from typing import Union

class ImageProcessingError(Exception):
    def __init__(self, message: str = "An error occurred during image processing"):
        self.message = message
        super().__init__(self.message)

class ImageProcessing:
    @staticmethod
    def encode_image_base64(img: Union[bytes, Image.Image], format="PNG") -> str:
        try:
            if isinstance(img, bytes):
                img = Image.open(BytesIO(img))

            if not isinstance(img, Image.Image):
                raise ImageProcessingError("Input must be a PIL.Image or bytes representing an image.")

            img_io = BytesIO()
            img.save(img_io, format=format)
            img_io.seek(0)
            return base64.b64encode(img_io.getvalue()).decode("utf-8")
        except Exception as e:
            raise ImageProcessingError(f"Error encoding image to base64: {str(e)}")

    @staticmethod
    def create_silhouette(img_bytes: bytes) -> str:
        try:
            img = Image.open(BytesIO(img_bytes))
            mask = img.getchannel("A") if "A" in img.getbands() else None 

            colored_layer = Image.new("RGBA", img.size, "#07679a")

            if mask:
                colored_layer.putalpha(mask)

            return ImageProcessing.encode_image_base64(colored_layer)
        except Exception as e:
            raise ImageProcessingError(f"Error creating silhouette: {str(e)}")

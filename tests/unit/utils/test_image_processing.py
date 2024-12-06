import unittest
from io import BytesIO
from PIL import Image
from app.utils.image_proccessing import ImageProcessing, ImageProcessingError

class TestImageProcessing(unittest.TestCase):
    def setUp(self):
        self.test_image = Image.new("RGBA", (100, 100), color=(255, 0, 0, 128))
        self.test_image_bytes = self._convert_image_to_bytes(self.test_image)

    def _convert_image_to_bytes(self, img: Image.Image) -> bytes:
        img_io = BytesIO()
        img.save(img_io, format="PNG")
        return img_io.getvalue()

    def test_encode_image_base64_with_pil_image(self):
        encoded_image = ImageProcessing.encode_image_base64(self.test_image)
        self.assertTrue(isinstance(encoded_image, str))
        self.assertTrue(encoded_image.startswith("iVBORw0KGgo"), "Base64 string does not start as expected.")

    def test_encode_image_base64_with_bytes(self):
        encoded_image = ImageProcessing.encode_image_base64(self.test_image_bytes)
        self.assertTrue(isinstance(encoded_image, str))
        self.assertTrue(encoded_image.startswith("iVBORw0KGgo"), "Base64 string does not start as expected.")

    def test_encode_image_base64_with_invalid_input(self):
        with self.assertRaises(ImageProcessingError):
            ImageProcessing.encode_image_base64("invalid input")

    def test_create_silhouette_with_valid_bytes(self):
        silhouette_image = ImageProcessing.create_silhouette(self.test_image_bytes)
        self.assertTrue(isinstance(silhouette_image, str))
        self.assertTrue(silhouette_image.startswith("iVBORw0KGgo"), "Base64 string does not start as expected.")

    def test_create_silhouette_with_invalid_input(self):
        with self.assertRaises(ImageProcessingError):
            ImageProcessing.create_silhouette(b"not an image")

    def test_create_silhouette_alpha_channel(self):
        silhouette_image = ImageProcessing.create_silhouette(self.test_image_bytes)
        self.assertTrue(isinstance(silhouette_image, str))
        self.assertTrue(silhouette_image.startswith("iVBORw0KGgo"))

    def test_create_silhouette_without_alpha_channel(self):
        rgb_image = Image.new("RGB", (100, 100), color=(255, 0, 0))
        rgb_image_bytes = self._convert_image_to_bytes(rgb_image)

        silhouette_image = ImageProcessing.create_silhouette(rgb_image_bytes)
        self.assertTrue(isinstance(silhouette_image, str))
        self.assertTrue(silhouette_image.startswith("iVBORw0KGgo"))

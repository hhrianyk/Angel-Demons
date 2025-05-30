import os
import subprocess
from PIL import Image
import logging

logger = logging.getLogger(__name__)


class MindARCompiler:
    def __init__(self, upload_folder, target_folder):
        self.upload_folder = upload_folder
        self.target_folder = target_folder
        os.makedirs(target_folder, exist_ok=True)

    def compile_image(self, image_path):
        """Compile image target using MindAR compiler"""
        try:
            # Перевірка та підготовка зображення
            if not os.path.exists(image_path):
                raise FileNotFoundError(f"Image not found: {image_path}")

            # Конвертація до JPEG (якщо потрібно)
            img = Image.open(image_path)
            if img.mode != 'RGB':
                img = img.convert('RGB')

            temp_path = os.path.join(self.upload_folder, 'temp_compile.jpg')
            img.save(temp_path, 'JPEG', quality=90)

            # Компіляція з MindAR
            base_name = os.path.splitext(os.path.basename(image_path))[0]
            output_file = os.path.join(self.target_folder, f"{base_name}.mind")

            cmd = [
                'npx', 'mind-ar-js-image-target-compiler',
                temp_path,
                '--output', output_file,
                '--force'
            ]

            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=120  # 2 хвилини таймаут
            )

            if result.returncode != 0:
                error_msg = result.stderr or "Unknown error"
                raise RuntimeError(f"Compilation failed: {error_msg}")

            if not os.path.exists(output_file):
                raise RuntimeError("Output .mind file not generated")

            return output_file

        except Exception as e:
            logger.error(f"Compilation error for {image_path}: {e}")
            raise
        finally:
            if 'temp_path' in locals() and os.path.exists(temp_path):
                os.remove(temp_path)
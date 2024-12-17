from PIL import Image, ImageDraw, ImageFont
import random
import numpy as np
from typing import Tuple, Optional

class OCRDataGenerator:
    def __init__(self, font_paths: list, 
                 bg_colors: list = [(255, 255, 255), (250, 250, 250), (245, 245, 245)],
                 text_colors: list = [(0, 0, 0), (50, 50, 50)]):
        self.font_paths = font_paths
        self.bg_colors = bg_colors
        self.text_colors = text_colors

    def _calculate_text_size(self, text: str, font: ImageFont.FreeTypeFont) -> Tuple[int, int]:
        """Calculate the size of the text with given font using getbbox()."""
        bbox = font.getbbox(text)
        return bbox[2] - bbox[0], bbox[3] - bbox[1]

    def _calculate_image_size(self, 
                            text: str, 
                            font: ImageFont.FreeTypeFont,
                            min_height: int = 64,
                            horizontal_padding: int = 40,
                            vertical_padding: int = 20) -> Tuple[int, int]:
        """
        Calculate appropriate image size based on text content and font.
        
        Args:
            text: Text to render
            font: Font to use
            min_height: Minimum height of the image
            horizontal_padding: Padding on left and right
            vertical_padding: Padding on top and bottom
            
        Returns:
            tuple: (width, height) for the image
        """
        text_width, text_height = self._calculate_text_size(text, font)
        
        # Calculate dimensions
        width = text_width + (horizontal_padding * 2)
        height = max(text_height + (vertical_padding * 2), min_height)
        
        # Ensure width is at least 1.5 times the height for very short text
        width = max(width, int(height * 1.5))
        
        return width, height

    def _add_noise(self, img: Image.Image, noise_factor: float = 0.02) -> Image.Image:
        """Add random noise to the image."""
        img_array = np.array(img)
        noise = np.random.normal(0, 255 * noise_factor, img_array.shape)
        noisy_img_array = np.clip(img_array + noise, 0, 255).astype(np.uint8)
        return Image.fromarray(noisy_img_array)

    def _apply_random_transform(self, img: Image.Image, max_skew: float = 2.0) -> Image.Image:
        """Apply random transformation (slight rotation and skew)."""
        angle = random.uniform(-max_skew, max_skew)
        return img.rotate(angle, resample=Image.BICUBIC, expand=True)

    def generate_image(self, 
                      text: str,
                      min_font_size: int = 24,
                      max_font_size: int = 48,
                      horizontal_padding: int = 40,
                      vertical_padding: int = 20,
                      min_height: int = 64,
                      add_noise: bool = True,
                      random_transform: bool = True) -> Tuple[Image.Image, dict]:
        """
        Generate an image containing the given text with dynamic sizing.
        
        Args:
            text: Text to render
            min_font_size: Minimum font size to use
            max_font_size: Maximum font size to use
            horizontal_padding: Padding on left and right
            vertical_padding: Padding on top and bottom
            min_height: Minimum height of the image
            add_noise: Whether to add noise to the image
            random_transform: Whether to apply random transformations
            
        Returns:
            tuple: (Generated image, metadata dictionary)
        """
        # Randomly select parameters
        font_path = random.choice(self.font_paths)
        font_size = random.randint(min_font_size, max_font_size)
        bg_color = random.choice(self.bg_colors)
        text_color = random.choice(self.text_colors)
        
        # Create font
        font = ImageFont.truetype(font_path, font_size)
        
        # Calculate appropriate image size
        image_size = self._calculate_image_size(
            text, 
            font,
            min_height=min_height,
            horizontal_padding=horizontal_padding,
            vertical_padding=vertical_padding
        )
        
        # Create base image
        img = Image.new('RGB', image_size, color=bg_color)
        draw = ImageDraw.Draw(img)
        
        # Calculate text position
        text_width, text_height = self._calculate_text_size(text, font)
        x = (image_size[0] - text_width) // 2
        y = (image_size[1] - text_height) // 2
        
        # Draw text
        draw.text((x, y), text, font=font, fill=text_color)
        
        # Apply transformations
        if random_transform:
            img = self._apply_random_transform(img)
            
        if add_noise:
            img = self._add_noise(img)
        
        # Create metadata
        metadata = {
            'text': text,
            'font': font_path,
            'font_size': font_size,
            'image_size': image_size,
            'bg_color': bg_color,
            'text_color': text_color
        }
        
        return img, metadata

    def generate_dataset(self, 
                        texts: list,
                        output_dir: str,
                        images_per_text: int = 1,
                        **kwargs) -> list:
        """
        Generate a dataset of images from a list of texts.
        
        Args:
            texts: List of texts to generate images for
            output_dir: Directory to save the images
            images_per_text: Number of images to generate per text
            **kwargs: Additional arguments to pass to generate_image
            
        Returns:
            list: List of dictionaries containing image paths and metadata
        """
        import os
        import json
        
        os.makedirs(output_dir, exist_ok=True)
        dataset_info = []
        
        for idx, text in enumerate(texts):
            for variant in range(images_per_text):
                img, metadata = self.generate_image(text, **kwargs)
                
                # Save image
                image_filename = f"{idx}_{variant}.png"
                image_path = os.path.join(output_dir, image_filename)
                img.save(image_path)
                
                # Save metadata
                metadata['image_path'] = image_path
                dataset_info.append(metadata)
        
        # Save dataset metadata
        with open(os.path.join(output_dir, 'metadata.json'), 'w') as f:
            json.dump(dataset_info, f, indent=2)
            
        return dataset_info
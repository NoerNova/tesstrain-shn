# Shan data synthesis for Tesseract-OCR v5

This dir contained several script to synthesize Tesseract-OCR [tesstrain](https://github.com/tesseract-ocr/tesstrain) datasets for Shan language.

1. Short, single-line dataset by split chunk 20-50 each.
    - This part using Pillow package to generate.
2. Long, multi-line dataset split with "။" as a paragraph in Shan.
    - This part using Tesseract's text2image to generate.

This also contained Fonts and dataset_labs notebook for testing, extract and generate from docx for example.

## Usage

```bash
pip install -r requirements.txt
```
import time
from OCRDataGenerator import OCRDataGenerator

output_dir = "./output"
fonts = [
    "./Shan.ttf",
    "./PangLong.ttf"
]

generator = OCRDataGenerator(font_paths = fonts)

texts = [
    "ၸွမ်းတီႈၼႂ်းပိူင်ၵၢၼ်ပၢႆးမၢၵ်ႈမုၼ်းယူႇႁိုဝ်?",
    "လူဝ်ႇမီးလွင်ႈလူင်ပွင်ႊၸိုင်ႈၶဝ်ႈပႃး",
    "တီႈလႂ် မႃး။ ၵမ်ႈၼမ်ၼမ်တႄႉ"
]

for text in texts:
    image, metadata = generator.generate_image(
        text=text,
        min_font_size=24,
        max_font_size=48,
        horizontal_padding=40,
        vertical_padding=20,
        min_height=64,
        add_noise=False,
        random_transform=False
    )
    print(f"Text: {text}")
    print(f"Image size: {metadata['image_size']}\n")

    ts = time.time()

    # save TIF
    image.save(f"{output_dir}/{ts}.tif")
        
    # save TXT
    with open(f"{output_dir}/{ts}.gt.txt", "w", encoding='utf-8') as text_file:
        text_file.write(text)

    print(f"Saved image for word: {text}")
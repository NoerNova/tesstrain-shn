import re
from shannlp import word_tokenize, shan_characters, shan_digits
import os
import random
import pathlib
import subprocess

def remove_emojis(data):
    emoj = re.compile("["
        u"\U0001F600-\U0001F64F"  # emoticons
        u"\U0001F300-\U0001F5FF"  # symbols & pictographs
        u"\U0001F680-\U0001F6FF"  # transport & map symbols
        u"\U0001F1E0-\U0001F1FF"  # flags (iOS)
        u"\U00002500-\U00002BEF"  # chinese char
        u"\U00002702-\U000027B0"
        u"\U000024C2-\U0001F251"
        u"\U0001f926-\U0001f937"
        u"\U00010000-\U0010ffff"
        u"\u2640-\u2642" 
        u"\u2600-\u2B55"
        u"\u200d"
        u"\u23cf"
        u"\u23e9"
        u"\u231a"
        u"\ufe0f"  # dingbats
        u"\u3030"
        "]+", re.UNICODE)
    return re.sub(emoj, '', data)

def remove_latin_text(text):
    text = re.sub(r"[^\u1000-\u109f0-9\s/\-\"']", '', text)
    text = re.sub(r"\s+", " ", text)
    return text

def remove_myanmar_text(text):
    allowed_chars = set(shan_characters + shan_digits + "/-'\"")
    tokens = word_tokenize(text, engine="newmm")
    cleaned_words = []

    for word in tokens:
        is_shan_word = True
        for char in word:
            if char not in allowed_chars and not char.isspace() and not char.isnumeric():
                is_shan_word = False
                break
        if is_shan_word:
            cleaned_words.append(word)
    
    cleaned_text = "".join(cleaned_words)
    
    cleaned_text = re.sub(r'\s+', ' ', cleaned_text).strip()
    
    return cleaned_text

def clean_shan_text(text, keep_numbers=True):
    
    text = remove_emojis(text)

    text = text.replace("၊", "၊ ").replace("။", "။ ").replace(" ၊", "၊ ").replace(" ။", "။ ").strip()
    text = re.sub(r"ႉ{2,}", "ႉ", text)
    text = text.replace("ႆၢ", "ၢႆ")
    text = text.replace("ေတ", "တေ")

    text = remove_latin_text(text)
    text = remove_myanmar_text(text)
    
    # Latin Numbers
    numbers = r"0-9" if keep_numbers else ""
    text = re.sub(rf'[^{numbers}{shan_characters}\s]', '', text)
    
    return text

def get_font_name(line_count, total_count):
    fonts = ["GreatHorKham Taunggyi", "Myanmar Text", "PangLong Italic", "Pyidaungsu", "Shan"]
    num_fonts = len(fonts)
    
    range_size = total_count // num_fonts
    
    font_ranges = [(i * range_size, (i + 1) * range_size, fonts[i]) for i in range(num_fonts)]
    
    for min_val, max_val, font in font_ranges:
        if min_val <= line_count < max_val:
            return font
    
    return "Shan"  # Default

def text2img_data_generator(training_text_file: str, output_directory: str, fonts_dir: str, count: int):

    lines = []

    with open(training_text_file, 'r') as input_file:
        for line in input_file.readlines():
            lines.append(line.strip())

    if not os.path.exists(output_directory):
        os.mkdir(output_directory)

    random.shuffle(lines)

    line_count = 0
    lines = lines[:count]

    for line in lines:
        line = line.strip()
        line = clean_shan_text(line)

        # remove short sentences
        if len(line) < 20:
            continue

        fonts_name = get_font_name(line_count, total_count=count)

        training_text_file_name = pathlib.Path(training_text_file).stem
        line_training_text = os.path.join(output_directory, f'{training_text_file_name}_{line_count}.gt.txt')
        with open(line_training_text, 'w') as output_file:
            output_file.writelines([line])

        file_base_name = f'{training_text_file_name}_{line_count}'

        subprocess.run([
            'text2image',
            f'--font={fonts_name}',
            f'--fonts_dir={fonts_dir}',
            f'--text={line_training_text}',
            f'--outputbase={output_directory}/{file_base_name}',
            '--max_pages=1',
            '--strip_unrenderable_words',
            '--leading=32',
            '--xsize=3600',
            '--ysize=480',
            '--char_spacing=1.0',
            '--exposure=0',
            '--unicharset_file=data/shn/unicharset'
        ])

        line_count += 1

def main():
    training_text_file = './shannews.txt'
    output_directory = "../data/shn-ground-truth"
    fonts_dir = '/home/noernova/Labs/tesstrain/shan-datasets/fonts'
    count = 250000

    text2img_data_generator(training_text_file, output_directory, fonts_dir, count)

if __name__ == "__main__":
    main()
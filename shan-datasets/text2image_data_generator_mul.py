import re
import os
import random
import pathlib
import subprocess
import multiprocessing
from shannlp import word_tokenize, shan_characters, shan_digits

# Precompile regex for better performance
EMOJI_PATTERN = re.compile("["
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
    "]", re.UNICODE)

LATIN_PATTERN = re.compile(r"[^\u1000-\u109f0-9\s/\-\"']")
MULTI_SPACE_PATTERN = re.compile(r"\s+")
DUPLICATE_MARK_PATTERN = re.compile(r"ႉ{2,}")

ALLOWED_CHARS = set(shan_characters + shan_digits + "/-'\"")

FONTS = ["GreatHorKham Taunggyi", "Myanmar Text", "PangLong Italic", "Pyidaungsu", "Shan"]
NUM_FONTS = len(FONTS)

def remove_emojis(text):
    return EMOJI_PATTERN.sub('', text)

def remove_latin_text(text):
    return MULTI_SPACE_PATTERN.sub(" ", LATIN_PATTERN.sub('', text))

def remove_myanmar_text(text):
    return "".join(word for word in word_tokenize(text, engine="newmm")
                    if all(c in ALLOWED_CHARS or c.isspace() or c.isnumeric() for c in word)).strip()

def clean_shan_text(text, keep_numbers=True):
    text = remove_emojis(text)
    text = text.replace("၊", "၊ ").replace("။", "။ ").strip()
    text = DUPLICATE_MARK_PATTERN.sub("ႉ", text)
    text = text.replace("ႆၢ", "ၢႆ").replace("ေတ", "တေ")
    text = remove_latin_text(text)
    text = remove_myanmar_text(text)
    return text if keep_numbers else re.sub(rf'[^{shan_characters}\s]', '', text)

def get_font_name(index, total_count):
    return FONTS[(index * NUM_FONTS) // total_count]

def process_line(args):
    line, line_count, output_directory, fonts_dir, training_text_file_name, total_count = args
    
    cleaned_line = clean_shan_text(line)
    if len(cleaned_line) < 20:
        return  # Skip short sentences
    
    font_name = get_font_name(line_count, total_count)
    file_base_name = f'{training_text_file_name}_{line_count}'
    line_file = os.path.join(output_directory, f'{file_base_name}.gt.txt')
    
    with open(line_file, 'w') as f:
        f.write(cleaned_line)
    
    subprocess.run([
        'text2image',
        f'--font={font_name}',
        f'--fonts_dir={fonts_dir}',
        f'--text={line_file}',
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

def text2img_data_generator(training_text_file, output_directory, fonts_dir, count):
    os.makedirs(output_directory, exist_ok=True)
    
    with open(training_text_file, 'r') as file:
        lines = [line.strip() for line in file if len(line.strip()) >= 20]
    
    random.shuffle(lines)
    lines = lines[:count]
    
    training_text_file_name = pathlib.Path(training_text_file).stem
    
    with multiprocessing.Pool() as pool:
        pool.map(process_line, [(line, i, output_directory, fonts_dir, training_text_file_name, count)
                                for i, line in enumerate(lines)])

def main():
    text2img_data_generator(
        training_text_file='./shannews.txt',
        output_directory="../data/shn-ground-truth",
        fonts_dir='/home/noernova/Desktop/Labs/tesstrain/shan-datasets/fonts',
        count=300000
    )

if __name__ == "__main__":
    main()

import time
from OCRDataGenerator import OCRDataGenerator
from datasets import load_dataset
import re
import unicodedata
from shannlp import word_tokenize, shan_characters

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
    text = re.sub(r"[^\u1000-\u109f\s]", '', text)
    text = re.sub(r"\s+", " ", text)
    return text

def remove_myanmar_text(text):
    tokens = word_tokenize(text, engine="newmm")
    cleaned_words = []
    for word in tokens:
        is_shan_word = True
        for char in word:
            if char not in shan_characters and not char.isspace():
                is_shan_word = False
                break
        if is_shan_word:
            cleaned_words.append(word)
    
    cleaned_text = "".join(cleaned_words)
    
    cleaned_text = re.sub(r'\s+', ' ', cleaned_text).strip()
    
    return cleaned_text

def clean_shan_text(text, keep_numbers=False):
    # Normalize Unicode
    text = unicodedata.normalize("NFC", text)
    
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

def split_shan_chunks(text, min_len=20, max_len=50):
    # Initial text preprocessing
    text = clean_shan_text(text)
    text = text.replace("၊", "၊ ").replace("။", "။ ").replace(" ၊", "၊ ").replace(" ။", "။ ").strip()

    tokens = word_tokenize(text, engine="newmm")
    
    chunks = []
    current_chunk = []
    current_length = 0
    
    for token in tokens:
        token_len = len(token)
        
        # If adding token exceeds max_len, finalize current chunk
        if current_length + token_len > max_len and current_chunk:
            # If current chunk is too short, try to merge with previous
            if current_length < min_len and chunks:
                last_chunk = chunks.pop()
                chunks.append(last_chunk + ' ' + ''.join(current_chunk))
            else:
                chunks.append(''.join(current_chunk))
            current_chunk = [token]
            current_length = token_len
        else:
            # Add token to current chunk
            current_chunk.append(token)
            current_length += token_len
            
            # If we hit max_len exactly or have a good split point
            if (current_length >= min_len and token in (' ', '။')) or current_length == max_len:
                chunks.append(''.join(current_chunk))
                current_chunk = []
                current_length = 0
    
    # Handle remaining tokens
    if current_chunk:
        if current_length < min_len and chunks:
            last_chunk = chunks.pop()
            chunks.append(last_chunk + ' ' + ''.join(current_chunk))
        else:
            chunks.append(''.join(current_chunk))
    
    # Clean up whitespace in chunks
    chunks = [re.sub(r'\s+', ' ', chunk.strip()) for chunk in chunks if chunk.strip()]
    
    # Final validation pass
    final_chunks = []
    i = 0
    while i < len(chunks):
        current = chunks[i]
        
        # If chunk exceeds max_len, force split at last valid space
        if len(current) > max_len:
            split_idx = max_len
            while split_idx > 0 and current[split_idx] not in (' ', '။'):
                split_idx -= 1
            if split_idx > min_len:
                final_chunks.append(current[:split_idx].strip())
                chunks.insert(i + 1, current[split_idx:].strip())
            else:
                final_chunks.append(current)
        else:
            final_chunks.append(current)
        i += 1
    
    return final_chunks

def generate_images_from_huggingface(dataset_repo, chunk_size, fonts, output_dir):
    generator = OCRDataGenerator(font_paths=fonts)
    chunk_count = 0
    
    # Load dataset from Hugging Face
    dataset = load_dataset(dataset_repo, split="train")
    contents = dataset["content"]

    print("Generate images...")
    for content in contents:
        content = content.strip()
        content = clean_shan_text(content, keep_numbers=True)

        texts = split_shan_chunks(content)

        for text in texts:
            if len(text) < 1:
                continue
            
            text = re.sub(r"(^။)|(^၊)", "", text) # remove start ၊, ။
            text = text.strip()

            image, metadata = generator.generate_image(
                text=text,
                min_font_size=24,
                max_font_size=48,
                horizontal_padding=40,
                vertical_padding=20,
                min_height=64,
                add_noise=True,
                random_transform=False
            )
            print(f"Text: {text}")
            print(f"Image size: {metadata['image_size']}\n")

            ts = time.time()

            # Save TIF
            image.save(f"{output_dir}/{ts}.tif")

            # Save TXT
            with open(f"{output_dir}/{ts}.gt.txt", "w", encoding='utf-8') as text_file:
                text_file.write(text)

            print(f"Saved image for word: {text}")

            chunk_count += 1
            print(f"chunk size: {chunk_count}")

            if chunk_count > chunk_size:
                return
        
        print(f"Total chunk size: {chunk_count}")

def main():
    output_dir = "../data/shn-ground-truth"
    fonts = [
        "fonts/Shan.ttf",
        "fonts/PangLong.ttf",
        "fonts/GreatHorKham_Taunggyi.ttf",
        "fonts/mmrtext.ttf",
        "fonts/Pyidaungsu.ttf"
    ]

    huggingface_datasets_repo = [
        "NorHsangPha/shan-novel-tainovel_com",
        "NorHsangPha/shan-news-shannews_org",
        "NorHsangPha/shan-news-taifreedom_com",
        "NorHsangPha/shan-news-shanhumanrights_org",
        "NorHsangPha/shan-news-ssppssa_org",
    ]

    chunk_size = 50000 # for each repo

    for repo in huggingface_datasets_repo:
        generate_images_from_huggingface(dataset_repo=repo, chunk_size=chunk_size, fonts=fonts, output_dir=output_dir)

if __name__ == "__main__":
    main()
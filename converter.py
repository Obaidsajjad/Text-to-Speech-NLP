from googletrans import LANGUAGES,Translator
import os
from gtts import gTTS
import streamlit as st
from langchain_community.document_loaders import WebBaseLoader
from PyPDF2 import PdfReader
import re
from bs4 import BeautifulSoup
from deep_translator import GoogleTranslator
import requests
import docx

def translate_text(text="type",src="en", dest="en"):
    translator = GoogleTranslator(source=src, target=dest)

    text_chunks = split_text(text, max_chars=5000)
    
    # Translate each chunk
    translated_chunks = [translator.translate(chunk) for chunk in text_chunks]
    
    # Join the translated chunks back together
    translated_text = ' '.join(translated_chunks)

    # print("Translation completed")
    return translated_text

def clean_html_content(html_content):
    # Use BeautifulSoup to parse the HTML content
    soup = BeautifulSoup(html_content, 'html.parser')

    # Remove unwanted elements like headers, navigation links, images, and footers
    for unwanted_tag in soup(['header', 'nav', 'footer', 'img', 'script', 'style', 'aside']):
        unwanted_tag.decompose()

    # You can also remove any anchor tags <a> but keep the text
    for link in soup.find_all('a'):
        link.unwrap()

    # Get only the text from the soup (cleaned)
    cleaned_text = soup.get_text(separator=' ', strip=True)
    return cleaned_text

language_code_mapping = {
    'auto':'auto',      'afrikaans': 'af',      'albanian': 'sq',       'amharic': 'am',        'arabic': 'ar',     'basque': 'eu',   
    'bengali': 'bn',    'bosnian': 'bs',        'bulgarian': 'bg',      'catalan': 'ca',        'chinese (simplified)': 'zh-CN',    
    'chinese (traditional)': 'zh-TW',           'croatian': 'hr',       'czech': 'cs',          'danish': 'da',     'dutch': 'nl',    
    'english': 'en',    'estonian': 'et',       'filipino': 'tl',       'finnish': 'fi',        'french': 'fr',     'galician': 'gl',  
    'german': 'de',     'greek': 'el',          'gujarati': 'gu',       'hausa': 'ha',          'hindi': 'hi',      'hungarian': 'hu',
    'icelandic': 'is',  'indonesian': 'id',     'italian': 'it',        'japanese': 'ja',       'javanese': 'jv',   'kannada': 'kn',  
    'khmer': 'km',      'korean': 'ko',         'latin': 'la',          'latvian': 'lv',        'lithuanian': 'lt', 'malagasy': 'mg',
    'malay': 'ms',      'malayalam': 'ml',      'maori': 'mi',          'marathi': 'mr',        'nepali': 'ne',     'norwegian': 'no',
    'polish': 'pl',     'portuguese': 'pt',     'punjabi': 'pa',        'romanian': 'ro',       'russian': 'ru',    'serbian': 'sr',
    'sinhala': 'si',    'slovak': 'sk',         'spanish': 'es',        'sundanese': 'su',      'swahili': 'sw',    'swedish': 'sv',   
    'tamil': 'ta',      'telugu': 'te',         'thai': 'th',           'turkish': 'tr',        'ukrainian': 'uk',  'urdu': 'ur',  
    'vietnamese': 'vi',    'welsh': 'cy',
    }

def split_text(text, max_chars=5000):
    """Splits the text into chunks of max_chars length."""
    chunks = []
    while len(text) > max_chars:
        # Find the last space within the max_chars limit to avoid cutting words
        split_index = text[:max_chars].rfind(' ')
        if split_index == -1:  # No space found, force split at max_chars
            split_index = max_chars
        chunks.append(text[:split_index])
        text = text[split_index:].strip()  # Remove the chunk and strip leading spaces
    if text:
        chunks.append(text)  # Append the last remaining part
    return chunks

def get_translated_txt(text,source,dest):
    
    # Fetch the language code from the dictionary
    destination_lang_code = language_code_mapping.get(dest.lower())
    
    if destination_lang_code is None:
        st.error("Language Error")
        return

    get_text = translate_text(text=text,src=source, dest=dest)
    st.write("Translation Done...")
    # Convert translated text to speech using the short code
    tts = gTTS(text=get_text, lang=destination_lang_code,tld="co.in", slow=False)
    audio_file = "output.mp3"
    tts.save(audio_file)

    st.audio("output.mp3", format="audio/mpeg", loop=False,autoplay=True)
    return get_text


#__________________________________________________________________
def get_files_text(file):
    text = ""
    filename=file.name
    file_ext=filename.split('.')[1]

    if file.name.endswith(".pdf"):
        text += get_pdf_text(file)
    elif file.name.endswith(".docx"):
        text += get_docx_text(file)
    elif file.name.endswith(".csv"):
        text += get_csv_text(file)
    return text

def get_pdf_text(pdf_file):
    text = ""
    pdf_reader = PdfReader(pdf_file)
    for page in pdf_reader.pages:
        text += page.extract_text()
    return text

def get_docx_text(docxs):
    all_text = []
    doc = docx.Document(docxs)
    for para in doc.paragraphs:
        all_text.append(para.text)
    text = ''.join(all_text)
    return text

def get_csv_text():
    return "a"

#_________________________________________________________________________________--

def read_url(url):
    if not url:
        st.error("URL cannot be empty.")
    
    # Check if the URL starts with http:// or https://, otherwise raise an error
    if not re.match(r"^(http|https)://", url):
        st.error("Invalid URL scheme. The URL must start with http:// or https://")

    loader = WebBaseLoader(url)
    # web_pages = loader.load()
    # text = web_pages[0].page_content.replace("\n", " ")
    # text=text.replace("\t", " ")
    # cleaned_text = clean_html_content(text)

    documents = loader.load()
    
    # Fetch raw HTML content from the website
    raw_html = requests.get(url).text
    
    # Clean the HTML content using BeautifulSoup
    cleaned_content = clean_html_content(raw_html)
    # print(type(text))
    return cleaned_content
#_____________________________________________________________________________________________

def main():
    st.set_page_config(layout="wide")
    
    tab1, tab2, tab3 = st.tabs(["    Custom Text   ", "    Add a Document    ", "    Read a Website    "])

    with tab1:
        st.title("Converter")
        text_input = st.text_area(placeholder="Enter text Here", label="Enter Text to Listen")
        col1,col2=st.columns(2)
        with col1:
            source_lang=st.selectbox("Select Your Source Language.." ,(k for k,v in language_code_mapping.items()))
        with col2:
            dest_lang=st.selectbox("Select Your Destination Language.." ,(k for k,v in language_code_mapping.items()))
        # st.write(source_lang,dest_lang)
        if st.button("Convert to Speech"):
            text = get_translated_txt(text_input,source_lang, dest_lang)
            with st.expander("See explanation"):
                st.write(text)


    with tab2:
        st.title("Document Reader")
        file = st.file_uploader("Upload your Files to read",accept_multiple_files=False, type=['pdf','docx'])
        if file is not None:
            with st.spinner():
                text = get_files_text(file)
                # st.write(type(text))
                with st.expander("Origional Text"):
                    st.write(text)
        col1,col2=st.columns(2)
        with col1:
            source_lang=st.selectbox("Select Your Source Language" ,(k for k,v in language_code_mapping.items()))
        with col2:
            dest_lang=st.selectbox("Select Your Destination Language" ,(k for k,v in language_code_mapping.items()))
        # st.write(language_code_mapping.get(source_lang.lower()),language_code_mapping.get(dest_lang.lower()))
        
        if st.button("Convert"):
            text = get_translated_txt(text,source_lang, dest_lang)
            with st.expander("See explanation"):
                st.write(text)

    with tab3:
        st.title("Website reader")
        url = st.text_input(placeholder="Enter url Here", label="Enter URL to Listen")
        if url:
            text = read_url(url)
            # st.write(type(text))
            with st.expander("Original Text"):
                st.write(text)
        col1,col2=st.columns(2)
        with col1:
            source_lang=st.selectbox("Select Your Source Language." ,(k for k,v in language_code_mapping.items()))
        with col2:
            dest_lang=st.selectbox("Select Your Destination Language." ,(k for k,v in language_code_mapping.items()))
        # st.write(source_lang,dest_lang)
        
        if st.button("Translate"):
            texts = get_translated_txt(text,source_lang, dest_lang)
            with st.expander("See explanation"):
                st.write(texts)
    


if __name__ == "__main__":
    main()

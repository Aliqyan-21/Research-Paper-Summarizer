from flask import Flask, render_template, request, redirect
from werkzeug.utils import secure_filename
import os
import openai
import textwrap
import re
import time
from PyPDF2 import PdfReader

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'static/uploads'
app.config['ALLOWED_EXTENSIONS'] = {'pdf'}

def open_file(filepath):
    with open(filepath, 'r', encoding='latin-1') as infile:
        return infile.read().strip()

def save_file(content, filepath):
    with open(filepath, 'w', encoding='latin-1') as outfile:
        outfile.write(content)

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']

def set_openai_api_key(api_key):
    openai.api_key = api_key

def pdf_to_text(pdf_path):
    text = ""
    with open(pdf_path, 'rb') as file:
        reader = PdfReader(file)
        for page_num in range(len(reader.pages)):
            page = reader.pages[page_num]
            text += page.extract_text()
    return text

def gpt3_completion(prompt, engine='gpt-3.5-turbo', temp=0.6, top_p=1.0, tokens=2000, freq_pen=0.25, pres_pen=0.0, stop=['<<END>>']):
    max_retry = 1
    retry = 0
    while True:
        try:
            response = openai.Completion.create(
                engine=engine,
                prompt=prompt,
                temperature=temp,
                max_tokens=tokens,
                top_p=top_p,
                frequency_penalty=freq_pen,
                presence_penalty=pres_pen,
                stop=stop)
            text = response['choices'][0]['text'].strip() #type: ignore
            text = re.sub('\s+', ' ', text) #type: ignore
            return text
        except Exception as oops:
            retry += 1
            if retry >= max_retry:
                return "GPT3 error: %s" % oops
            time.sleep(20)

@app.route('/')
@app.route('/upload', methods=['GET', 'POST'])
def upload():
    if request.method == 'POST':
        if 'file' not in request.files:
            return redirect(request.url)
        file = request.files['file']
        if file.filename == '':
            return redirect(request.url)
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename) #type: ignore
            file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(file_path)

            # Convert PDF to text
            text = pdf_to_text(file_path)
            
            # Process text with GPT-3
            api_key = open_file('openaiapikey.txt')
            set_openai_api_key(api_key)
            chunks = textwrap.wrap(text, 2000)
            result = []
            for chunk in chunks:
                prompt = open_file('prompt.txt').replace('<<SUMMARY>>', chunk)
                prompt = prompt.encode(encoding='ASCII',errors='ignore').decode()
                summary = gpt3_completion(prompt)
                result.append(summary)
            summary_text = '\n\n'.join(result)
            
            # Save the result to a file (optional)
            save_file(summary_text, 'output1.txt')
            
            return render_template('result.html', summary=summary_text)
    return render_template("upload.html")

@app.route('/result')
def result():
    return render_template("result.html")

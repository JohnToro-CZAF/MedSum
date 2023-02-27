import os
import logging
from werkzeug.utils import secure_filename
from typing import List, Dict, Tuple, Set, Optional
from dotenv import load_dotenv

from flask import Flask, flash, request, request, jsonify, abort, send_from_directory
from flask_cors import CORS, cross_origin
from ariadne.constants import PLAYGROUND_HTML
from model import query

from DocReader import DocReader
from DocSummarizer import DocSummarizer


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger('HELLO WORLD')

INDEX_PATH = './'
UPLOAD_FOLDER = '/home/vishc1/projects/PNH/MedSum/database/documents'
RESOURCES_FOLDER = '/home/vishc1/projects/PNH/MedSum/database/resources'
ALLOWED_EXTENSIONS = set(['txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif'])
load_dotenv()
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
os.environ["OPENAI_API_KEY"] = OPENAI_API_KEY

app = Flask(__name__)
reader = DocReader(directory_path=UPLOAD_FOLDER, index_path=INDEX_PATH)
summarizer = DocSummarizer(documents_path=UPLOAD_FOLDER, resources_path=RESOURCES_FOLDER)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config["CLIENT_IMAGES"] = RESOURCES_FOLDER

@app.route('/upload', methods=['POST'])
@cross_origin()
def fileUpload():
    file = request.files['file'] 
    filename = secure_filename(file.filename)
    file.save(UPLOAD_FOLDER + "/" + filename)
    print("Reading file...")
    try:
        # TODO: We have to make this function asynchronous
        reader.construct_index()
    except:
        print("Error reading file... Aborting saving file")
        os.remove(UPLOAD_FOLDER + "/" + filename)
    
    print("Done reading file...")
    response = summarizer.get_summary(filename, reader)
    return response

@app.route("/handle_message", methods=['GET','POST'])
def handle_message() -> dict:
    message = request.json
    response = reader.predict(message['text'])
    return jsonify({"text": response})

@app.route("/handle_summary", methods=['POST'])
# @cross_origin()
def handle_summary() -> dict:
    message = request.json
    response = summarizer.retrieve_summary(message['file_name'])
    return response

# Get Image file Routing
@app.route("/images/<path:image_name>", methods = ['GET'])
@cross_origin()
def get_image(image_name):
    dir_name, fn = image_name.split('*')
    if os.path.exists(app.config["CLIENT_IMAGES"] + '/' + dir_name + '/' + fn):
        print("bullshit")
    return send_from_directory(app.config["CLIENT_IMAGES"] + '/' + dir_name, path=fn, as_attachment=True)

@app.route("/graphql", methods=["GET"])
def graphql_playground():
    return PLAYGROUND_HTML, 200

if __name__ == "__main__":
    app.secret_key = os.urandom(24)
    cors = CORS(app, expose_headers='Authorization')
    app.config['CORS_HEADERS'] = 'Content-Type'
    app.run(debug=True, host="0.0.0.0", use_reloader=False, port=4949)
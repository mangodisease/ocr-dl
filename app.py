from flask import Flask, request
from flask_cors import CORS
from PIL import Image
import os
import easyocr
import numpy as np
import cv2
from io import BytesIO
import json
import pp


app = Flask(__name__)
cors = CORS(app, resources={r"/*": {"origins": "*"}})

@app.route("/ping", methods=['GET'])
def ping():
    return "Hello, I am alive", 200

@app.route("/process", methods=["POST"])
def process():
    if 'file' not in request.files:
        return 'No file provided', 400
    file = request.files['file']
    if file.filename == '':
        return 'Invalid file', 400
    upload_dir = 'images'  # Replace with the desired upload directory
    file.save(os.path.join(upload_dir, file.filename))
    upload_url = f"https://csu-dl-api.onrender.com/uploads/{file.filename}"  # Replace with the appropriate URL
    return upload_url, 200

@app.route("/ocr", methods=['POST'])
def ocr():
    try:
        image = request.files['file'].read()
        uploaded = np.fromstring(image, np.uint8)
        id = cv2.imdecode(np.frombuffer(uploaded, np.uint8), 1)

        # Convert the image to RGB format
        Extrat = cv2.cvtColor(id, cv2.COLOR_BGR2RGB)#.COLOR_BGR2GRAY
        reader = easyocr.Reader(['en'])#, gpu = True
        results = reader.readtext(Extrat, detail=1, paragraph=False)
        obj = {}

        #index intefier / not accurate
        """
        keys = [
            {"i": 6, "title": "Name"}, {"i": 12, "title": "Nationality"},
            {"i": 13, "title": "Sex"}, {"i": 14, "title": "Date of Birth"},
            {"i": 15, "title": "Weight"}, {"i": 16, "title": "Height"},
            {"i": 18, "title": "Address"}, {"i": 19, "title": "Address"},
            {"i": 23, "title": "License No"}, {"i": 24, "title": "Expiry Date"},
            {"i": 25, "title": "Agency Code"}, {"i": 29, "title": "Blood Type"},
            {"i": 30, "title": "Eyes Color"}, {"i": 15, "title": "DL Codes"}
        ]
        
        for j in keys:
            val = results[j["i"]]
            obj[j['title']] = str(results[j["i"]][1])
        """
        #Patter sequence / some of values are not properly render if image is not good
        for i, el in enumerate(results):
            val = str(el[1]).upper()
            if "MIDDLE NAME" in val:
                obj["Name"] = str(results[i + 1][1]).upper()
            elif "HEIGHT" in val:
                obj["Nationality"] = str(results[i + 1][1]).upper()
                #sequence after nationality
                obj["Sex"] = str(results[i + 2][1]).upper()
                obj["Date of Birth"] = str(results[i + 3][1]).upper()
                obj["Weight"] = str(results[i + 4][1]).upper()
                obj["Height"] = str(results[i + 5][1]).upper()
            elif "ADDRESS" in val:
                obj["Address"] = str("{} {}").format(results[i + 1][1], results[i + 2][1]).upper()
            elif "AGENCY CODE" in val:
                obj["License No"] = str(results[i + 1][1]).upper()
            elif "EXPIRY DATE" in val:
                obj["Expiry Date"] = str(results[i +1][1]).upper()
            
        return json.dumps(obj), 200
    except:
        return "notOK", 400

if __name__ == "__main__":
	app.run(host="0.0.0.0", port="8080", debug=True)
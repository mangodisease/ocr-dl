from flask import Flask, request, jsonify
import pytesseract
from PIL import Image
import io

app = Flask(__name__)

@app.route('/ocr', methods=['POST'])
def ocr():
    # Get the uploaded image file
    file = request.files['file']

    # Read the image using PIL
    image = Image.open(io.BytesIO(file.read()))

    # Perform OCR using pytesseract
    text = pytesseract.image_to_string(image)

    # Return the extracted text as JSON response
    return jsonify({'text': text})

if __name__ == '__main__':
    app.run()

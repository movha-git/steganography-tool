from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
from stego import encode_message, decode_message
from PIL import Image
import os
import uuid

app = Flask(__name__)
CORS(app)

UPLOAD_FOLDER = 'uploads'
OUTPUT_FOLDER = 'outputs'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(OUTPUT_FOLDER, exist_ok=True)


def convert_to_png(image_path):
    """Convert any image format to PNG so steganography works correctly"""
    img = Image.open(image_path).convert('RGB')
    png_path = image_path.rsplit('.', 1)[0] + '_converted.png'
    img.save(png_path, 'PNG')
    return png_path


@app.route('/encode', methods=['POST'])
def encode():
    if 'image' not in request.files:
        return jsonify({'error': 'No image uploaded'}), 400

    image   = request.files['image']
    message = request.form.get('message', '').strip()

    if not message:
        return jsonify({'error': 'No message provided'}), 400

    # Save uploaded image
    ext            = image.filename.rsplit('.', 1)[-1].lower()
    input_filename = f"{uuid.uuid4().hex}.{ext}"
    input_path     = os.path.join(UPLOAD_FOLDER, input_filename)
    image.save(input_path)

    # Always convert to PNG before encoding
    try:
        png_path = convert_to_png(input_path)
    except Exception as e:
        return jsonify({'error': f'Could not read image: {str(e)}'}), 400

    output_filename = f"{uuid.uuid4().hex}_output.png"
    output_path     = os.path.join(OUTPUT_FOLDER, output_filename)

    try:
        result = encode_message(png_path, message, output_path)
        return jsonify({
            'success':  True,
            'message':  result,
            'download': output_filename
        })
    except ValueError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        return jsonify({'error': f'Encoding failed: {str(e)}'}), 500


@app.route('/decode', methods=['POST'])
def decode():
    if 'image' not in request.files:
        return jsonify({'error': 'No image uploaded'}), 400

    image    = request.files['image']
    ext      = image.filename.rsplit('.', 1)[-1].lower()
    filename = f"{uuid.uuid4().hex}.{ext}"
    path     = os.path.join(UPLOAD_FOLDER, filename)
    image.save(path)

    # Convert to PNG before decoding
    try:
        png_path = convert_to_png(path)
    except Exception as e:
        return jsonify({'error': f'Could not read image: {str(e)}'}), 400

    try:
        hidden_message = decode_message(png_path)
        return jsonify({
            'success':        True,
            'hidden_message': hidden_message
        })
    except Exception as e:
        return jsonify({'error': f'Decoding failed: {str(e)}'}), 500


@app.route('/download/<filename>', methods=['GET'])
def download(filename):
    path = os.path.join(OUTPUT_FOLDER, filename)
    if os.path.exists(path):
        return send_file(path, as_attachment=True, download_name='hidden_image.png')
    return jsonify({'error': 'File not found'}), 404


@app.route('/ping', methods=['GET'])
def ping():
    return jsonify({'status': 'Server is running'})


if __name__ == '__main__':
    app.run(debug=True, port=5002)
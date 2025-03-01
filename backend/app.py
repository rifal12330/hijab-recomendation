import os
import cv2
import numpy as np
from flask import Flask, request, jsonify
from sklearn.ensemble import RandomForestClassifier
import pickle
from sklearn.cluster import KMeans
from flask_cors import CORS  # Import CORS


# Inisialisasi Flask app
app = Flask(__name__)
CORS(app)  # Aktifkan CORS untuk semua route


# Muat model yang sudah dilatih
MODEL_PATH = "backend/model/skin_tone_model.pkl"
with open(MODEL_PATH, 'rb') as f:
    model = pickle.load(f)  # Memuat model langsung

# Fungsi untuk ekstraksi warna kulit menggunakan K-Means
def extract_skin_color(image_path, k=5):
    image = cv2.imread(image_path)
    
    if image is None:
        print(f"Gambar tidak ditemukan: {image_path}")
        return [0, 0, 0]  # Mengembalikan warna default (hitam)

    image = cv2.resize(image, (100, 100))
    image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
    image = image.reshape(-1, 3)

    kmeans = KMeans(n_clusters=k, random_state=42)
    kmeans.fit(image)
    dominant_color = kmeans.cluster_centers_[0]
    return dominant_color

# Fungsi untuk mendapatkan rekomendasi hijab
def get_hijab_recommendation(rgb, tone):
    r, g, b = rgb
    if tone == 'Light':
        if r > g and r > b:  # Warna hangat
            return {'color': 'Light Blue', 'type': 'Pashmina'}
        else:  # Warna dingin
            return {'color': 'Soft Pink', 'type': 'Instan'}
    elif tone == 'Medium':
        if r > g and r > b:  # Warna hangat
            return {'color': 'Bold Red', 'type': 'Segi Empat'}
        else:  # Warna dingin
            return {'color': 'Navy Blue', 'type': 'Pashmina'}
    else:
        return {'color': 'Unknown', 'type': 'Unknown'}

# Endpoint untuk prediksi warna kulit dan tone
@app.route('/predict', methods=['POST'])
def predict():
    try:
        # Ambil file gambar dari request
        if 'file' not in request.files:
            return jsonify({"error": "Tidak ada file yang diunggah"}), 400

        file = request.files['file']
        if file.filename == '':
            return jsonify({"error": "File tidak dipilih"}), 400

        # Simpan file sementara
        file_path = os.path.join("temp", file.filename)
        os.makedirs("temp", exist_ok=True)
        file.save(file_path)

        # Ekstraksi warna kulit
        skin_color = extract_skin_color(file_path)
        os.remove(file_path)  # Hapus file sementara setelah diproses

        # Prediksi tone menggunakan model
        input_data = np.array([skin_color])  # Format: [[R, G, B]]
        tone = model.predict(input_data)[0]  # Prediksi tone (Light/Medium)

        # Siapkan respons
        response = {
            "skin_color_rgb": skin_color.tolist(),  # Konversi ke list
            "predicted_tone": tone
        }
        return jsonify(response), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Endpoint untuk rekomendasi hijab
@app.route('/recommend', methods=['POST'])
def recommend():
    try:
        # Ambil data dari request
        data = request.json
        if not data or 'skin_color_rgb' not in data or 'predicted_tone' not in data:
            return jsonify({"error": "Data tidak valid"}), 400

        # Dapatkan rekomendasi hijab
        recommendation = get_hijab_recommendation(data['skin_color_rgb'], data['predicted_tone'])

        # Siapkan respons
        response = {
            "recommendation": recommendation
        }
        return jsonify(response), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Jalankan aplikasi Flask
if __name__ == '__main__':
    app.run(debug=True)
import cv2
import numpy as np
from sklearn.cluster import KMeans

def extract_skin_color(image_path, k=5):
    """
    Mengekstraksi warna kulit dominan dari gambar menggunakan K-Means.
    """
    image = cv2.imread(image_path)
    if image is None:
        raise ValueError(f"Gambar tidak ditemukan: {image_path}")

    # Resize dan reshape gambar
    image = cv2.resize(image, (100, 100))
    image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
    image = image.reshape(-1, 3)

    # Ekstraksi warna dominan menggunakan K-Means
    kmeans = KMeans(n_clusters=k, random_state=42)
    kmeans.fit(image)
    dominant_color = kmeans.cluster_centers_[0]  # Warna dominan pertama
    return dominant_color
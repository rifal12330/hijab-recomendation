<template>
  <div id="app">
    <h1>Ambil Gambar untuk Rekomendasi Hijab</h1>

    <!-- Tombol untuk membuka kamera -->
    <button @click="openCamera">Buka Kamera</button>

    <!-- Video untuk menampilkan kamera -->
    <video ref="video" autoplay style="display: none;"></video>

    <!-- Tombol untuk mengambil gambar -->
    <button @click="captureImage" v-if="isCameraOpen">Ambil Gambar</button>

    <!-- Tampilkan gambar yang diambil -->
    <div v-if="imagePreview">
      <img :src="imagePreview" alt="Preview Gambar" style="max-width: 100%; height: auto;">
      <button @click="uploadImage">Dapatkan Rekomendasi</button>
    </div>

    <!-- Tampilkan loading -->
    <div v-if="loading" style="margin: 20px 0;">
      <p>Memproses gambar...</p>
    </div>

    <!-- Tampilkan hasil prediksi -->
    <div v-if="result">
      <h2>Hasil Prediksi:</h2>
      <p>Predicted Tone: {{ result.predicted_tone }}</p>
    </div>

    <!-- Tampilkan rekomendasi hijab -->
    <div v-if="recommendation">
      <h2>Rekomendasi Hijab:</h2>
      <p>Warna: {{ recommendation.color }}, Jenis: {{ recommendation.type }}</p>
    </div>

    <!-- Tampilkan pesan error -->
    <div v-if="error" style="color: red;">
      <p>{{ error }}</p>
    </div>
  </div>
</template>

<script>
export default {
  data() {
    return {
      isCameraOpen: false,      // Apakah kamera terbuka
      imagePreview: null,       // Gambar yang diambil dari kamera
      result: null,             // Hasil prediksi dari backend
      recommendation: null,     // Rekomendasi hijab dari backend
      error: null,              // Pesan error
      loading: false,           // Apakah sedang memproses
    };
  },
  methods: {
    // Buka kamera
    async openCamera() {
      try {
        const stream = await navigator.mediaDevices.getUserMedia({ video: true });
        const video = this.$refs.video;
        video.srcObject = stream;
        video.style.display = "block";
        this.isCameraOpen = true;
      } catch (err) {
        this.error = "Tidak dapat mengakses kamera. Pastikan Anda memberikan izin.";
        console.error("Error mengakses kamera:", err);
      }
    },
    // Ambil gambar dari kamera
    captureImage() {
      const video = this.$refs.video;
      const canvas = document.createElement("canvas");
      canvas.width = video.videoWidth;
      canvas.height = video.videoHeight;
      const context = canvas.getContext("2d");
      context.drawImage(video, 0, 0, canvas.width, canvas.height);

      // Konversi canvas ke data URL (format gambar)
      this.imagePreview = canvas.toDataURL("image/png");

      // Matikan kamera
      this.isCameraOpen = false;
      video.srcObject.getTracks().forEach(track => track.stop());
      video.style.display = "none";
    },
    // Kirim gambar ke backend untuk prediksi dan rekomendasi
    async uploadImage() {
      if (!this.imagePreview) {
        this.error = "Silakan ambil gambar terlebih dahulu.";
        return;
      }

      this.loading = true;
      this.error = null;
      this.result = null;
      this.recommendation = null;

      try {
        // Konversi data URL ke Blob
        const response = await fetch(this.imagePreview);
        const blob = await response.blob();

        // Kirim gambar ke endpoint /predict
        const formData = new FormData();
        formData.append("file", blob, "capture.png");

        const predictResponse = await fetch("http://127.0.0.1:5000/predict", {
          method: "POST",
          body: formData,
        });

        if (!predictResponse.ok) {
          throw new Error(`Error: ${predictResponse.status} - ${predictResponse.statusText}`);
        }

        const predictData = await predictResponse.json();
        this.result = predictData;

        // Kirim hasil prediksi ke endpoint /recommend
        const recommendResponse = await fetch("http://127.0.0.1:5000/recommend", {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
          },
          body: JSON.stringify({
            skin_color_rgb: predictData.skin_color_rgb,
            predicted_tone: predictData.predicted_tone,
          }),
        });

        if (!recommendResponse.ok) {
          throw new Error(`Error: ${recommendResponse.status} - ${recommendResponse.statusText}`);
        }

        const recommendData = await recommendResponse.json();
        this.recommendation = recommendData.recommendation;
      } catch (err) {
        this.error = err.message;
      } finally {
        this.loading = false;
      }
    },
  },
};
</script>

<style>
#app {
  font-family: Avenir, Helvetica, Arial, sans-serif;
  text-align: center;
  margin-top: 60px;
}

button {
  padding: 10px 20px;
  background-color: #42b983;
  color: white;
  border: none;
  border-radius: 5px;
  cursor: pointer;
  margin: 10px;
}

button:hover {
  background-color: #369f6e;
}

video {
  max-width: 100%;
  height: auto;
  border-radius: 10px;
  margin: 20px 0;
}

img {
  border-radius: 10px;
  box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
  margin: 20px 0;
}

.error {
  color: red;
  margin-top: 20px;
}
</style>
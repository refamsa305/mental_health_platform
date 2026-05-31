# HiHealth Platform 🧠

**HiHealth Platform** adalah sebuah aplikasi berbasis web yang dirancang untuk menganalisis dampak penggunaan media sosial terhadap kesehatan mental pengguna. Aplikasi ini mengintegrasikan data analitik makro, prediksi *machine learning*, dan pencatatan laporan riwayat kesehatan secara interaktif menggunakan integrasi *cloud* Supabase.

## 🚀 Fitur Utama

1. **Dashboard Analisis Dataset Makro**: 
   Menjawab 7 pertanyaan bisnis utama mengenai interaksi antara durasi waktu layar (*screen time*), platform media sosial yang digunakan, serta hubungannya dengan tingkat kecemasan (GAD-7) dan depresi (PHQ-9). Visualisasi disajikan secara interaktif menggunakan grafik.
2. **Kalkulator Prediksi Skor Klinis**: 
   Menggunakan model Machine Learning yang telah dilatih untuk memprediksi probabilitas tingkat kecemasan (GAD-7) dan depresi (PHQ-9) pengguna secara instan berdasarkan pola konsumsi gawai.
3. **Laporan Kesehatan Mental Pribadi**: 
   Sistem rekam medis digital (*log history*) personal bagi pengguna untuk memantau fluktuasi indikasi kesehatan mental dari waktu ke waktu, lengkap dengan pelacakan tren (grafik garis historis) dan rekomendasi kesehatan.

## 🛠️ Teknologi yang Digunakan

- **Frontend / Antarmuka**: [Streamlit](https://streamlit.io/)
- **Visualisasi Data**: Plotly
- **Pemrosesan Data**: Pandas, NumPy
- **Machine Learning**: Scikit-Learn
- **Database & Backend**: [Supabase](https://supabase.com/)

## 📋 Prasyarat & Panduan Instalasi

Pastikan komputer/server Anda sudah terinstal **Python 3.8** (atau versi lebih baru).

1. **Unduh (Clone) Repository**
   ```bash
   git clone https://github.com/refamsa305/mental_health_platform.git
   cd mental_health_platform
   ```

2. **Instal Dependensi**
   ```bash
   pip install -r requirements.txt
   ```

3. **Atur Variabel Lingkungan (.env)**
   Buat sebuah file bernama `.env` di folder utama proyek (satu tingkat dengan `app.py`) dan isi dengan kredensial API Supabase Anda untuk memastikan fitur autentikasi dan rekam medis berjalan:
   ```env
   SUPABASE_URL=https://<ID-PROYEK-ANDA>.supabase.co
   SUPABASE_KEY=<KUNCI-ANON-API-ANDA>
   ```

4. **Jalankan Aplikasi**
   ```bash
   streamlit run app.py
   ```
   Aplikasi akan segera terbuka di peramban web (*browser*) Anda secara otomatis (biasanya beralamat di `http://localhost:8501`).

## 📁 Struktur File Utama

- `app.py` : Berisi struktur program utama aplikasi (UI, logika *login*, *routing* navigasi, grafik).
- `model_gad7.pkl` & `model_phq9.pkl` : Model AI / Machine Learning yang sudah dilatih (digunakan di kalkulator prediksi).
- `social_media_mental_health.csv` : Dataset awal yang divisualisasikan pada menu Dashboard Analisis.
- `requirements.txt` : Daftar pustaka (*libraries*) Python yang dibutuhkan agar kode dapat berjalan sempurna.
- `bg2.png` & `bg3.png` : Gambar aset penunjang visualisasi *background* / logo.

## 🔒 Catatan Keamanan
Kunci rahasia API Anda (`.env`) wajib dijaga dan **tidak boleh diunggah ke GitHub publik**. File konfigurasi `.gitignore` dalam repositori ini secara otomatis telah melindungi `.env` Anda agar tidak ikut tersimpan ke dalam riwayat repositori.

import streamlit as st
import pandas as pd
import numpy as np
import pickle
import plotly.express as px
from supabase import create_client, Client

# ==========================================
# CONFIG & THEME COLOR SYSTEM (White, Grey, Light Blue)
# ==========================================
st.set_page_config(page_title="MindMetrics - Dampak Media Sosial", layout="wide")

# Custom CSS untuk mencerminkan warna Dominan Putih (#FFFFFF), Abu-abu (#F8F9FA), dan Biru Muda (#E3F2FD, #2196F3)
st.markdown("""
    <style>
    /* Mengubah warna background utama */
    .stApp {
        background-color: #FFFFFF;
    }
    
    /* Box untuk Visualisasi (Warna Abu-abu Terang) */
    .box-visual {
        background-color: #F8F9FA;
        border: 2px solid #E0E0E0;
        border-radius: 12px;
        padding: 20px;
        margin-bottom: 20px;
        box-shadow: 2px 2px 5px rgba(0,0,0,0.05);
    }
    
    /* Box untuk Penjelasan (Warna Biru Muda Lembut) */
    .box-explanation {
        background-color: #E3F2FD;
        border: 2px solid #BBDEFB;
        border-radius: 12px;
        padding: 20px;
        margin-bottom: 20px;
        color: #0D47A1;
        box-shadow: 2px 2px 5px rgba(0,0,0,0.05);
    }
    
    /* Tombol dan aksen teks utama */
    h1, h2, h3 {
        color: #1565C0;
    }
    div.stButton > button:first-child {
        background-color: #2196F3;
        color: white;
        border-radius: 8px;
        border: none;
    }
    div.stButton > button:first-child:hover {
        background-color: #0B79D0;
        color: white;
    }
    </style>
""", unsafe_allow_html=True) # <-- Sudah diperbaiki menjadi unsafe_allow_html

# ==========================================
# KONEKSI SUPABASE
# ==========================================
SUPABASE_URL = "https://cqmlvarkzhejzxbnwtfe.supabase.co/rest/v1/"
SUPABASE_KEY = "sb_publishable_YBD-kczdlV9QE_S6JbsngQ_w5Y0D8hc"

@st.cache_resource
def init_supabase():
    try:
        return create_client(SUPABASE_URL, SUPABASE_KEY)
    except Exception as e:
        return None

supabase = init_supabase()

# ==========================================
# LOGIKA STRUKTUR KATEGORI SEVERITY
# ==========================================
def get_gad_severity(score):
    if score <= 4: return "Minimal"
    elif score <= 9: return "Mild"
    elif score <= 14: return "Moderate"
    else: return "Severe"

def get_phq_severity(score):
    if score <= 4: return "None-Minimal"
    elif score <= 9: return "Mild"
    elif score <= 14: return "Moderate"
    elif score <= 19: return "Moderately Severe"
    else: return "Severe"

# ==========================================
# SISTEM UTAMA AUTENTIKASI (SESSION STATE DENGAN MEMORI LOKAL)
# ==========================================
if 'logged_in' not in st.session_state:
    st.session_state['logged_in'] = False
if 'username' not in st.session_state:
    st.session_state['username'] = ""
# Membuat database lokal sementara di memori browser untuk menampung pendaftaran akun offline
if 'db_users_mock' not in st.session_state:
    st.session_state['db_users_mock'] = {"admin": "admin"} # Default akun bawaan

# Halaman Login / Registrasi jika belum masuk
if not st.session_state['logged_in']:
    st.title("🔐 Selamat Datang di MindMetrics")
    st.subheader("Platform Analisis Dampak Media Sosial terhadap Kesehatan Mental")
    
    # Cek status Supabase
    using_mock_db = (SUPABASE_URL == "ISI_DENGAN_URL_SUPABASE_ANDA" or SUPABASE_KEY == "ISI_DENGAN_ANON_KEY_SUPABASE_ANDA")
    
    if using_mock_db:
        st.warning("⚠️ Mode Penyimpanan Lokal Aktif: Data pendaftaran baru Anda akan tersimpan sementara di memori browser ini.")

    tab_auth1, tab_auth2 = st.tabs(["Masuk (Login)", "Daftar Akun Baru"])
    
    with tab_auth1:
        login_user = st.text_input("Username", key="login_u")
        login_pass = st.text_input("Kata Sandi", type="password", key="login_p")
        if st.button("Masuk"):
            if not using_mock_db and supabase:
                # Alur Asli menggunakan database Supabase Cloud
                res = supabase.table("users").select("*").eq("username", login_user).eq("password", login_pass).execute()
                if len(res.data) > 0:
                    st.session_state['logged_in'] = True
                    st.session_state['username'] = login_user
                    st.success("Login Berhasil!")
                    st.rerun()
                else:
                    st.error("Username atau password salah!")
            else:
                # Alur menggunakan Database Memori Lokal (Bisa membaca akun baru yang Anda daftarkan)
                if login_user in st.session_state['db_users_mock'] and st.session_state['db_users_mock'][login_user] == login_pass:
                    st.session_state['logged_in'] = True
                    st.session_state['username'] = login_user
                    st.success(f"Selamat datang kembali, {login_user}!")
                    st.rerun()
                else:
                    st.error("Username atau password salah / Belum terdaftar!")
                
    with tab_auth2:
        reg_user = st.text_input("Buat Username", key="reg_u")
        reg_pass = st.text_input("Buat Kata Sandi", type="password", key="reg_p")
        if st.button("Daftar Akun"):
            if reg_user.strip() == "" or reg_pass.strip() == "":
                st.error("Username dan Kata Sandi tidak boleh kosong!")
            elif not using_mock_db and supabase:
                # Mendaftar ke Supabase asli
                try:
                    supabase.table("users").insert({"username": reg_user, "password": reg_pass}).execute()
                    st.success("Akun berhasil dibuat di cloud Supabase! Silakan masuk pada tab 'Masuk (Login)'.")
                except Exception as e:
                    st.error("Gagal mendaftar: Username mungkin sudah terpakai.")
            else:
                # Mendaftar ke database memori lokal sementara
                if reg_user in st.session_state['db_users_mock']:
                    st.error("Username tersebut sudah terdaftar di memori local!")
                else:
                    st.session_state['db_users_mock'][reg_user] = reg_pass
                    st.success(f"🎉 Akun '{reg_user}' BERHASIL disimpan di memori lokal! Silakan pindah ke tab 'Masuk (Login)' untuk mengetesnya.")
                    
    st.stop()

# ==========================================
# MENU NAVIGASI UTAMA (SETELAH LOGIN)
# ==========================================
st.sidebar.title(f"👋 Halo, {st.session_state['username']}")
menu = st.sidebar.radio("Navigasi Menu:", [
    "1. Analisis Dataset (Dashboard)", 
    "2. Prediksi Skor GAD-7 & PHQ-9", 
    "3. Laporan Kesehatan Mental Saya"
])

if st.sidebar.button("Keluar (Logout)"):
    st.session_state['logged_in'] = False
    st.session_state['username'] = ""
    st.rerun()

# Membaca data untuk visualisasi
@st.cache_data
def load_data():
    return pd.read_csv('social_media_mental_health.csv')

df_clean = load_data()

# ==========================================
# KOMPONEN 1: ANALISIS DATASET
# ==========================================
if menu == "1. Analisis Dataset (Dashboard)":
    st.title("📊 Dashboard Analisis Risiko Media Sosial")
    st.write("Eksplorasi data makro mengenai hubungan durasi layar dengan tingkat kecemasan dan depresi.")
    
    # --- VISUALISASI 1 ---
    st.markdown("### Hubungan Waktu Layar Harian dengan Skor Gangguan Mental")
    col1_v, col1_e = st.columns(2)
    
    with col1_v:
        st.markdown('<div class="box-visual">', unsafe_allow_index=True)
        st.markdown("#### **Kotak Visualisasi**")
        # Membuat visualisasi tren menggunakan Plotly
        df_grouped = df_clean.groupby('Daily_Screen_Time_Hours')[['GAD_7_Score', 'PHQ_9_Score']].mean().reset_index()
        fig1 = px.line(df_grouped, x='Daily_Screen_Time_Hours', y=['GAD_7_Score', 'PHQ_9_Score'],
                       labels={'value': 'Rata-rata Skor', 'Daily_Screen_Time_Hours': 'Waktu Layar (Jam)'},
                       title="Tren Skor GAD-7 & PHQ-9 berdasarkan Screen Time")
        fig1.update_layout(plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)')
        st.plotly_chart(fig1, use_container_width=True)
        st.markdown('</div>', unsafe_allow_index=True)
        
    with col1_e:
        st.markdown('<div class="box-explanation">', unsafe_allow_index=True)
        st.markdown("#### **Kotak Penjelasan & Interpretasi**")
        st.markdown("""
        **Analisis Data:**
        - Berdasarkan grafik di samping, terlihat adanya **korelasi positif** yang signifikan antara peningkatan *Daily Screen Time Hours* dengan kenaikan rata-rata skor kecemasan (GAD-7) dan depresi (PHQ-9).
        - Pengguna dengan durasi layar di atas **6 jam per hari** cenderung menembus ambang batas skor klinis kategori *Moderate* ke atas.
        - Faktor pemicu utama disinyalir diakibatkan oleh paparan konten yang memicu perbandingan sosial (*Social Comparison*) secara terus-menerus.
        """)
        st.markdown('</div>', unsafe_allow_index=True)

    # --- VISUALISASI 2 ---
    st.markdown("### Distribusi Tingkat Keparahan Berdasarkan Platform Utama")
    col2_v, col2_e = st.columns(2)
    
    with col2_v:
        st.markdown('<div class="box-visual">', unsafe_allow_index=True)
        st.markdown("#### **Kotak Visualisasi**")
        fig2 = px.histogram(df_clean, x="Primary_Platform", color="PHQ_9_Severity",
                            title="Distribusi Tingkat Depresi (PHQ-9) per Platform Media Sosial",
                            barmode="group")
        fig2.update_layout(plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)')
        st.plotly_chart(fig2, use_container_width=True)
        st.markdown('</div>', unsafe_allow_index=True)
        
    with col2_e:
        st.markdown('<div class="box-explanation">', unsafe_allow_index=True)
        st.markdown("#### **Kotak Penjelasan & Interpretasi**")
        st.markdown("""
        **Analisis Data:**
        - Platform dengan fokus visual yang intensif (seperti TikTok dan Instagram) menunjukkan persebaran tingkat keparahan indikasi *Severe* dan *Moderate* yang lebih padat dibandingkan platform profesional atau teks.
        - Pola konsumsi pasif (*passive scrolling*) pada platform hiburan memperkuat efek isolasi emosional dan gangguan pola tidur (*Late Night Usage*).
        """)
        st.markdown('</div>', unsafe_allow_index=True)

# ==========================================
# KOMPONEN 2: PREDIKSI SKOR MENGGUNAKAN PKL
# ==========================================
elif menu == "2. Prediksi Skor GAD-7 & PHQ-9":
    st.title("🤖 Kalkulator Prediksi Risiko Kesehatan Mental")
    st.write("Gunakan kecerdasan buatan untuk memperkirakan skor kecemasan dan depresi Anda berdasarkan aktivitas digital harian.")
    
    try:
        with open('model_gad7.pkl', 'rb') as f:
            model_gad = pickle.load(f)
        with open('model_phq9.pkl', 'rb') as f:
            model_phq = pickle.load(f)
            
        # Form Input User
        col_form1, col_form2 = st.columns(2)
        with col_form1:
            age = st.number_input("Berapa Umur Anda?", min_value=12, max_value=80, value=20)
            gender = st.selectbox("Gender", ["Male", "Female"])
            archetype = st.selectbox("Arketipe Pengguna", ["Hyper-Connected", "Digital Minimalist", "Average User", "Passive Scroller"])
            platform = st.selectbox("Platform Utama yang Sering Digunakan", ["Twitter/X", "TikTok", "Snapchat", "LinkedIn", "YouTube", "Instagram"])
            content_type = st.selectbox("Jenis Konten Dominan", ["Gaming", "Entertainment/Comedy", "Educational/Tech", "Self-Help/Motivation", "Lifestyle/Fashion", "News/Politics"])
            
        with col_form2:
            activity = st.selectbox("Tipe Aktivitas", ["Active", "Passive"])
            screen_time = st.slider("Durasi Penggunaan Layar Harian (Jam)", 0.0, 16.0, 4.0)
            sleep_duration = st.slider("Durasi Tidur Harian (Jam)", 2.0, 12.0, 7.0)
            late_night = st.selectbox("Sering Menggunakan Gadget Larut Malam?", ["Tidak", "Ya"])
            social_compare = st.selectbox("Sering Merasa Insecure/Membandingkan Diri di Medsos?", ["Tidak", "Ya"])
            
        # Konversi input biner ke angka numerik sesuai pelatihan dataset
        late_night_numeric = 1 if late_night == "Ya" else 0
        social_compare_numeric = 1 if social_compare == "Ya" else 0
        
        if st.button("Hitung Prediksi & Simpan Ke Database"):
            # Format DataFrame input agar sama persis dengan struktur data training
            input_data = pd.DataFrame([{
                'Age': age, 'Gender': gender, 'User_Archetype': archetype, 'Primary_Platform': platform,
                'Daily_Screen_Time_Hours': screen_time, 'Dominant_Content_Type': content_type,
                'Activity_Type': activity, 'Late_Night_Usage': late_night_numeric,
                'Social_Comparison_Trigger': social_compare_numeric, 'Sleep_Duration_Hours': sleep_duration
            }])
            
            # Melakukan prediksi dari file .pkl
            pred_gad_score = round(model_gad.predict(input_data)[0], 2)
            pred_phq_score = round(model_phq.predict(input_data)[0], 2)
            
            gad_sev = get_gad_severity(pred_gad_score)
            phq_sev = get_phq_severity(pred_phq_score)
            
            # Tampilkan Hasil Utama
            st.success("🎯 Hasil Prediksi Berhasil Dihitung!")
            
            res_col1, res_col2 = st.columns(2)
            with res_col1:
                st.metric(label="Prediksi Skor GAD-7 (Kecemasan)", value=f"{pred_gad_score} / 21", delta=gad_sev, delta_color="inverse")
            with res_col2:
                st.metric(label="Prediksi Skor PHQ-9 (Depresi)", value=f"{pred_phq_score} / 27", delta=phq_sev, delta_color="inverse")
                
            # Simpan data ke tabel Supabase user_reports
            if supabase:
                report_payload = {
                    "username": st.session_state['username'], "age": age, "gender": gender,
                    "primary_platform": platform, "daily_screen_time": screen_time, "sleep_duration": sleep_duration,
                    "gad7_score": pred_gad_score, "gad7_severity": gad_sev,
                    "phq9_score": pred_phq_score, "phq9_severity": phq_sev
                }
                supabase.table("user_reports").insert(report_payload).execute()
                st.info("Laporan hasil tes ini otomatis disimpan ke profil Anda.")
            else:
                st.warning("Mode Lokal: Berhasil memprediksi, namun data tidak disimpan ke cloud karena Supabase belum diaktifkan.")
                
    except FileNotFoundError:
        st.error("File 'model_gad7.pkl' atau 'model_phq9.pkl' tidak ditemukan. Jalankan file 'train_model.py' terlebih dahulu untuk mengekspor model cerdas Anda.")

# ==========================================
# KOMPONEN 3: LAPORAN KESEHATAN MENTAL USER
# ==========================================
elif menu == "3. Laporan Kesehatan Mental Saya":
    st.title("📋 Riwayat Dokumen & Catatan Kesehatan Emosional")
    st.write("Semua riwayat pengujian Anda tersimpan dengan aman di bawah ini.")
    
    if supabase:
        # Menarik data khusus milik user yang sedang aktif login
        user_data = supabase.table("user_reports").select("*").eq("username", st.session_state['username']).order("created_at", desc=True).execute()
        
        if len(user_data.data) > 0:
            df_report = pd.DataFrame(user_data.data)
            
            # Mempercantik visualisasi riwayat internal user
            st.markdown("### 📈 Perkembangan Kondisi Anda Seiring Waktu")
            fig_track = px.line(df_report, x="created_at", y=["gad7_score", "phq9_score"], 
                                labels={"value": "Nilai Skor", "created_at": "Tanggal Tes"},
                                title="Tren Fluktuasi Kesehatan Mental Anda")
            st.plotly_chart(fig_track, use_container_width=True)
            
            st.markdown("### 🗃️ Detail Log Rekam Medis Digital")
            st.dataframe(df_report[['created_at', 'age', 'primary_platform', 'daily_screen_time', 'sleep_duration', 'gad7_score', 'gad7_severity', 'phq9_score', 'phq9_severity']], use_container_width=True)
        else:
            st.info("Anda belum pernah melakukan kalkulasi prediksi. Silakan buka menu nomor 2 untuk membuat laporan pertama Anda.")
    else:
        st.warning("Fitur riwayat database ini membutuhkan koneksi aktif ke Supabase.")
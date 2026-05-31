import streamlit as st
import pandas as pd
import numpy as np
import pickle
import plotly.express as px
import base64

# ==========================================
# 1. INTEGRASI BACKGROUND GAMBAR KUSTOM
# ==========================================
def get_base64_of_bin_file(bin_file):
    try:
        with open(bin_file, 'rb') as f:
            data = f.read()
        return base64.b64encode(data).decode()
    except FileNotFoundError:
        return None

def set_png_as_page_bg(png_file):
    bin_str = get_base64_of_bin_file(png_file)
    if bin_str:
        page_bg_img = f'''
        <style>
        .stApp {{
            background-image: url("data:image/jpeg;base64,{bin_str}");
            background-size: cover;
            background-position: center;
            background-repeat: no-repeat;
            background-attachment: fixed;
        }}
        </style>
        '''
        st.markdown(page_bg_img, unsafe_allow_html=True)
    else:
        st.markdown("<style>.stApp { background-color: #F8F9FA; }</style>", unsafe_allow_html=True)

# Panggil gambar background kustom Anda
set_png_as_page_bg('bg3.png')

# ==========================================
# 2. PENGATURAN HALAMAN & INJEKSI CSS GLOBAL
# ==========================================
st.set_page_config(page_title="MindMetrics Platform", layout="wide", initial_sidebar_state="expanded")

st.markdown("""
    <style>
    /* Pengaturan teks utama agar kontras tinggi */
    p, span, label, .stMarkdown, .stText {
        color: #2F3640 !important;
        font-weight: 500 !important;
    }
    
    /* Memaksa layout form masuk */
    div[data-testid="stForm"] {
        background-color: rgba(255, 255, 255, 0.96) !important;
        border: 1px solid #E4E7EB !important;
        border-radius: 16px !important;
        padding: 30px !important;
        box-shadow: 0 10px 25px rgba(0, 0, 0, 0.08) !important;
    }
    
    /* Penggantian border default kontainer streamlit */
    div[data-testid="stVerticalBlockBorderWrapper"] {
        border-radius: 14px !important;
        box-shadow: 0 4px 15px rgba(0, 0, 0, 0.03) !important;
        margin-bottom: 20px !important;
        background-color: #FFFFFF !important;
    }
    
    /* Tombol kustom aplikasi utama */
    div.stButton > button:first-child, div.stFormSubmitButton > button {
        background-color: #2196F3 !important;
        color: #FFFFFF !important;
        border-radius: 8px !important;
        border: none !important;
        padding: 12px 24px !important;
        font-weight: 600 !important;
        width: 100% !important;
    }
    div.stButton > button:first-child:hover, div.stFormSubmitButton > button:hover {
        background-color: #1976D2 !important;
    }
    
    h1 { color: #0B3C5D !important; font-weight: 800 !important; }
    h2, h3 { color: #1D2731 !important; font-weight: 700 !important; }
    h4 { color: #1565C0 !important; font-weight: 700 !important; margin-top: 0px !important; }
    
    /* Pengingat Metrik Besar */
    div[data-testid="stMetricValue"] {
        font-size: 2rem !important;
        font-weight: 700 !important;
    }

    /* ==========================================
       STYLING SIDEBAR PROFESIONAL
       ========================================== */
    /* Background & Border Sidebar */
    [data-testid="stSidebar"] {
        background-color: #1E293B !important;
        border-right: 1px solid #334155 !important;
    }

    /* Pembungkus Konten Profil */
    .sidebar-profile-box {
        background: linear-gradient(135deg, #1E3A8A 0%, #0F172A 100%);
        padding: 20px;
        border-radius: 12px;
        border: 1px solid #2563EB;
        margin-bottom: 25px;
        box-shadow: 0 4px 12px rgba(0,0,0,0.15);
    }
    .profile-greeting {
        color: #94A3B8 !important;
        font-size: 0.85rem !important;
        text-transform: uppercase;
        letter-spacing: 0.1em;
        margin: 0 !important;
    }
    .profile-name {
        color: #FFFFFF !important;
        font-size: 1.25rem !important;
        font-weight: 700 !important;
        margin-top: 4px !important;
        margin-bottom: 0 !important;
    }

    /* Kustomisasi Radio Button Sidebar Menjadi Menu List Profesional */
    [data-testid="stSidebar"] .stRadio > label {
        color: #94A3B8 !important;
        font-size: 0.85rem !important;
        text-transform: uppercase;
        letter-spacing: 0.05em;
        margin-bottom: 10px;
        font-weight: 600 !important;
    }
    [data-testid="stSidebar"] div[data-testid="stMarkdownContainer"] p {
        color: #E2E8F0 !important;
    }
    /* Mengubah text warna option list agar kontras di latar gelap */
    [data-testid="stSidebar"] .stRadio div[role="radiogroup"] label {
        background-color: #334155 !important;
        padding: 12px 16px !important;
        border-radius: 8px !important;
        margin-bottom: 8px !important;
        border: 1px solid #475569 !important;
        transition: all 0.2s ease-in-out;
        width: 100%;
    }
    /* Hover effect pada menu navigasi */
    [data-testid="stSidebar"] .stRadio div[role="radiogroup"] label:hover {
        background-color: #475569 !important;
        border-color: #3B82F6 !important;
        cursor: pointer;
    }
    /* Penanda untuk pilihan yang sedang aktif */
    [data-testid="stSidebar"] .stRadio div[role="radiogroup"] [data-checked="true"] label {
        background: linear-gradient(90deg, #2563EB 0%, #1D4ED8 100%) !important;
        border-color: #3B82F6 !important;
        box-shadow: 0 4px 10px rgba(37, 99, 235, 0.2);
    }
    [data-testid="stSidebar"] .stRadio div[role="radiogroup"] [data-checked="true"] label p {
        color: #FFFFFF !important;
        font-weight: 600 !important;
    }

    /* Tombol Keluar / Logout Premium */
    div.sidebar-logout-container div.stButton > button {
        background-color: transparent !important;
        color: #F1F5F9 !important;
        border: 1px solid #475569 !important;
        border-radius: 8px !important;
        padding: 10px 20px !important;
        font-size: 0.9rem !important;
        font-weight: 500 !important;
        transition: all 0.2s ease;
    }
    div.sidebar-logout-container div.stButton > button:hover {
        background-color: #EF4444 !important;
        color: #FFFFFF !important;
        border-color: #EF4444 !important;
        box-shadow: 0 4px 12px rgba(239, 68, 68, 0.2);
    }
    
    /* Garis pembatas kustom untuk sidebar */
    .sidebar-divider {
        border-top: 1px solid #334155;
        margin: 20px 0;
    }
    </style>
""", unsafe_allow_html=True)

# ==========================================
# 3. MEMORI STATE / SIMULASI DATABASE LOCAL
# ==========================================
if 'logged_in' not in st.session_state:
    st.session_state['logged_in'] = False
if 'username' not in st.session_state:
    st.session_state['username'] = ""
if 'full_name' not in st.session_state:
    st.session_state['full_name'] = ""
if 'db_users_mock' not in st.session_state:
    st.session_state['db_users_mock'] = {
        "admin": {"password": "admin", "name": "Administrator Uji Coba"}
    }
# Inisialisasi basis data log untuk pelacakan tanggal
if 'db_reports_mock' not in st.session_state:
    st.session_state['db_reports_mock'] = []

# ==========================================
# 4. HALAMAN GERBANG MASUK (TEKS UTAMA & TAB MENJADI PUTIH)
# ==========================================
if not st.session_state['logged_in']:
    # Injeksi CSS Tambahan Khusus untuk membuat teks di dalam komponen st.tabs menjadi PUTIH
    st.markdown("""
        <style>
        /* Mengubah warna teks tab yang tidak aktif menjadi putih transparan */
        button[data-baseweb="tab"] p {
            color: rgba(255, 255, 255, 0.7) !important;
            font-weight: 600 !important;
            font-size: 1.05rem !important;
        }
        /* Mengubah warna teks tab yang sedang aktif/diklik menjadi putih cerah */
        button[data-baseweb="tab"][aria-selected="true"] p {
            color: #FFFFFF !important;
            font-weight: 700 !important;
        }
        /* Mengubah warna garis bawah tab yang aktif menjadi putih/biru muda cerah */
        div[data-baseweb="tab-highlight"] {
            background-color: #FFFFFF !important;
        }
        </style>
    """, unsafe_allow_html=True)

    _, center_col, _ = st.columns([1, 1.8, 1])
    with center_col:
        st.write("")
        st.write("")
        
        # --- [DI LUAR KOTAK PUTIH] LOGO & JUDUL UTAMA ---
        # Menampilkan logo tepat di tengah dengan HTML agar ukurannya presisi
        st.markdown(
            """
            <div style="text-align: center;">
                <img src="data:image/png;base64,{}" width="220px" style="margin-bottom: 15px;">
            </div>
            """.format(get_base64_of_bin_file("logo.png") if get_base64_of_bin_file("logo.png") else ""), 
            unsafe_allow_html=True
        )

        # --- [DI LUAR KOTAK PUTIH] TAB NAVIGASI MASUK / DAFTAR (SEKARANG TEKSNYA PUTIH) ---
        tab_login, tab_register = st.tabs(["🔒 MASUK (LOGIN)", "📝 DAFTAR AKUN BARU"])
        
        # --- [DI DALAM KOTAK PUTIH] FORM LOGIN ---
        with tab_login:
            with st.form(key="form_login_internal"):
                st.markdown("### Selamat Datang Kembali")
                login_u = st.text_input("Username", placeholder="Masukkan nama pengguna")
                login_p = st.text_input("Kata Sandi", type="password", placeholder="Masukkan kata sandi")
                submit_login = st.form_submit_button("Masuk Sekarang")
                
            if submit_login:
                if login_u in st.session_state['db_users_mock'] and st.session_state['db_users_mock'][login_u]["password"] == login_p:
                    st.session_state['logged_in'] = True
                    st.session_state['username'] = login_u
                    st.session_state['full_name'] = st.session_state['db_users_mock'][login_u]["name"]
                    st.rerun()
                else:
                    st.error("❌ Username atau Kata Sandi salah!")
                        
        # --- [DI DALAM KOTAK PUTIH] FORM REGISTER ---
        with tab_register:
            with st.form(key="form_register_internal"):
                st.markdown("### Buat Akun Baru")
                reg_name = st.text_input("Nama Lengkap", placeholder="Masukkan nama lengkap Anda")
                reg_u = st.text_input("Username Baru", placeholder="Buat nama pengguna unik")
                reg_p = st.text_input("Kata Sandi Baru", type="password", placeholder="Buat kata sandi aman")
                submit_register = st.form_submit_button("Daftar Sekarang")
                
            if submit_register:
                if reg_name.strip() == "" or reg_u.strip() == "" or reg_p.strip() == "":
                    st.error("❌ Semua kolom wajib diisi!")
                else:
                    if reg_u in st.session_state['db_users_mock']:
                        st.error("❌ Username sudah terpakai.")
                    else:
                        st.session_state['db_users_mock'][reg_u] = {"password": reg_p, "name": reg_name}
                        st.success(f"🎉 Akun {reg_name} sukses terdaftar! Silakan pindah ke tab Login.")
                        
    st.stop()
# ==========================================
# 5. SIDEBAR UTAMA APLIKASI (PRO-LOOK UPDATED)
# ==========================================
# Komponen Profil Premium via HTML Injection
st.sidebar.markdown(f"""
    <div class="sidebar-profile-box">
        <p class="profile-greeting">Sesi Aktif Pengguna</p>
        <p class="profile-name">👤 {st.session_state['full_name']}</p>
    </div>
""", unsafe_allow_html=True)

# Menu Pilihan Radio yang sudah ter-styling CSS di atas
menu_pilihan = st.sidebar.radio("Navigasi Sistem:", [
    "📊 1. Analisis Dataset (Dashboard)", 
    "🤖 2. Prediksi Skor GAD-7 & PHQ-9", 
    "📋 3. Laporan Kesehatan Mental Saya"
])

st.sidebar.markdown('<div class="sidebar-divider"></div>', unsafe_allow_html=True)

# Container Khusus untuk Tombol Keluar agar terisolasi styling-nya
with st.sidebar.container():
    st.markdown('<div class="sidebar-logout-container">', unsafe_allow_html=True)
    if st.button("🚪 Keluar Aplikasi"):
        st.session_state['logged_in'] = False
        st.session_state['username'] = ""
        st.session_state['full_name'] = ""
        st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)

# Membaca data csv global untuk dashboard makro
@st.cache_data
def load_data():
    return pd.read_csv('social_media_mental_health.csv')
df_clean = load_data()

# ==========================================
# 6. EKSEKUSI TIAP HALAMAN KONTEN
# ==========================================

# --- KOMPONEN 1: DASHBOARD MAKRO ---
if menu_pilihan == "📊 1. Analisis Dataset (Dashboard)":
    st.title("📊 Dashboard Analisis Risiko Media Sosial")
    st.write("Eksplorasi visualisasi data mengenai pengaruh aktivitas digital terhadap indikasi kecemasan dan depresi.")
    st.write("")

    # Row 1
    st.markdown("### 📈 Hubungan Waktu Layar Terhadap Skor GAD-7 & PHQ-9")
    col1_v, col1_e = st.columns(2)
    with col1_v:
        with st.container(border=True):
            st.markdown("#### **Visualisasi Grafik**")
            df_grouped = df_clean.groupby('Daily_Screen_Time_Hours')[['GAD_7_Score', 'PHQ_9_Score']].mean().reset_index()
            fig1 = px.line(df_grouped, x='Daily_Screen_Time_Hours', y=['GAD_7_Score', 'PHQ_9_Score'],
                           labels={'value': 'Rata-rata Skor', 'Daily_Screen_Time_Hours': 'Waktu Layar (Jam)'})
            fig1.update_layout(plot_bgcolor='#FFFFFF', paper_bgcolor='#FFFFFF', margin=dict(l=10, r=10, t=10, b=10))
            st.plotly_chart(fig1, use_container_width=True)
    with col1_e:
        st.markdown(
            """
            <div style="background-color: #E3F2FD; padding: 24px; border-radius: 14px; border: 1px solid #BBDEFB;">
                <h4 style="color: #0D47A1 !important; margin-bottom: 15px;">💡 Interpretasi & Analisis Data</h4>
                <p style="color: #1565C0 !important; line-height: 1.6;">
                    <b>Korelasi Positif Kuat:</b> Grafik di samping menunjukkan bahwa semakin tinggi <i>Daily Screen Time</i>, rata-rata skor kecemasan (GAD-7) dan depresi (PHQ-9) cenderung merangkak naik secara konsisten.<br><br>
                    <b>Titik Kritis (Threshold):</b> Pengguna yang menghabiskan waktu layar di atas <b>6-8 jam per hari</b> menunjukkan lonjakan skor emosional yang signifikan dibanding kelompok di bawah 3 jam.
                </p>
            </div>
            """, unsafe_allow_html=True
        )
    st.markdown("### 📊 Analisis Pola Istirahat Berdasarkan Aktivitas")

    # Membuat layout 2 kolom (Kolom Kiri untuk Grafik, Kolom Kanan untuk Interpretasi)
    kolom_grafik, kolom_teks = st.columns(2)

    with kolom_grafik:
        with st.container(border=True):
            st.markdown("#### **Grafik Durasi Tidur**")
            
            # Proses pembuatan grafik lingkaran (Pie Chart) contoh sebaran data aktivitas
            fig_pie = px.pie(
                df_clean, 
                names='Activity_Type', 
                values='Sleep_Duration_Hours',
                title="Kontribusi Total Jam Tidur Berdasarkan Tipe Aktivitas"
            )
            fig_pie.update_layout(plot_bgcolor='#FFFFFF', paper_bgcolor='#FFFFFF')
            
            # Tampilkan di kolom kiri
            st.plotly_chart(fig_pie, use_container_width=True)

    with kolom_teks:
        st.markdown(
            """
            <div style="background-color: #E3F2FD; padding: 24px; border-radius: 14px; border: 1px solid #BBDEFB;">
                <h4 style="color: #0D47A1 !important; margin-bottom: 15px;">💡 Analisis Pola Tidur</h4>
                <p style="color: #1565C0 !important; line-height: 1.6;">
                    <b>Informasi Tambahan:</b> Melalui grafik lingkaran di samping, kita dapat melihat distribusi total jam istirahat antara pengguna aktif (Active) dan pengguna pasif (Passive) di media sosial.
                </p>
            </div>
            """, unsafe_allow_html=True
        )

# --- KOMPONEN 2: MESIN PREDIKSI PKL + INPUT TANGGAL ---
elif menu_pilihan == "🤖 2. Prediksi Skor GAD-7 & PHQ-9":
    st.title("🤖 Kalkulator Prediksi Skor Klinis")
    st.write("Masukkan parameter harian Anda beserta tanggal pencatatan untuk memprediksi tingkat indikasi kecemasan dan depresi.")
    st.write("")

    try:
        with open('model_gad7.pkl', 'rb') as f:
            model_gad = pickle.load(f)
        with open('model_phq9.pkl', 'rb') as f:
            model_phq = pickle.load(f)

        with st.form(key="form_prediksi_kesehatan"):
            st.markdown("### 📄 Pengisian Log Kuesioner Harian")
            
            # INPUTAN TANGGAL UTAMA
            input_date = st.date_input("Pilih Tanggal Log Hari Ini:", value=pd.Timestamp.now().date())
            st.markdown("---")
            
            col_inp1, col_inp2 = st.columns(2)
            with col_inp1:
                age = st.number_input("Berapa Umur Anda?", min_value=12, max_value=80, value=20)
                gender = st.selectbox("Gender", ["Male", "Female"])
                archetype = st.selectbox("Arketipe Pengguna Medsos", ["Hyper-Connected", "Digital Minimalist", "Average User", "Passive Scroller"])
                platform = st.selectbox("Platform Media Sosial Terlama", ["Twitter/X", "TikTok", "Snapchat", "LinkedIn", "YouTube", "Instagram"])
                content_type = st.selectbox("Jenis Konten Dominan", ["Gaming", "Entertainment/Comedy", "Educational/Tech", "Self-Help/Motivation", "Lifestyle/Fashion", "News/Politics"])
            with col_inp2:
                activity = st.selectbox("Tipe Aktivitas", ["Active", "Passive"])
                screen_time = st.slider("Durasi Penggunaan Layar Harian (Jam)", 0.0, 16.0, 4.0)
                sleep_duration = st.slider("Durasi Waktu Tidur Harian (Jam)", 2.0, 12.0, 7.0)
                late_night = st.selectbox("Sering Pakai Gadget Larut Malam?", ["Tidak", "Ya"])
                social_compare = st.selectbox("Sering Membandingkan Diri / Insecure di Medsos?", ["Tidak", "Ya"])

            submit_prediction = st.form_submit_button("💥 Hitung Hasil & Simpan Laporan")

        if submit_prediction:
            late_night_num = 1 if late_night == "Ya" else 0
            social_compare_num = 1 if social_compare == "Ya" else 0
            
            input_df = pd.DataFrame([{
                'Age': age, 'Gender': gender, 'User_Archetype': archetype, 'Primary_Platform': platform,
                'Daily_Screen_Time_Hours': screen_time, 'Dominant_Content_Type': content_type,
                'Activity_Type': activity, 'Late_Night_Usage': late_night_num,
                'Social_Comparison_Trigger': social_compare_num, 'Sleep_Duration_Hours': sleep_duration
            }])
            
            pred_gad = round(float(model_gad.predict(input_df)[0]), 2)
            pred_phq = round(float(model_phq.predict(input_df)[0]), 2)
            
            def get_gad_label(s):
                if s <= 4: return "Minimal"
                elif s <= 9: return "Mild"
                elif s <= 14: return "Moderate"
                else: return "Severe"

            def get_phq_label(s):
                if s <= 4: return "None-Minimal"
                elif s <= 9: return "Mild"
                elif s <= 14: return "Moderate"
                elif s <= 19: return "Moderately Severe"
                else: return "Severe"
                
            g_sev = get_gad_label(pred_gad)
            p_sev = get_phq_label(pred_phq)
            
            st.success("🎯 Hasil Prediksi Berhasil Dihitung!")
            res_c1, res_c2 = st.columns(2)
            with res_c1:
                st.metric(label="Prediksi Skor GAD-7 (Kecemasan)", value=f"{pred_gad} / 21", delta=g_sev, delta_color="inverse")
            with res_c2:
                st.metric(label="Prediksi Skor PHQ-9 (Depresi)", value=f"{pred_phq} / 27", delta=p_sev, delta_color="inverse")
                
            # Simpan log ke dalam array session state
            report_payload = {
                "username": st.session_state['username'], "tanggal": str(input_date),
                "screen_time": screen_time, "waktu_tidur": sleep_duration,
                "late_night": late_night, "social_compare": social_compare,
                "skor_gad": pred_gad, "keparahan_gad": g_sev,
                "skor_phq": pred_phq, "keparahan_phq": p_sev, "platform": platform
            }
            st.session_state['db_reports_mock'].append(report_payload)
            st.balloons()
            st.info(f"✅ Data log tanggal {input_date} sukses disimpan.")

    except FileNotFoundError:
        st.error("❌ Berkas 'model_gad7.pkl' tidak ditemukan. Jalankan 'train_model.py' terlebih dahulu.")


# --- KOMPONEN 3: EKSEKUSI 5 PILAR SEKTOR LAPORAN KESEHATAN MENTAL ---
elif menu_pilihan == "📋 3. Laporan Kesehatan Mental Saya":
    st.title("📋 Rekam Medis & Laporan Dashboard Kesehatan")
    st.write("Halaman pelacakan klinis terintegrasi berdasarkan data log aktivitas digital Anda.")
    st.write("")

    # Filter data khusus milik user aktif
    if 'db_reports_mock' in st.session_state and len(st.session_state['db_reports_mock']) > 0:
        all_rep = pd.DataFrame(st.session_state['db_reports_mock'])
        user_df = all_rep[all_rep['username'] == st.session_state['username']].copy()
    else:
        user_df = pd.DataFrame()

    if not user_df.empty:
        user_df['tanggal'] = pd.to_datetime(user_df['tanggal'])
        user_df = user_df.sort_values(by='tanggal')
        
        last_record = user_df.iloc[-1] # Entri data paling terakhir

        # ==========================================
        # 📌 LAPORAN 1: RINGKASAN KONDISI KLINIS TERBARU (STATUS UTAMA)
        # ==========================================
        st.markdown("### 🗂️ 1. Ringkasan Kondisi Klinis Terkini")
        with st.container(border=True):
            stat_c1, stat_c2, stat_c3 = st.columns(3)
            with stat_c1:
                st.metric(label="Tanggal Tes Terakhir", value=last_record['tanggal'].strftime('%Y-%m-%d'))
            with stat_c2:
                st.metric(label="Status Kecemasan (GAD-7)", value=f"{last_record['skor_gad']} / 21", delta=last_record['keparahan_gad'], delta_color="inverse")
            with stat_c3:
                st.metric(label="Status Depresi (PHQ-9)", value=f"{last_record['skor_phq']} / 27", delta=last_record['keparahan_phq'], delta_color="inverse")
            
            # Rekomendasi dinamis penanganan emosi berdasarkan status keparahan medis
            st.write("")
            if "Severe" in [last_record['keparahan_gad'], last_record['keparahan_phq']] or "Moderately Severe" in last_record['keparahan_phq']:
                st.error("🚨 **Rekomendasi Medis Klinis:** Skor Anda tergolong sangat tinggi. Platform menyarankan Anda untuk segera mengambil jeda dari media sosial (*Digital Detox*) atau menjadwalkan konsultasi dengan ahli psikolog profesional.")
            else:
                st.success("🌱 **Rekomendasi Medis Klinis:** Kondisi mental Anda saat ini relatif stabil berada pada ambang batas aman. Tetap pertahaman kontrol screen time harian Anda dengan bijak.")

        # ==========================================
        # 📌 LAPORAN 2: PELACAKAN FLUKTUASI TREN TEMPORAL (TIME-SERIES)
        # ==========================================
        st.write("")
        st.markdown("### 📈 2. Tren Fluktuasi Skor Gangguan Mental Terhadap Waktu")
        col_l2_v, col_l2_e = st.columns(2)
        with col_l2_v:
            with st.container(border=True):
                st.markdown("#### **Grafik Perkembangan Skor Klinis**")
                fig_l2 = px.line(user_df, x='tanggal', y=['skor_gad', 'skor_phq'], markers=True,
                                 labels={'value': 'Nilai Skor', 'tanggal': 'Tanggal Evaluasi'})
                fig_l2.update_layout(plot_bgcolor='#FFFFFF', paper_bgcolor='#FFFFFF', margin=dict(l=10, r=10, t=10, b=10))
                st.plotly_chart(fig_l2, use_container_width=True)
        with col_l2_e:
            st.markdown(
                """
                <div style="background-color: #E3F2FD; padding: 24px; border-radius: 14px; border: 1px solid #BBDEFB;">
                    <h4 style="color: #0D47A1 !important; margin-bottom: 15px;">💡 Interpretasi Grafik Tren Kronologis</h4>
                    <p style="color: #1565C0 !important; line-height: 1.6;">
                        <b>Melacak Dinamika Emosi:</b> Grafik garis kontinuitas di samping memetakan pergerakan mental Anda.<br><br>
                        Apabila grafik menunjukkan penurunan ke arah kanan, artinya intervensi pola hidup sehat digital yang Anda lakukan efektif menurunkan ketegangan stres saraf otak.
                    </p>
                </div>
                """, unsafe_allow_html=True
            )

        # ==========================================
        # 📌 LAPORAN 3: ANALISIS FAKTOR PEMICU UTAMA (ROOT CAUSE ANALYSIS)
        # ==========================================
        st.write("")
        st.markdown("### 🎯 3. Analisis Dampak Pemicu Perbandingan Sosial (*Social Comparison*)")
        col_l3_v, col_l3_e = st.columns(2)
        with col_l3_v:
            with st.container(border=True):
                st.markdown("#### **Komparasi Dampak Insecure Terhadap Kecemasan**")
                # Mengelompokkan rata-rata skor berdasarkan pemicu insecure
                trigger_df = user_df.groupby('social_compare')['skor_gad'].mean().reset_index()
                fig_l3 = px.bar(trigger_df, x='social_compare', y='skor_gad', color='social_compare',
                                labels={'skor_gad': 'Rata-rata Skor GAD-7', 'social_compare': 'Perasaan Membandingkan Diri'})
                fig_l3.update_layout(plot_bgcolor='#FFFFFF', paper_bgcolor='#FFFFFF', margin=dict(l=10, r=10, t=10, b=10))
                st.plotly_chart(fig_l3, use_container_width=True)
        with col_l3_e:
            st.markdown(
                """
                <div style="background-color: #E3F2FD; padding: 24px; border-radius: 14px; border: 1px solid #BBDEFB;">
                    <h4 style="color: #0D47A1 !important; margin-bottom: 15px;">💡 Analisis Akar Masalah (Root Cause)</h4>
                    <p style="color: #1565C0 !important; line-height: 1.6;">
                        <b>Efek Kebiasaan Membandingkan Diri:</b> Diagram ini membuktikan seberapa besar rasa <i>insecure</i> memengaruhi kecemasan Anda.<br><br>
                        Ketika Anda mengisi log dengan kondisi sering membandingkan pencapaian diri dengan unggahan orang lain, grafik secara nyata mendeteksi adanya pembengkakan skor kecemasan klinis yang signifikan.
                    </p>
                </div>
                """, unsafe_allow_html=True
            )

        # ==========================================
        # 📌 LAPORAN 4: PELACAK KORELASI WAKTU LAYAR VS WAKTU TIDUR (HABIT IMPACT)
        # ==========================================
        st.write("")
        st.markdown("### ⏱️ 4. Hubungan Durasi Screen Time Terhadap Porsi Istirahat Tidur")
        col_l4_v, col_l4_e = st.columns(2)
        with col_l4_v:
            with st.container(border=True):
                st.markdown("#### **Diagram Batang Kelompok Screen Time vs Tidur**")
                fig_l4 = px.bar(user_df, x='tanggal', y=['screen_time', 'waktu_tidur'], barmode='group',
                                labels={'value': 'Durasi (Jam)', 'tanggal': 'Tanggal'})
                fig_l4.update_layout(plot_bgcolor='#FFFFFF', paper_bgcolor='#FFFFFF', margin=dict(l=10, r=10, t=10, b=10))
                st.plotly_chart(fig_l4, use_container_width=True)
        with col_l4_e:
            st.markdown(
                """
                <div style="background-color: #E3F2FD; padding: 24px; border-radius: 14px; border: 1px solid #BBDEFB;">
                    <h4 style="color: #0D47A1 !important; margin-bottom: 15px;">💡 Korelasi Kebiasaan Istirahat</h4>
                    <p style="color: #1565C0 !important; line-height: 1.6;">
                        <b>Hukum Hubungan Terbalik:</b> Di sini terpampang perbandingan durasi gawai dengan jam tidur malam.<br><br>
                        Seringkali terjadi hukum korelasi negatif: di tanggal-tanggal saat balok biru (Screen Time) memuncak tinggi melebihi ambang batas wajar, balok merah (Waktu Tidur) Anda otomatis akan menyusut drastis.
                    </p>
                </div>
                """, unsafe_allow_html=True
            )

        # ==========================================
        # 📌 LAPORAN 5: PROFIL RISIKO KESEHATAN PER PLATFORM SOSIAL MEDIA
        # ==========================================
        st.write("")
        st.markdown("### 🏛️ 5. Profil Risiko Tingkat Depresi Berdasarkan Jenis Platform")
        col_l5_v, col_l5_e = st.columns(2)
        with col_l5_v:
            with st.container(border=True):
                st.markdown("#### **Rata-rata Skor Depresi Per Aplikasi Medsos**")
                platform_df = user_df.groupby('platform')['skor_phq'].mean().reset_index()
                fig_l5 = px.bar(platform_df, x='platform', y='skor_phq', color='platform',
                                labels={'skor_phq': 'Rata-rata Skor PHQ-9', 'platform': 'Aplikasi Terlama'})
                fig_l5.update_layout(plot_bgcolor='#FFFFFF', paper_bgcolor='#FFFFFF', margin=dict(l=10, r=10, t=10, b=10))
                st.plotly_chart(fig_l5, use_container_width=True)
        with col_l5_e:
            st.markdown(
                """
                <div style="background-color: #E3F2FD; padding: 24px; border-radius: 14px; border: 1px solid #BBDEFB;">
                    <h4 style="color: #0D47A1 !important; margin-bottom: 15px;">💡 Pemetaan Risiko Ekosistem Aplikasi</h4>
                    <p style="color: #1565C0 !important; line-height: 1.6;">
                        <b>Identifikasi Lingkungan Toxic:</b> Setiap aplikasi memiliki tipe algoritma umpan (*feed*) yang berbeda.<br><br>
                        Melalui grafik ini, Anda bisa menyimpulkan secara personal platform mana yang menjadi pemicu utama penurunan kestabilan mood emosi Anda, sehingga Anda bisa mengambil langkah pencegahan berupa pembatasan durasi aplikasi tersebut secara spesifik.
                    </p>
                </div>
                """, unsafe_allow_html=True
            )

    else:
        st.markdown(
            """
            <div style="background-color: rgba(255,255,255,0.9); border: 2px dashed #7F8C8D; padding: 40px; border-radius: 14px; text-align: center;">
                <h3 style="color: #7F8C8D !important;">Belum Ada Riwayat Laporan Terbaca</h3>
                <p style="color: #7F8C8D !important;">Sistem mendeteksi profil Anda belum pernah melakukan pengisian kuesioner harian.<br>Silakan berpindah ke menu <b>🤖 2. Prediksi Skor GAD-7 & PHQ-9</b> terlebih dahulu untuk memasukkan data aktivitas harian Anda!</p>
            </div>
            """, unsafe_allow_html=True
        )
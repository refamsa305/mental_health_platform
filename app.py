import streamlit as st
import pandas as pd
import numpy as np
import pickle
import plotly.express as px
import base64
from supabase import create_client, Client

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

# Memanggil gambar background Anda
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
    .sidebar-profile-box p {
        margin: 0 !important;
    }
    .profile-greeting {
        color: #94A3B8 !important;
        font-size: 0.85rem !important;
        text-transform: uppercase;
        letter-spacing: 0.1em;
    }
    .profile-name {
        color: #FFFFFF !important;
        font-size: 1.25rem !important;
        font-weight: 700 !important;
        margin-top: 4px !important;
    }

    /* Kustomisasi Menu Navigasi List Sidebar */
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
    [data-testid="stSidebar"] .stRadio div[role="radiogroup"] label {
        background-color: #334155 !important;
        padding: 12px 16px !important;
        border-radius: 8px !important;
        margin-bottom: 8px !important;
        border: 1px solid #475569 !important;
        width: 100%;
    }
    [data-testid="stSidebar"] .stRadio div[role="radiogroup"] label:hover {
        background-color: #475569 !important;
        border-color: #3B82F6 !important;
        cursor: pointer;
    }
    [data-testid="stSidebar"] .stRadio div[role="radiogroup"] [data-checked="true"] label {
        background: linear-gradient(90deg, #2563EB 0%, #1D4ED8 100%) !important;
        border-color: #3B82F6 !important;
        box-shadow: 0 4px 10px rgba(37, 99, 235, 0.2);
    }
    [data-testid="stSidebar"] .stRadio div[role="radiogroup"] [data-checked="true"] label p {
        color: #FFFFFF !important;
        font-weight: 600 !important;
    }

    /* Tombol Keluar Premium */
    div.sidebar-logout-container div.stButton > button {
        background-color: transparent !important;
        color: #F1F5F9 !important;
        border: 1px solid #475569 !important;
        border-radius: 8px !important;
        padding: 10px 20px !important;
    }
    div.sidebar-logout-container div.stButton > button:hover {
        background-color: #EF4444 !important;
        color: #FFFFFF !important;
        border-color: #EF4444 !important;
    }
    .sidebar-divider {
        border-top: 1px solid #334155;
        margin: 20px 0;
    }
    </style>
""", unsafe_allow_html=True)

# ==========================================
# 3. KONEKSI REAL-TIME SUPABASE CLOUD
# ==========================================
SUPABASE_URL = "https://cqmlvarkzhejzxbnwtfe.supabase.co/rest/v1/"
SUPABASE_KEY = "sb_publishable_YBD-kczdlV9QE_S6JbsngQ_w5Y0D8hc"

@st.cache_resource
def init_supabase():
    return create_client(SUPABASE_URL, SUPABASE_KEY)

supabase = init_supabase()

if 'logged_in' not in st.session_state: st.session_state['logged_in'] = False
if 'username' not in st.session_state: st.session_state['username'] = ""
if 'full_name' not in st.session_state: st.session_state['full_name'] = ""

# ==========================================
# 4. HALAMAN GERBANG MASUK (LOGIN & REGISTER)
# ==========================================
if not st.session_state['logged_in']:
    st.markdown("""
        <style>
        button[data-baseweb="tab"] p { color: rgba(255, 255, 255, 0.7) !important; font-weight: 600 !important; }
        button[data-baseweb="tab"][aria-selected="true"] p { color: #FFFFFF !important; font-weight: 700 !important; }
        div[data-baseweb="tab-highlight"] { background-color: #FFFFFF !important; }
        </style>
    """, unsafe_allow_html=True)

    _, center_col, _ = st.columns([1, 1.8, 1])
    with center_col:
        st.write("")
        st.write("")
        st.markdown("<h1 style='text-align: center; color: #FFFFFF !important;'>🧠 MindMetrics</h1>", unsafe_allow_html=True)
        st.markdown("<p style='text-align: center; font-size: 1.1rem; color: #E2E8F0 !important; font-weight: 600;'>Platform Analisis Dampak Media Sosial terhadap Kesehatan Mental</p>", unsafe_allow_html=True)
        
        tab_login, tab_register = st.tabs(["🔒 MASUK (LOGIN)", "📝 DAFTAR AKUN BARU"])
        
        with tab_login:
            with st.form(key="form_login"):
                st.markdown("### Selamat Datang Kembali")
                login_u = st.text_input("Username", placeholder="Masukkan nama pengguna")
                login_p = st.text_input("Kata Sandi", type="password", placeholder="Masukkan kata sandi")
                submit_login = st.form_submit_button("Masuk Sekarang")
            if submit_login:
                res = supabase.from_("users").select("*").eq("username", login_u).eq("password", login_p).execute()
                if len(res.data) > 0:
                    st.session_state['logged_in'] = True
                    st.session_state['username'] = login_u
                    st.session_state['full_name'] = res.data[0]["full_name"]
                    st.rerun()
                else:
                    st.error("❌ Username atau Kata Sandi salah!")
                        
        with tab_register:
            with st.form(key="form_register"):
                st.markdown("### Buat Akun Baru")
                reg_name = st.text_input("Nama Lengkap", placeholder="Masukkan nama lengkap Anda")
                reg_u = st.text_input("Username Baru", placeholder="Buat nama pengguna unik")
                reg_p = st.text_input("Kata Sandi Baru", type="password", placeholder="Buat kata sandi aman")
                submit_register = st.form_submit_button("Daftar Sekarang")
            if submit_register:
                if reg_name.strip() == "" or reg_u.strip() == "" or reg_p.strip() == "":
                    st.error("❌ Semua kolom wajib diisi!")
                else:
                    check_user = supabase.from_("users").select("*").eq("username", reg_u).execute()
                    if len(check_user.data) > 0:
                        st.error("❌ Username sudah terpakai.")
                    else:
                        supabase.from_("users").insert({"username": reg_u, "password": reg_p, "full_name": reg_name}).execute()
                        st.success(f"🎉 Akun {reg_name} sukses terdaftar! Silakan pindah ke tab Login.")
    st.stop()

# ==========================================
# 5. SIDEBAR UTAMA APLIKASI
# ==========================================
st.sidebar.markdown(f"""
    <div class="sidebar-profile-box">
        <p class="profile-greeting">Sesi Aktif Pengguna</p>
        <p class="profile-name">👤 {st.session_state['full_name']}</p>
    </div>
""", unsafe_allow_html=True)

menu_pilihan = st.sidebar.radio("Navigasi Sistem:", [
    "📊 1. Analisis Dataset (Dashboard)", 
    "🤖 2. Prediksi Skor GAD-7 & PHQ-9", 
    "📋 3. Laporan Kesehatan Mental Saya"
])

st.sidebar.markdown('<div class="sidebar-divider"></div>', unsafe_allow_html=True)
with st.sidebar.container():
    st.markdown('<div class="sidebar-logout-container">', unsafe_allow_html=True)
    if st.sidebar.button("🚪 Keluar Aplikasi"):
        st.session_state['logged_in'] = False
        st.session_state['username'] = ""
        st.session_state['full_name'] = ""
        st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)

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

    st.write("")
    st.markdown("### 📊 Analisis Pola Istirahat Berdasarkan Aktivitas")
    kolom_grafik, kolom_teks = st.columns(2)
    with kolom_grafik:
        with st.container(border=True):
            st.markdown("#### **Grafik Durasi Tidur**")
            fig_pie = px.pie(df_clean, names='Activity_Type', values='Sleep_Duration_Hours', title="Kontribusi Total Jam Tidur Berdasarkan Tipe Aktivitas")
            fig_pie.update_layout(plot_bgcolor='#FFFFFF', paper_bgcolor='#FFFFFF')
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

# --- KOMPONEN 2: MESIN PREDIKSI DENGAN FILE .PKL ---
elif menu_pilihan == "🤖 2. Prediksi Skor GAD-7 & PHQ-9":
    st.title("🤖 Kalkulator Prediksi Skor Klinis")
    st.write("Masukkan parameter harian Anda beserta tanggal pencatatan untuk memprediksi tingkat indikasi kecemasan dan depresi.")
    st.write("")

    try:
        # PANGGILAN MODEL DARI FILE .PKL PILIHAN ANDA
        with open('model_gad7.pkl', 'rb') as f: model_gad = pickle.load(f)
        with open('model_phq9.pkl', 'rb') as f: model_phq = pickle.load(f)

        with st.form(key="form_prediksi_kesehatan"):
            st.markdown("### 📄 Pengisian Log Kuesioner Harian")
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
            
            g_sev = "Minimal" if pred_gad <= 4 else "Mild" if pred_gad <= 9 else "Moderate" if pred_gad <= 14 else "Severe"
            p_sev = "None-Minimal" if pred_phq <= 4 else "Mild" if pred_phq <= 9 else "Moderate" if pred_phq <= 14 else "Moderately Severe" if pred_phq <= 19 else "Severe"
            
            st.success("🎯 Hasil Prediksi Berhasil Dihitung!")
            res_c1, res_c2 = st.columns(2)
            with res_c1: st.metric(label="Prediksi Skor GAD-7 (Kecemasan)", value=f"{pred_gad} / 21", delta=g_sev, delta_color="inverse")
            with res_c2: st.metric(label="Prediksi Skor PHQ-9 (Depresi)", value=f"{pred_phq} / 27", delta=p_sev, delta_color="inverse")
                
            report_payload = {
                "username": st.session_state['username'], "tanggal": str(input_date),
                "screen_time": screen_time, "waktu_tidur": sleep_duration,
                "late_night": late_night, "social_compare": social_compare,
                "skor_gad": pred_gad, "keparahan_gad": g_sev,
                "skor_phq": pred_phq, "keparahan_phq": p_sev, "platform": platform
            }
            # Menggunakan .from_() agar sinkron dengan Supabase terbaru
            supabase.from_("user_reports").insert(report_payload).execute()
            st.balloons()
            st.info(f"✅ Data log tanggal {input_date} sukses disimpan permanen ke Cloud Supabase.")

    except FileNotFoundError:
        st.error("❌ Berkas 'model_gad7.pkl' atau 'model_phq9.pkl' tidak ditemukan di repositori GitHub Anda.")

# --- KOMPONEN 3: LAKUKAN 5 PILAR SEKTOR LAPORAN ---
elif menu_pilihan == "📋 3. Laporan Kesehatan Mental Saya":
    st.title("📋 Rekam Medis & Laporan Dashboard Kesehatan")
    st.write("Halaman pelacakan klinis terintegrasi berdasarkan data log aktivitas digital Anda.")
    st.write("")

    res_reports = supabase.from_("user_reports").select("*").eq("username", st.session_state['username']).execute()
    
    if len(res_reports.data) > 0:
        user_df = pd.DataFrame(res_reports.data)
        user_df['tanggal'] = pd.to_datetime(user_df['tanggal'])
        user_df = user_df.sort_values(by='tanggal')
        
        last_record = user_df.iloc[-1]

        # 📌 PILAR 1
        st.markdown("### 🗂️ 1. Ringkasan Status Kesehatan Mental Terakhir")
        with st.container(border=True):
            stat_c1, stat_c2, stat_c3 = st.columns(3)
            with stat_c1: st.metric(label="Tanggal Pengujian Terakhir", value=last_record['tanggal'].strftime('%Y-%m-%d'))
            with stat_c2: st.metric(label="Tingkat Kecemasan (GAD-7)", value=f"{last_record['skor_gad']} / 21", delta=last_record['keparahan_gad'], delta_color="inverse")
            with stat_c3: st.metric(label="Tingkat Depresi (PHQ-9)", value=f"{last_record['skor_phq']} / 27", delta=last_record['keparahan_phq'], delta_color="inverse")

        # 📌 PILAR 2
        st.write("")
        st.markdown("### 📈 2. Pelacakan Tren Fluktuasi Skor Mental dari Hari ke Hari")
        col_l2_v, col_l2_e = st.columns(2)
        with col_l2_v:
            with st.container(border=True):
                fig_l2 = px.line(user_df, x='tanggal', y=['skor_gad', 'skor_phq'], markers=True, labels={'value': 'Nilai Skor', 'tanggal': 'Tanggal Evaluasi'})
                fig_l2.update_layout(plot_bgcolor='#FFFFFF', paper_bgcolor='#FFFFFF', margin=dict(l=10, r=10, t=10, b=10))
                st.plotly_chart(fig_l2, use_container_width=True)
        with col_l2_e:
            st.markdown('<div style="background-color: #E3F2FD; padding: 24px; border-radius: 14px; border: 1px solid #BBDEFB;"><h4 style="color: #0D47A1 !important; margin-bottom: 15px;">💡 Interpretasi Grafik Kronologis</h4><p style="color: #1565C0 !important; line-height: 1.6;">Memantau fluktuasi skor klinis digital yang langsung terintegrasi dengan tabel Supabase.</p></div>', unsafe_allow_html=True)

        # 📌 PILAR 3
        st.write("")
        st.markdown("### 🎯 3. Analisis Dampak Insecure / Membandingkan Diri")
        col_l3_v, col_l3_e = st.columns(2)
        with col_l3_v:
            with st.container(border=True):
                trigger_df = user_df.groupby('social_compare')['skor_gad'].mean().reset_index()
                fig_l3 = px.bar(trigger_df, x='social_compare', y='skor_gad', color='social_compare', labels={'skor_gad': 'Rata-rata Skor GAD-7'})
                fig_l3.update_layout(plot_bgcolor='#FFFFFF', paper_bgcolor='#FFFFFF', margin=dict(l=10, r=10, t=10, b=10))
                st.plotly_chart(fig_l3, use_container_width=True)
        with col_l3_e:
            st.markdown('<div style="background-color: #E3F2FD; padding: 24px; border-radius: 14px; border: 1px solid #BBDEFB;"><h4 style="color: #0D47A1 !important; margin-bottom: 15px;">💡 Analisis Faktor Pemicu</h4><p style="color: #1565C0 !important; line-height: 1.6;">Melihat korelasi aktivitas insecure di media sosial terhadap grafik rata-rata kecemasan user.</p></div>', unsafe_allow_html=True)

        # 📌 PILAR 4
        st.write("")
        st.markdown("### ⏱️ 4. Pengaruh Waktu Layar (Screen Time) terhadap Durasi Tidur")
        col_l4_v, col_l4_e = st.columns(2)
        with col_l4_v:
            with st.container(border=True):
                fig_l4 = px.bar(user_df, x='tanggal', y=['screen_time', 'waktu_tidur'], barmode='group')
                fig_l4.update_layout(plot_bgcolor='#FFFFFF', paper_bgcolor='#FFFFFF', margin=dict(l=10, r=10, t=10, b=10))
                st.plotly_chart(fig_l4, use_container_width=True)
        with col_l4_e:
            avg_screen = round(user_df['screen_time'].mean(), 1)
            avg_sleep = round(user_df['waktu_tidur'].mean(), 1)
            st.markdown(f'<div style="background-color: #E3F2FD; padding: 24px; border-radius: 14px; border: 1px solid #BBDEFB;"><h4 style="color: #0D47A1 !important; margin-bottom: 15px;">💡 Analisis Dampak Gaya Hidup</h4><p style="color: #1565C0 !important; line-height: 1.6;">Rata-rata screen time harian Anda berada di angka <b>{avg_screen} Jam</b> dengan durasi tidur <b>{avg_sleep} Jam</b>.</p></div>', unsafe_allow_html=True)

        # 📌 PILAR 5
        st.write("")
        st.markdown("### 🏛️ 5. Pemetaan Profil Risiko Gangguan Depresi per Platform")
        col_l5_v, col_l5_e = st.columns(2)
        with col_l5_v:
            with st.container(border=True):
                platform_df = user_df.groupby('platform')['skor_phq'].mean().reset_index()
                fig_l5 = px.bar(platform_df, x='platform', y='skor_phq', color='platform')
                fig_l5.update_layout(plot_bgcolor='#FFFFFF', paper_bgcolor='#FFFFFF', margin=dict(l=10, r=10, t=10, b=10))
                st.plotly_chart(fig_l5, use_container_width=True)
        with col_l5_e:
            max_toxic = platform_df.sort_values(by='skor_phq', ascending=False).iloc[0]['platform'] if not platform_df.empty else "Belum Diketahui"
            st.markdown(f'<div style="background-color: #E3F2FD; padding: 24px; border-radius: 14px; border: 1px solid #BBDEFB;"><h4 style="color: #0D47A1 !important; margin-bottom: 15px;">💡 Deteksi Ekosistem Berisiko</h4><p style="color: #1565C0 !important; line-height: 1.6;">Platform <b>{max_toxic}</b> terdeteksi memberikan porsi nilai depresi tertinggi bagi psikologis Anda harian.</p></div>', unsafe_allow_html=True)

        # DETAIL TABEL LOG REKAM MEDIS
        st.write("")
        st.markdown("### 🗃️ Riwayat Log Rekam Medis Digital Lengkap")
        with st.container(border=True):
            display_df = user_df[['tanggal', 'skor_gad', 'keparahan_gad', 'skor_phq', 'keparahan_phq', 'screen_time', 'waktu_tidur', 'platform']].copy()
            display_df['tanggal'] = display_df['tanggal'].dt.strftime('%Y-%m-%d')
            display_df.columns = ['Tanggal Evaluasi', 'Skor GAD-7', 'Kondisi Kecemasan', 'Skor PHQ-9', 'Kondisi Depresi', 'Waktu Layar (Jam)', 'Tidur (Jam)', 'Platform Terlama']
            st.dataframe(display_df, use_container_width=True, hide_index=True)

    else:
        st.markdown(
            """
            <div style="background-color: rgba(255,255,255,0.92); border: 2px dashed #7F8C8D; padding: 40px; border-radius: 14px; text-align: center;">
                <h3>Belum Ada Riwayat Laporan Terbaca</h3>
                <p>Silakan isi log kuesioner terlebih dahulu di menu nomor 2 untuk membuat rekam medis pertama Anda.</p>
            </div>
            """, unsafe_allow_html=True
        )
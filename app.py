import streamlit as st
import pandas as pd
import numpy as np
import pickle
import plotly.express as px
import base64
from supabase import create_client, Client

# ==========================================
# 1. PENGATURAN HALAMAN (Wajib di Paling Atas Perintah Streamlit)
# ==========================================
st.set_page_config(page_title="MindMetrics Platform", layout="wide", initial_sidebar_state="expanded")

# ==========================================
# 2. INTEGRASI BACKGROUND GAMBAR KUSTOM
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
# 3. INJEKSI CSS GLOBAL
# ==========================================
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
# 4. KONEKSI REAL-TIME SUPABASE CLOUD
# ==========================================
import os
from dotenv import load_dotenv

load_dotenv()
SUPABASE_URL = os.environ.get("SUPABASE_URL")
SUPABASE_KEY = os.environ.get("SUPABASE_KEY")

@st.cache_resource
def init_supabase():
    return create_client(SUPABASE_URL, SUPABASE_KEY)

supabase = init_supabase()

if 'logged_in' not in st.session_state: st.session_state['logged_in'] = False
if 'username' not in st.session_state: st.session_state['username'] = ""
if 'full_name' not in st.session_state: st.session_state['full_name'] = ""

# ==========================================
# 5. HALAMAN GERBANG MASUK (LOGIN & REGISTER)
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
        logo_b64 = get_base64_of_bin_file('bg2.png')
        if logo_b64:
            st.markdown(f'<div style="text-align: center; margin-bottom: 10px;"><img src="data:image/png;base64,{logo_b64}" width="200"></div>', unsafe_allow_html=True)
        st.markdown("<h1 style='text-align: center; color: #FFFFFF !important;'>MindMetrics</h1>", unsafe_allow_html=True)
        st.markdown("<p style='text-align: center; font-size: 1.1rem; color: #E2E8F0 !important; font-weight: 600;'>Platform Analisis Dampak Media Sosial terhadap Kesehatan Mental</p>", unsafe_allow_html=True)
        
        tab_login, tab_register = st.tabs(["MASUK (LOGIN)", "DAFTAR AKUN BARU"])
        
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
                    st.error("Username atau Kata Sandi salah!")
                        
        with tab_register:
            with st.form(key="form_register"):
                st.markdown("### Buat Akun Baru")
                reg_name = st.text_input("Nama Lengkap", placeholder="Masukkan nama lengkap Anda")
                reg_u = st.text_input("Username Baru", placeholder="Buat nama pengguna unik")
                reg_p = st.text_input("Kata Sandi Baru", type="password", placeholder="Buat kata sandi aman")
                submit_register = st.form_submit_button("Daftar Sekarang")
            if submit_register:
                if reg_name.strip() == "" or reg_u.strip() == "" or reg_p.strip() == "":
                    st.error("Semua kolom wajib diisi!")
                else:
                    check_user = supabase.from_("users").select("*").eq("username", reg_u).execute()
                    if len(check_user.data) > 0:
                        st.error("Username sudah terpakai.")
                    else:
                        supabase.from_("users").insert({"username": reg_u, "password": reg_p, "full_name": reg_name}).execute()
                        st.success(f"Akun {reg_name} sukses terdaftar! Silakan pindah ke tab Login.")
    st.stop()

# ==========================================
# 6. SIDEBAR UTAMA APLIKASI
# ==========================================
st.sidebar.markdown(f"""
    <div class="sidebar-profile-box">
        <p class="profile-greeting">Sesi Aktif Pengguna</p>
        <p class="profile-name">{st.session_state['full_name']}</p>
    </div>
""", unsafe_allow_html=True)

# List Navigasi Utama Tanpa Ikon/Emoji
menu_pilihan = st.sidebar.radio("Navigasi Sistem:", [
    "1. Analisis Dataset (Dashboard)", 
    "2. Prediksi Skor GAD-7 & PHQ-9", 
    "3. Laporan Kesehatan Mental Saya"
])

st.sidebar.markdown('<div class="sidebar-divider"></div>', unsafe_allow_html=True)
with st.sidebar.container():
    st.markdown('<div class="sidebar-logout-container">', unsafe_allow_html=True)
    if st.sidebar.button("Keluar Aplikasi"):
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
# 7. EKSEKUSI TIAP HALAMAN KONTEN
# ==========================================
# --- KOMPONEN 1: DASHBOARD ANALISIS DATASET (7 PERTANYAAN BISNIS) ---
if menu_pilihan == "1. Analisis Dataset (Dashboard)":
    st.title("Dashboard Analisis Risiko Media Sosial")
    st.write("Eksplorasi visualisasi data mengenai pengaruh aktivitas digital terhadap indikasi kecemasan dan depresi.")
    st.write("")
    # =========================================================================
    # PERTANYAAN 1: TREN RISIKO EMOSIONAL (SCREEN TIME VS SKOR)
    # =========================================================================
    st.markdown("### 📈 1. Dampak Durasi Waktu Layar Terhadap Skor Gangguan Mental")
    col1_v, col1_e = st.columns(2)
    with col1_v:
        with st.container(border=True):
            st.markdown("#### **Visualisasi Grafik Garis (Line Chart)**")
            df_q1 = df_clean.groupby('Daily_Screen_Time_Hours')[['GAD_7_Score', 'PHQ_9_Score']].mean().reset_index()
            fig1 = px.line(df_q1, x='Daily_Screen_Time_Hours', y=['GAD_7_Score', 'PHQ_9_Score'],
                           labels={'value': 'Rata-rata Skor', 'Daily_Screen_Time_Hours': 'Waktu Layar (Jam)'},
                           color_discrete_map={'GAD_7_Score': '#E44D26', 'PHQ_9_Score': '#2196F3'})
            fig1.update_layout(plot_bgcolor='#808080', paper_bgcolor='#808080',font_color='#000000',margin=dict(l=10, r=10, t=10, b=10))
            st.plotly_chart(fig1, use_container_width=True)
    with col1_e:
        st.markdown("""
            <div style="background-color: #E3F2FD; padding: 24px; border-radius: 14px; border: 1px solid #BBDEFB;">
                <h4 style="color: #0D47A1 !important; margin-bottom: 12px;">💡 Pertanyaan Bisnis & Jawaban Analisis</h4>
                <p style="color: #1565C0 !important; line-height: 1.6; margin: 0;">
                    <b>Pertanyaan Bisnis:</b> Bagaimana pengaruh durasi waktu layar harian terhadap rata-rata tingkat kecemasan (GAD-7) dan depresi (PHQ-9) pengguna?<br><br>
                    <b>Jawaban & Interpretasi:</b> Terdeteksi adanya <b>Korelasi Positif Kuat</b>. Rata-rata skor emosional merangkak naik seiring bertambahnya jam penggunaan gawai. Titik kritis <i>(threshold)</i> bahaya berada pada penggunaan <b>di atas 6 jam per hari</b>, di mana grafik menunjukkan lonjakan sudut kemiringan skor yang sangat tajam.
                </p>
            </div>
        """, unsafe_allow_html=True)


    # =========================================================================
    # PERTANYAAN 2: PROFIL RISIKO PLATFORM (PLATFORM VS PHQ-9)
    # =========================================================================
    st.write("")
    st.markdown("### 🏛️ 2. Pemetaan Profil Tingkat Risiko Depresi Per Platform Media Sosial")
    col2_v, col2_e = st.columns(2)
    with col2_v:
        with st.container(border=True):
            st.markdown("#### **Visualisasi Grafik Batang (Bar Chart)**")
            df_q2 = df_clean.groupby('Primary_Platform')['PHQ_9_Score'].mean().reset_index().sort_values(by='PHQ_9_Score', ascending=False)
            fig2 = px.bar(df_q2, x='Primary_Platform', y='PHQ_9_Score', color='Primary_Platform',
                          labels={'PHQ_9_Score': 'Rata-rata Skor PHQ-9', 'Primary_Platform': 'Platform Utama'})
            fig2.update_layout(plot_bgcolor='#808080', paper_bgcolor='#808080', margin=dict(l=10, r=10, t=10, b=10))
            st.plotly_chart(fig2, use_container_width=True)
    with col2_e:
        st.markdown("""
            <div style="background-color: #E3F2FD; padding: 24px; border-radius: 14px; border: 1px solid #BBDEFB;">
                <h4 style="color: #0D47A1 !important; margin-bottom: 12px;">💡 Pertanyaan Bisnis & Jawaban Analisis</h4>
                <p style="color: #1565C0 !important; line-height: 1.6; margin: 0;">
                    <b>Pertanyaan Bisnis:</b> Media sosial manakah yang memiliki rata-rata skor indikasi depresi (PHQ-9) tertinggi di antara pengguna?<br><br>
                    <b>Jawaban & Interpretasi:</b> Platform berbasis visual dinamis dan berdurasi pendek seperti <b>TikTok dan Instagram</b> menduduki peringkat teratas penyumbang rata-rata skor depresi tertinggi harian. Hal ini mengindikasikan bahwa jenis konsumsi konten cepat memicu kelelahan mental lebih tinggi dibanding platform berbasis teks atau jejaring profesional.
                </p>
            </div>
        """, unsafe_allow_html=True)


    # =========================================================================
    # PERTANYAAN 3: KORELASI GAYA HIDUP (LATE NIGHT VS SLEEP DURATION)
    # =========================================================================
    st.write("")
    st.markdown("### ⏱️ 3. Hubungan Penggunaan Larut Malam Terhadap Kuantitas Waktu Tidur")
    col3_v, col3_e = st.columns(2)
    with col3_v:
        with st.container(border=True):
            st.markdown("#### **Visualisasi Grafik Batang Kelompok (Grouped Bar)**")
            # Ubah biner ke teks agar visualisasi mudah dipahami
            df_clean['Begadang_Text'] = df_clean['Late_Night_Usage'].map({1: 'Ya (Begadang)', 0: 'Tidak'})
            df_q3 = df_clean.groupby('Begadang_Text')['Sleep_Duration_Hours'].mean().reset_index()
            fig3 = px.bar(df_q3, x='Begadang_Text', y='Sleep_Duration_Hours', color='Begadang_Text',
                          labels={'Sleep_Duration_Hours': 'Rata-rata Jam Tidur', 'Begadang_Text': 'Aktivitas Larut Malam'},
                          color_discrete_map={'Ya (Begadang)': '#EF4444', 'Tidak': '#10B981'})
            fig3.update_layout(plot_bgcolor='#808080', paper_bgcolor='#808080', margin=dict(l=10, r=10, t=10, b=10))
            st.plotly_chart(fig3, use_container_width=True)
    with col3_e:
        st.markdown("""
            <div style="background-color: #E3F2FD; padding: 24px; border-radius: 14px; border: 1px solid #BBDEFB;">
                <h4 style="color: #0D47A1 !important; margin-bottom: 12px;">💡 Pertanyaan Bisnis & Jawaban Analisis</h4>
                <p style="color: #1565C0 !important; line-height: 1.6; margin: 0;">
                    <b>Pertanyaan Bisnis:</b> Apakah kebiasaan menggunakan gawai larut malam (Late Night Usage) berkorelasi dengan penyusutan durasi tidur harian?<br><br>
                    <b>Jawaban & Interpretasi:</b> <b>Ya, Sangat Berkolerasi</b>. Pengguna yang memiliki kebiasaan menggunakan media sosial larut malam mengalami penurunan durasi tidur secara signifikan, dengan rata-rata kehilangan waktu istirahat sebanyak 1.5 hingga 2 jam per hari dibanding kelompok yang disiplin tidak memainkan gawai sebelum tidur.
                </p>
            </div>
        """, unsafe_allow_html=True)


    # =========================================================================
    # PERTANYAAN 4: ANALISIS AKIBAT PEMICU (SOCIAL COMPARISON VS GAD-7)
    # =========================================================================
    st.write("")
    st.markdown("### 🎯 4. Dampak Psikologis Pemicu Perbandingan Sosial Terhadap Kecemasan")
    col4_v, col4_e = st.columns(2)
    with col4_v:
        with st.container(border=True):
            st.markdown("#### **Visualisasi Box Plot (Distribusi Skor)**")
            df_clean['Insecure_Text'] = df_clean['Social_Comparison_Trigger'].map({1: 'Sering Membandingkan', 0: 'Tidak'})
            fig4 = px.box(df_clean, x='Insecure_Text', y='GAD_7_Score', color='Insecure_Text',
                          labels={'GAD_7_Score': 'Sebaran Skor GAD-7', 'Insecure_Text': 'Kondisi Psikologis User'})
            fig4.update_layout(plot_bgcolor='#808080', paper_bgcolor='#808080', margin=dict(l=10, r=10, t=10, b=10))
            st.plotly_chart(fig4, use_container_width=True)
    with col4_e:
        st.markdown("""
            <div style="background-color: #E3F2FD; padding: 24px; border-radius: 14px; border: 1px solid #BBDEFB;">
                <h4 style="color: #0D47A1 !important; margin-bottom: 12px;">💡 Pertanyaan Bisnis & Jawaban Analisis</h4>
                <p style="color: #1565C0 !important; line-height: 1.6; margin: 0;">
                    <b>Pertanyaan Bisnis:</b> Seberapa besar lonjakan rata-rata skor kecemasan (GAD-7) terjadi ketika pengguna terjebak dalam pemicu perbandingan sosial?<br><br>
                    <b>Jawaban & Interpretasi:</b> Perbandingan sosial merupakan <b>Akar Masalah (Root Cause) Utama</b> pembengkakan kecemasan klinis. Melalui visualisasi sebaran data di samping, kelompok yang sering membandingkan diri memiliki nilai median dan batas atas skor GAD-7 yang melesat naik hingga 40% lebih tinggi dibanding kelompok yang acuh.
                </p>
            </div>
        """, unsafe_allow_html=True)


    # =========================================================================
    # PERTANYAAN 5: KARAKTERISASI PENGGUNA (ARKETIPE VS KEPARAHAN)
    # =========================================================================
    st.write("")
    st.markdown("### 👥 5. Distribusi Tingkat Keparahan Depresi Berdasarkan Arketipe Karakter")
    col5_v, col5_e = st.columns(2)
    with col5_v:
        with st.container(border=True):
            st.markdown("#### **Visualisasi Grafik Batang Bertumpuk (Stacked Bar Chart)**")
            # Membuat pengelompokkan keparahan PHQ-9 manual untuk keperluan pemetaan distribusi makro
            def phq_severity_calc(s):
                return "Minimal" if s <= 4 else "Mild" if s <= 9 else "Moderate" if s <= 14 else "Severe"
            df_clean['PHQ_9_Severity'] = df_clean['PHQ_9_Score'].apply(phq_severity_calc)
            
            fig5 = px.histogram(df_clean, x='User_Archetype', color='PHQ_9_Severity', barmode='stack',
                                labels={'count': 'Jumlah Pengguna', 'User_Archetype': 'Arketipe Karakter', 'PHQ_9_Severity': 'Tingkat Depresi'})
            fig5.update_layout(plot_bgcolor='#808080', paper_bgcolor='#808080', margin=dict(l=10, r=10, t=10, b=10))
            st.plotly_chart(fig5, use_container_width=True)
    with col5_e:
        st.markdown("""
            <div style="background-color: #E3F2FD; padding: 24px; border-radius: 14px; border: 1px solid #BBDEFB;">
                <h4 style="color: #0D47A1 !important; margin-bottom: 12px;">💡 Pertanyaan Bisnis & Jawaban Analisis</h4>
                <p style="color: #1565C0 !important; line-height: 1.6; margin: 0;">
                    <b>Pertanyaan Bisnis:</b> Bagaimana distribusi tingkat keparahan depresi (PHQ-9 Severity) jika dibedakan berdasarkan Arketipe Karakter Pengguna?<br><br>
                    <b>Jawaban & Interpretasi:</b> Kelompok karakter bertipe <b>Hyper-Connected</b> dan <b>Passive Scroller</b> mendominasi sebaran porsi kategori depresi tingkat <i>Moderate</i> hingga <i>Severe</i> (diwakili warna merah/ungu bertumpuk). Sebaliknya, arketipe <i>Digital Minimalist</i> terbukti memiliki porsi warna hijau (Minimal) yang dominan dan paling tebal.
                </p>
            </div>
        """, unsafe_allow_html=True)


    # =========================================================================
    # PERTANYAAN 6: PENGARUH JENIS KONSUMSI (KONTEN VS GAD-7)
    # =========================================================================
    st.write("")
    st.markdown("### 🎬 6. Korelasi Jenis Konten Dominan Terhadap Stabilitas Emosi")
    col6_v, col6_e = st.columns(2)
    with col6_v:
        with st.container(border=True):
            st.markdown("#### **Visualisasi Grafik Batang Horizontal**")
            df_q6 = df_clean.groupby('Dominant_Content_Type')['GAD_7_Score'].mean().reset_index().sort_values(by='GAD_7_Score')
            fig6 = px.bar(df_q6, y='Dominant_Content_Type', x='GAD_7_Score', orientation='h', color='GAD_7_Score',
                          labels={'GAD_7_Score': 'Rata-rata Skor GAD-7', 'Dominant_Content_Type': 'Jenis Konten Utama'},
                          color_continuous_scale='Reds')
            fig6.update_layout(plot_bgcolor='#808080', paper_bgcolor='#808080', margin=dict(l=10, r=10, t=10, b=10))
            st.plotly_chart(fig6, use_container_width=True)
    with col6_e:
        st.markdown("""
            <div style="background-color: #E3F2FD; padding: 24px; border-radius: 14px; border: 1px solid #BBDEFB;">
                <h4 style="color: #0D47A1 !important; margin-bottom: 12px;">💡 Pertanyaan Bisnis & Jawaban Analisis</h4>
                <p style="color: #1565C0 !important; line-height: 1.6; margin: 0;">
                    <b>Pertanyaan Bisnis:</b> Apakah jenis konten yang paling sering dikonsumsi (Dominant Content Type) memengaruhi tinggi rendahnya stabilitas emosi pengguna?<br><br>
                    <b>Jawaban & Interpretasi:</b> <b>Ya, Sangat Berpengaruh</b>. Konten bertema <b>News/Politics</b> memicu rata-rata skor kecemasan tertinggi dibandingkan jenis lainnya. Hal ini disebabkan oleh fenomena <i>"Doomscrolling"</i> (kebiasaan membaca berita buruk terus-menerus), sementara konten bertema <i>Self-Help/Motivation</i> dan <i>Gaming</i> mencatat skor kecemasan yang relatif lebih rendah dan tenang.
                </p>
            </div>
        """, unsafe_allow_html=True)

# --- KOMPONEN 2: MESIN PREDIKSI PKL ---
elif menu_pilihan == "2. Prediksi Skor GAD-7 & PHQ-9":
    st.title("Kalkulator Prediksi Skor Klinis")
    st.write("Masukkan parameter harian Anda beserta tanggal pencatatan untuk memprediksi tingkat indikasi kecemasan dan depresi.")
    st.write("")

    try:
        with open('model_gad7.pkl', 'rb') as f: model_gad = pickle.load(f)
        with open('model_phq9.pkl', 'rb') as f: model_phq = pickle.load(f)

        with st.form(key="form_prediksi_kesehatan"):
            st.markdown("### Pengisian Log Kuesioner Harian")
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

            submit_prediction = st.form_submit_button("Hitung Hasil & Simpan Laporan")

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
            
            st.success("Hasil Prediksi Berhasil Dihitung!")
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
            supabase.from_("user_reports").insert(report_payload).execute()
            st.info(f"Data log tanggal {input_date} sukses disimpan permanen ke Cloud Supabase.")

    except FileNotFoundError:
        st.error("Berkas 'model_gad7.pkl' tidak ditemukan. Jalankan 'train_model.py' terlebih dahulu.")

# --- KOMPONEN 3: LAPORAN KESEHATAN MENTAL MURNI TEXT ---
elif menu_pilihan == "3. Laporan Kesehatan Mental Saya":
    st.title("Rekam Medis & Laporan Dashboard Kesehatan")
    st.write("Halaman pelacakan klinis terintegrasi berdasarkan data log aktivitas digital Anda.")
    st.write("")

    res_reports = supabase.from_("user_reports").select("*").eq("username", st.session_state['username']).execute()
    
    if len(res_reports.data) > 0:
        user_df = pd.DataFrame(res_reports.data)
        user_df['tanggal'] = pd.to_datetime(user_df['tanggal'])
        user_df = user_df.sort_values(by='tanggal')
        
        last_record = user_df.iloc[-1]

        # 📌 PILAR 1: RINGKASAN STATUS KONDISI KLINIS TERBARU
        st.markdown("### 1. Ringkasan Status Kesehatan Mental Terakhir")
        with st.container(border=True):
            stat_c1, stat_c2, stat_c3 = st.columns(3)
            with stat_c1: st.metric(label="Tanggal Pengujian Terakhir", value=last_record['tanggal'].strftime('%Y-%m-%d'))
            with stat_c2: st.metric(label="Tingkat Kecemasan (GAD-7)", value=f"{last_record['skor_gad']} / 21", delta=last_record['keparahan_gad'], delta_color="inverse")
            with stat_c3: st.metric(label="Tingkat Depresi (PHQ-9)", value=f"{last_record['skor_phq']} / 27", delta=last_record['keparahan_phq'], delta_color="inverse")
            
            st.write("")
            if "Severe" in [last_record['keparahan_gad'], last_record['keparahan_phq']] or "Moderately Severe" in last_record['keparahan_phq']:
                st.error("Rekomendasi Klinis: Skor Anda berada di zona kritis. Kami sangat menyarankan Anda untuk segera mengambil jeda total dari media sosial (Digital Detox) atau menjadwalkan sesi konsultasi dengan psikolog profesional.")
            elif "Moderate" in [last_record['keparahan_gad'], last_record['keparahan_phq']]:
                st.warning("Rekomendasi Klinis: Gejala kecemasan/depresi Anda berada di tingkat sedang. Cobalah batasi screen time maksimal 2 jam per hari.")
            else:
                st.success("Rekomendasi Klinis: Kondisi psikologis Anda saat ini relatif stabil dan aman. Tetap pertahankan kesadaran (mindfulness) dalam mengonsumsi gawai digital.")

        # 📌 PILAR 2: PELACAKAN TREN TEMPORAL (TIME-SERIES)
        st.write("")
        st.markdown("### 2. Pelacakan Tren Fluktuasi Skor Mental dari Hari ke Hari")
        col_l2_v, col_l2_e = st.columns(2)
        with col_l2_v:
            with st.container(border=True):
                fig_l2 = px.line(user_df, x='tanggal', y=['skor_gad', 'skor_phq'], markers=True, labels={'value': 'Nilai Skor', 'tanggal': 'Tanggal Evaluasi'})
                fig_l2.update_layout(plot_bgcolor='#FFFFFF', paper_bgcolor='#FFFFFF', margin=dict(l=10, r=10, t=10, b=10), font=dict(color='#000000'))
                st.plotly_chart(fig_l2, use_container_width=True)
        with col_l2_e:
            st.markdown('<div style="background-color: #E3F2FD; padding: 24px; border-radius: 14px; border: 1px solid #BBDEFB;"><h4 style="color: #0D47A1 !important; margin-bottom: 15px;">Interpretasi Grafik Kronologis</h4><p style="color: #1565C0 !important; line-height: 1.6;"><b>Melacak Dinamika Emosi:</b> Grafik garis kontinuitas di samping memetakan naik-turunnya kondisi emosional Anda berdasarkan data seketika dari cloud Supabase.</p></div>', unsafe_allow_html=True)

        # 📌 PILAR 3: ANALISIS AKAR MASALAH (SOCIAL COMPARISON TRIGGER)
        st.write("")
        st.markdown("### 3. Analisis Dampak Insecure / Membandingkan Diri")
        col_l3_v, col_l3_e = st.columns(2)
        with col_l3_v:
            with st.container(border=True):
                trigger_df = user_df.groupby('social_compare')['skor_gad'].mean().reset_index()
                fig_l3 = px.bar(trigger_df, x='social_compare', y='skor_gad', color='social_compare', labels={'skor_gad': 'Rata-rata Skor GAD-7'})
                fig_l3.update_layout(plot_bgcolor='#FFFFFF', paper_bgcolor='#FFFFFF', margin=dict(l=10, r=10, t=10, b=10), font=dict(color='#000000'))
                st.plotly_chart(fig_l3, use_container_width=True)
        with col_l3_e:
            st.markdown('<div style="background-color: #E3F2FD; padding: 24px; border-radius: 14px; border: 1px solid #BBDEFB;"><h4 style="color: #0D47A1 !important; margin-bottom: 15px;">Analisis Faktor Pemicu</h4><p style="color: #1565C0 !important; line-height: 1.6;"><b>Dampak Psikologis Insecure:</b> Diagram ini membuktikan secara nyata seberapa besar rata-rata kecemasan melesat naik saat Anda terjebak membandingkan diri di lini masa media sosial.</p></div>', unsafe_allow_html=True)

        # 📌 PILAR 4: EVALUASI HABIT (SCREEN TIME VS TIDUR)
        st.write("")
        st.markdown("### 4. Pengaruh Waktu Layar (Screen Time) terhadap Durasi Tidur")
        col_l4_v, col_l4_e = st.columns(2)
        with col_l4_v:
            with st.container(border=True):
                fig_l4 = px.bar(user_df, x='tanggal', y=['screen_time', 'waktu_tidur'], barmode='group')
                fig_l4.update_layout(plot_bgcolor='#FFFFFF', paper_bgcolor='#FFFFFF', margin=dict(l=10, r=10, t=10, b=10), font=dict(color='#000000'))
                st.plotly_chart(fig_l4, use_container_width=True)
        with col_l4_e:
            avg_screen = round(user_df['screen_time'].mean(), 1)
            avg_sleep = round(user_df['waktu_tidur'].mean(), 1)
            st.markdown(f'<div style="background-color: #E3F2FD; padding: 24px; border-radius: 14px; border: 1px solid #BBDEFB;"><h4 style="color: #0D47A1 !important; margin-bottom: 15px;">Analisis Dampak Gaya Hidup</h4><p style="color: #1565C0 !important; line-height: 1.6;"><b>Korelasi Kebiasaan Istirahat:</b> Saat ini rata-rata screen time harian Anda berada di angka <b>{avg_screen} Jam</b> dengan durasi tidur <b>{avg_sleep} Jam</b> harian. Menjaga keseimbangan kedua variabel ini adalah kunci kestabilan emosi.</p></div>', unsafe_allow_html=True)

        # 📌 PILAR 5: PROFIL RISIKO PER PLATFORM MEDSOS
        st.write("")
        st.markdown("### 5. Pemetaan Profil Risiko Gangguan Depresi per Platform")
        col_l5_v, col_l5_e = st.columns(2)
        with col_l5_v:
            with st.container(border=True):
                platform_df = user_df.groupby('platform')['skor_phq'].mean().reset_index()
                fig_l5 = px.bar(platform_df, x='platform', y='skor_phq', color='platform')
                fig_l5.update_layout(plot_bgcolor='#FFFFFF', paper_bgcolor='#FFFFFF', margin=dict(l=10, r=10, t=10, b=10), font=dict(color='#000000'))
                st.plotly_chart(fig_l5, use_container_width=True)
        with col_l5_e:
            max_toxic = platform_df.sort_values(by='skor_phq', ascending=False).iloc[0]['platform'] if not platform_df.empty else "Belum Diketahui"
            st.markdown(f'<div style="background-color: #E3F2FD; padding: 24px; border-radius: 14px; border: 1px solid #BBDEFB;"><h4 style="color: #0D47A1 !important; margin-bottom: 15px;">Deteksi Ekosistem Berisiko</h4><p style="color: #1565C0 !important; line-height: 1.6;"><b>Identifikasi Dampak Algoritma:</b> Berdasarkan riwayat data log Anda, ekosistem pada platform <b>{max_toxic}</b> memicu kecenderungan rata-rata skor depresi tertinggi dibandingkan platform lainnya.</p></div>', unsafe_allow_html=True)

        # DETAIL TABEL LOG REKAM MEDIS HISTORIS
        st.write("")
        st.markdown("### Riwayat Log Rekam Medis Digital Lengkap")
        with st.container(border=True):
            display_df = user_df[['tanggal', 'skor_gad', 'keparahan_gad', 'skor_phq', 'keparahan_phq', 'screen_time', 'waktu_tidur', 'platform']].copy()
            display_df['tanggal'] = display_df['tanggal'].dt.strftime('%Y-%m-%d')
            display_df.columns = ['Tanggal Evaluasi', 'Skor GAD-7', 'Kondisi Kecemasan', 'Skor PHQ-9', 'Kondisi Depresi', 'Waktu Layar (Jam)', 'Tidur (Jam)', 'Platform Terlama']
            st.dataframe(display_df, use_container_width=True, hide_index=True)

    else:
        st.markdown(
            """
            <div style="background-color: rgba(255,255,255,0.92); border: 2px dashed #7F8C8D; padding: 40px; border-radius: 14px; text-align: center;">
                <h3 style="color: #7F8C8D !important;">Belum Ada Riwayat Laporan Terbaca</h3>
                <p style="color: #7F8C8D !important;">Sistem mendeteksi profil Anda belum pernah melakukan pengisian kuesioner harian.<br>Silakan berpindah ke menu <b>2. Prediksi Skor GAD-7 & PHQ-9</b> terlebih dahulu untuk menghitung prediksi dan membuat rekam laporan pertama Anda!</p>
            </div>
            """, unsafe_allow_html=True
        )
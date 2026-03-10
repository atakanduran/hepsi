import streamlit as st
import pandas as pd
import numpy as np
import requests
from datetime import datetime

# 1. SAYFA VE GÜVENLİK AYARLARI
st.set_page_config(page_title="Zeytin OS | Yönetim", page_icon="🌳", layout="wide")

# --- GÜVENLİK KONTROLÜ ---
if "authenticated" not in st.session_state:
    st.session_state.authenticated = False

# --- TELEGRAM FONKSİYONU ---
def send_telegram_msg(mesaj):
    try:
        token = st.secrets["TELEGRAM_TOKEN"]
        chat_id = st.secrets["CHAT_ID"]
        url = f"https://api.telegram.org/bot{token}/sendMessage"
        params = {"chat_id": chat_id, "text": mesaj}
        requests.get(url, params=params, timeout=10)
    except:
        pass

# --- GİRİŞ EKRANI ---
if not st.session_state.authenticated:
    st.title("🔐 Zeytin OS Güvenli Giriş")
    sifre = st.text_input("Yönetici Şifresi:", type="password")
    if st.button("Sisteme Giriş Yap"):
        if sifre == "1925": # Burayı dilediğin şifreyle değiştirebilirsin Başkan
            st.session_state.authenticated = True
            send_telegram_msg("🔓 Bilgi: Yönetici girişi yapıldı.")
            st.rerun()
        else:
            st.error("Hatalı Şifre!")
    st.stop()

# --- SİSTEM DEĞİŞKENLERİ ---
if "depo_seviyesi" not in st.session_state:
    st.session_state.depo_seviyesi = 65
if "hidrofor_calisiyor" not in st.session_state:
    st.session_state.hidrofor_calisiyor = False
if "sulama_aktif" not in st.session_state:
    st.session_state.sulama_aktif = False

# --- HAVA DURUMU FONKSİYONU ---
def get_weather():
    try:
        api_key = st.secrets["OPENWEATHER_API_KEY"]
        url = f"https://api.openweathermap.org/data/2.5/weather?q=Bergama,TR&appid={api_key}&units=metric&lang=tr"
        data = requests.get(url).json()
        return {"temp": data["main"]["temp"], "desc": data["weather"][0]["description"].capitalize(), "wind": data["wind"]["speed"]}
    except:
        return {"temp": "N/A", "desc": "Bağlantı Yok", "wind": 0}

# --- SOL MENÜ ---
with st.sidebar:
    st.title("🌳 Zeytin OS v1.2")
    st.info("📍 İzmir / Bergama")
    st.divider()
    
    sayfa = st.radio("Yönetim Paneli:", ["Zeytinlik Hesap Merkezi", "Çiftlik Gözlem & Sulama", "Su Deposu ve Hidrofor"])
    
    st.divider()
    if st.button("🔴 Güvenli Çıkış Yap"):
        st.session_state.authenticated = False
        send_telegram_msg("🔒 Bilgi: Yönetici çıkışı yapıldı.")
        st.rerun()

# --- 1. SAYFA: ZEYTİNLİK HESAP MERKEZİ ---
if sayfa == "Zeytinlik Hesap Merkezi":
    st.title("📈 Verim Analizi ve Finansal Hesaplama")
    
    w = get_weather()
    st.write(f"🌤️ **Anlık Bergama:** {w['temp']}°C | {w['desc']} | Rüzgar: {w['wind']} m/s")
    st.divider()

    col1, col2 = st.columns(2)
    with col1:
        st.subheader("🌳 Tarla ve Ağaç Verimi")
        donum = st.number_input("Toplam Arazi (Dönüm)", value=8.0, step=0.1)
        agac_basi = st.slider("Ağaç Başı Verim (Kg)", 5, 60, 25)
        
        st.write("### 📜 Referans Verim Listeleri")
        liste_secimi = st.radio("Verim Modeli Seçin:", ["Özel Hesaplama", "Tariş Standart", "İspanyol (Arbequina) Yoğun"])
        
        if liste_secimi == "Tariş Standart":
            donum_basi_agac = 25
            st.caption("Tariş Standart: 6x6 metre dikim modeli.")
        elif liste_secimi == "İspanyol (Arbequina) Yoğun":
            donum_basi_agac = 150
            st.caption("İspanyol Model: 1.5x4 metre sık dikim modeli.")
        else:
            donum_basi_agac = st.number_input("Dönümdeki Ağaç Sayısı", value=20)

        toplam_agac = donum * donum_basi_agac
        toplam_zeytin = toplam_agac * agac_basi
        st.metric("Toplam Ağaç / Tahmini Hasat", f"{int(toplam_agac)} Adet / {toplam_zeytin:,.0f} Kg")

    with col2:
        st.subheader("💧 Yağ Oranı ve Ekonomi")
        # Yağ oranını ondalık olarak istedin Başkan, step 0.1 yaptık
        yag_randiman = st.number_input("Yağ Randımanı (Kaç kiloda 1 litre?)", value=4.5, step=0.1)
        litre_fiyat = st.number_input("Yağ Litre Fiyatı (TL)", value=350)
        
        toplam_yag = toplam_zeytin / yag_randiman
        toplam_gelir = toplam_yag * litre_fiyat
        
        st.success(f"Tahmini Yağ Üretimi: {int(toplam_yag)} Litre")
        st.metric("Beklenen Brüt Gelir", f"{toplam_gelir:,.0f} TL")

# --- 2. SAYFA: ÇİFTLİK GÖZLEM & SULAMA ---
elif sayfa == "Çiftlik Gözlem & Sulama":
    st.title("🛰️ Çiftlik Gözlem & Aktif Sulama Kontrolü")
    
    # SULAMA KONTROL ÜNİTESİ (Dün taslaktaki gibi)
    st.subheader("🚿 Ana Sulama Sistemi")
    c1, c2 = st.columns([1, 2])
    
    with c1:
        if st.session_state.sulama_aktif:
            st.error("🚿 SULAMA DEVREDE")
            if st.button("🛑 SULAMAYI DURDUR", use_container_width=True):
                st.session_state.sulama_aktif = False
                send_telegram_msg("🚿 Bilgi: Tarlada sulama sistemi durduruldu.")
                st.rerun()
        else:
            st.success("💤 SİSTEM HAZIR")
            if st.button("💧 SULAMAYI BAŞLAT", use_container_width=True):
                st.session_state.sulama_aktif = True
                send_telegram_msg("🚿 Uyarı: Tarlada sulama işlemi başlatıldı!")
                st.rerun()
    
    with c2:
        st.info("Sulama sistemi aktifken Kart-1 üzerinden hat basıncı ve akış verileri anlık takip edilir.")
        st.metric("Ana Hat Akışı", "120 L/dk" if st.session_state.sulama_aktif else "0 L/dk")

    st.divider()
    st.subheader("🌱 Bölgesel Nem Haritası (Kart-1)")
    nem_cols = st.columns(4)
    for i in range(1, 21):
        with nem_cols[(i-1) % 4]:
            n = np.random.randint(25, 45)
            st.write(f"{'🟢' if n >= 32 else '🔴'} Bölge {i:02d}: %{n}")

# --- 3. SAYFA: SU DEPOSU VE HİDROFOR ---
elif sayfa == "Su Deposu ve Hidrofor":
    st.title("💧 Su Deposu ve Hidrofor (Kart-2)")
    
    l, r = st.columns([1, 2])
    with l:
        st.markdown(f'<div style="background:#f0f0f0; border:2px solid #555; border-radius:10px; width:70px; height:250px; position:relative; margin:auto;"><div style="background:#2196F3; width:100%; height:{st.session_state.depo_seviyesi}%; position:absolute; bottom:0; border-radius:0 0 8px 8px;"></div></div>', unsafe_allow_html=True)
        st.write(f"<p style='text-align:center; font-weight:bold;'>%{st.session_state.depo_seviyesi}</p>", unsafe_allow_html=True)

    with r:
        if st.session_state.hidrofor_calisiyor:
            st.error("⚡ Hidrofor Çalışıyor")
            if st.button("🔴 DURDUR", use_container_width=True):
                st.session_state.hidrofor_calisiyor = False
                send_telegram_msg("✅ Bilgi: Hidrofor durduruldu.")
                st.rerun()
        else:
            st.success("💤 Beklemede")
            if st.button("🟢 BAŞLAT", use_container_width=True):
                st.session_state.hidrofor_calisiyor = True
                send_telegram_msg("⚡ Uyarı: Hidrofor başlatıldı!")
                st.rerun()

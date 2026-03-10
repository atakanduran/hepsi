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
        chat_ids = [st.secrets["CHAT_ID"], st.secrets["CHAT_ID_2"]]
        for cid in chat_ids:
            url = f"https://api.telegram.org/bot{token}/sendMessage"
            params = {"chat_id": cid, "text": mesaj}
            requests.get(url, params=params, timeout=10)
    except:
        pass

# --- HAVA DURUMU FONKSİYONU ---
def get_weather():
    try:
        api_key = st.secrets["OPENWEATHER_API_KEY"]
        url = f"https://api.openweathermap.org/data/2.5/weather?q=Bergama,TR&appid={api_key}&units=metric&lang=tr"
        data = requests.get(url).json()
        return {"temp": data["main"]["temp"], "desc": data["weather"][0]["description"].capitalize(), "hum": data["main"]["humidity"]}
    except:
        return {"temp": "N/A", "desc": "Bağlantı Yok", "hum": 0}

# --- GİRİŞ EKRANI ---
if not st.session_state.authenticated:
    st.title("🚜 Çiftlik Yönetimine Hoşgeldiniz")
    sifre = st.text_input("Yönetici Şifresi:", type="password")
    if st.button("Sisteme Giriş Yap"):
        if sifre == "1925": 
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

# Otomatik Hidrofor Kapatma
if st.session_state.depo_seviyesi >= 95 and st.session_state.hidrofor_calisiyor:
    st.session_state.hidrofor_calisiyor = False
    send_telegram_msg("🛑 Otomatik Bilgi: Depo %95 doluluğa ulaştı, hidrofor kapatıldı.")

KART1_PIL, KART2_PIL = 85, 9

# --- SOL MENÜ (SIDEBAR) ---
with st.sidebar:
    st.title("🌳 Zeytin OS v1.8")
    st.info("📍 İzmir / Bergama")
    w = get_weather()
    st.write(f"🌡️ **Hava:** {w['temp']}°C | %{w['hum']} Nem")
    
    st.divider()
    st.subheader("🔋 Batarya Durumları")
    # İki gösterge olarak ayarlandı
    st.caption(f"Kart-1 (Sensör): %{KART1_PIL}")
    st.progress(KART1_PIL/100)
    st.caption(f"Kart-2 (Depo): %{KART2_PIL}")
    st.progress(KART2_PIL/100)
    
    st.divider()
    sayfa = st.radio("Yönetim Paneli:", ["Zeytinlik Hesap Merkezi", "Çiftlik Gözlem & Sulama", "Su Deposu ve Hidrofor"])
    if st.button("🔴 Güvenli Çıkış Yap"):
        st.session_state.authenticated = False
        send_telegram_msg("🔒 Bilgi: Yönetici çıkışı yapıldı.")
        st.rerun()

# --- 1. SAYFA: ZEYTİNLİK HESAP MERKEZİ ---
if sayfa == "Zeytinlik Hesap Merkezi":
    st.title("📈 Verim Analizi ve Finansal Hesaplama")
    col1, col2 = st.columns(2)
    with col1:
        st.subheader("🌳 Tarla ve Ağaç")
        donum = st.number_input("Toplam Arazi (Dönüm)", value=8.0, step=0.1)
        agac_basi = st.slider("Ağaç Başı Verim (Kg)", 5, 60, 25)
        donum_basi_agac = st.slider("Dönümdeki Ağaç Sayısı", 20, 200, 20, 5)
        toplam_zeytin = (donum * donum_basi_agac) * agac_basi
        st.metric("Tahmini Toplam Hasat", f"{toplam_zeytin:,.0f} Kg")
    with col2:
        st.subheader("💧 Yağ ve Ekonomi")
        yag_verimi_ondalik = st.number_input("Yağ Verim Oranı (Örn: 0.20 - 0.25)", value=0.22, step=0.01)
        litre_fiyat = st.number_input("Yağ Litre Fiyatı (TL)", value=350)
        toplam_yag_kg = toplam_zeytin * yag_verimi_ondalik
        st.success(f"Tahmini Üretim: {int(toplam_yag_kg)} Litre")
        st.metric("Beklenen Brüt Gelir", f"{toplam_yag_kg * litre_fiyat:,.0f} TL")

# --- 2. SAYFA: ÇİFTLİK GÖZLEM & SULAMA ---
elif sayfa == "Çiftlik Gözlem & Sulama":
    st.title("🛰️ Çiftlik Gözlem & Sulama")
    
    c_btn, c_stat = st.columns([1, 1])
    with c_btn:
        if st.button("💧 SULAMAYI BAŞLAT" if not st.session_state.sulama_aktif else "🛑 SULAMAYI DURDUR", use_container_width=True):
            st.session_state.sulama_aktif = not st.session_state.sulama_aktif
            send_telegram_msg(f"🚿 Sulama {'başlatıldı' if st.session_state.sulama_aktif else 'durduruldu'}.")
            st.rerun()
    with c_stat:
        # Su basıncı / akış yeri geri geldi
        st.metric("Ana Hat Akışı", "120 L/dk" if st.session_state.sulama_aktif else "0 L/dk")
    
    if st.session_state.sulama_aktif:
        st.warning("⚠️ SULAMA SİSTEMİ AKTİF - Hatlarda su akışı var.")

    st.divider()
    nem_cols = st.columns(4)
    for i in range(1, 21):
        with nem_cols[(i-1)%4]:
            n = np.random.randint(25, 45)
            icon = "🟢" if (st.session_state.sulama_aktif or n >= 32) else "🔴"
            st.write(f"{icon} Bölge {i:02d} %{100 if st.session_state.sulama_aktif else n}")

# --- 3. SAYFA: SU DEPOSU VE HİDROFOR ---
elif sayfa == "Su Deposu ve Hidrofor":
    st.title("💧 Su Deposu ve Hidrofor")
    
    if st.session_state.hidrofor_calisiyor:
        st.info("⚡ HİDROFOR DOLUM YAPIYOR - Depo seviyesi artıyor.")
        
    l, r = st.columns([1, 2])
    with l:
        st.markdown(f'<div style="background:#f0f0f0; border:2px solid #555; border-radius:10px; width:70px; height:250px; position:relative; margin:auto;"><div style="background:#2196F3; width:100%; height:{st.session_state.depo_seviyesi}%; position:absolute; bottom:0; border-radius:0 0 8px 8px;"></div></div>', unsafe_allow_html=True)
        st.write(f"<p style='text-align:center; font-weight:bold;'>%{st.session_state.depo_seviyesi}</p>", unsafe_allow_html=True)
    with r:
        if st.button("🟢 BAŞLAT" if not st.session_state.hidrofor_calisiyor else "🔴 DURDUR", use_container_width=True):
            st.session_state.hidrofor_calisiyor = not st.session_state.hidrofor_calisiyor
            send_telegram_msg(f"✅ Hidrofor {'başlatıldı' if st.session_state.hidrofor_calisiyor else 'durduruldu'}.")
            st.rerun()

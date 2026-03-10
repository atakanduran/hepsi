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
        return {
            "temp": data["main"]["temp"], 
            "desc": data["weather"][0]["description"].capitalize(), 
            "hum": data["main"]["humidity"]
        }
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
if "uyari_gonderildi_k1" not in st.session_state:
    st.session_state.uyari_gonderildi_k1 = False
if "uyari_gonderildi_k2" not in st.session_state:
    st.session_state.uyari_gonderildi_k2 = False

# Sabit Batarya Değerleri (Test için)
KART1_PIL, KART2_PIL = 85, 9

# --- BATARYA KRİTİK UYARI KONTROLÜ ---
if KART1_PIL <= 10 and not st.session_state.uyari_gonderildi_k1:
    send_telegram_msg(f"🚨 Kart-1 şarjı %{KART1_PIL}'a düştü!")
    st.session_state.uyari_gonderildi_k1 = True

if KART2_PIL <= 10 and not st.session_state.uyari_gonderildi_k2:
    send_telegram_msg(f"🚨 Kart-2 şarjı %{KART2_PIL}'a düştü!")
    st.session_state.uyari_gonderildi_k2 = True

# Otomatik Hidrofor Kapatma
if st.session_state.depo_seviyesi >= 95 and st.session_state.hidrofor_calisiyor:
    st.session_state.hidrofor_calisiyor = False
    send_telegram_msg("🛑 Otomatik Bilgi: Depo %95 doluluğa ulaştı, hidrofor kapatıldı.")

# --- SOL MENÜ (SIDEBAR) ---
with st.sidebar:
    st.title("🌳 Zeytin OS v1.9")
    st.info("📍 İzmir / Bergama")
    
    w = get_weather()
    st.write(f"🌡️ **Sıcaklık:** {w['temp']}°C")
    st.write(f"💧 **Nem:** %{w['hum']}")
    st.write(f"☁️ **Gökyüzü:** {w['desc']}") # Bulut/Hava durumu eklendi
    
    st.divider()
    st.subheader("🔋 Batarya Durumları")
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
        st.metric("Tah

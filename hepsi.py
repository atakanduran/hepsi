import streamlit as st
import pandas as pd
import numpy as np
import requests
from datetime import datetime

# 1. SAYFA AYARLARI
st.set_page_config(page_title="Zeytin OS | İzmir-Bergama", page_icon="🌳", layout="wide")

# --- FONKSİYONLAR ---
def send_telegram_msg(mesaj):
    try:
        token = st.secrets["TELEGRAM_TOKEN"]
        chat_id = st.secrets["CHAT_ID"]
        url = f"https://api.telegram.org/bot{token}/sendMessage"
        params = {"chat_id": chat_id, "text": mesaj}
        requests.get(url, params=params, timeout=10)
    except:
        pass

def get_weather():
    try:
        api_key = st.secrets["OPENWEATHER_API_KEY"]
        # Bergama koordinatları üzerinden çekiyoruz
        url = f"https://api.openweathermap.org/data/2.5/weather?q=Bergama,TR&appid={api_key}&units=metric&lang=tr"
        data = requests.get(url).json()
        return {
            "temp": data["main"]["temp"],
            "desc": data["weather"][0]["description"].capitalize(),
            "wind": data["wind"]["speed"],
            "humidity": data["main"]["humidity"]
        }
    except:
        return {"temp": "N/A", "desc": "Bağlantı Yok", "wind": 0, "humidity": 0}

# --- SİSTEM DEĞİŞKENLERİ ---
if "depo_seviyesi" not in st.session_state:
    st.session_state.depo_seviyesi = 65
if "hidrofor_calisiyor" not in st.session_state:
    st.session_state.hidrofor_calisiyor = False

KART1_PIL, KART2_PIL = 85, 9

# --- SOL MENÜ (NAVİGASYON) ---
with st.sidebar:
    st.title("🌳 Zeytin OS v1.0")
    st.info("📍 İzmir / Bergama")
    st.divider()
    
    sayfa = st.radio(
        "Görüntüleme Merkezi:",
        ["Zeytinlik Hesap Paneli", "Su Deposu ve Hidrofor", "Çiftlik Gözlem Merkezi"]
    )
    
    st.divider()
    st.write("### 🔋 Cihaz Durumları")
    st.caption(f"Kart-1 (Sensör): %{KART1_PIL}")
    st.progress(KART1_PIL/100)
    st.caption(f"Kart-2 (Depo): %{KART2_PIL}")
    st.progress(KART2_PIL/100)
    if KART2_PIL <= 10:
        st.warning("⚠️ Kart-2 Batarya Kritik!")

# --- 1. SAYFA: HESAP PANELİ & HAVA DURUMU (TASLAK) ---
if sayfa == "Zeytinlik Hesap Paneli":
    st.title("📈 Zeytinlik Verim ve Hava Durumu")
    
    # Hava Durumu Şeridi
    w = get_weather()
    w_col1, w_col2, w_col3, w_col4 = st.columns(4)
    w_col1.metric("Sıcaklık", f"{w['temp']}°C")
    w_col2.metric("Durum", w['desc'])
    w_col3.metric("Rüzgar", f"{w['wind']} m/s")
    w_col4.metric("Nem", f"%{w['humidity']}")
    
    st.divider()
    
    col1, col2 = st.columns(2)
    with col1:
        st.subheader("🌳 Arazi ve Ağaç Hesabı")
        donum = st.number_input("Toplam Arazi (Dönüm)", value=8.0, step=0.5)
        donum_basi_agac = st.number_input("Dönümdeki Ağaç Sayısı", value=20)
        agac_basi_zeytin = st.slider("Ağaç Başı Zeytin Verimi (Kg)", 5, 60, 25)
        
        toplam_agac = donum * donum_basi_agac
        toplam_zeytin = toplam_agac * agac_basi_zeytin
        
        st.info(f"Toplam Ağaç: {int(toplam_agac)} | Toplam Zeytin: {toplam_zeytin:,.0f} Kg")

    with col2:
        st.subheader("💰 Yağ ve Gelir Tahmini")
        randiman = st.selectbox("Yağ Oranı (1 Litre için kaç kg zeytin?)", [3, 4, 5, 6], index=2)
        litre_fiyat = st.number_input("Yağ Litre Satış Fiyatı (TL)", value=350)
        
        toplam_yag = toplam_zeytin / randiman
        toplam_gelir = toplam_yag * litre_fiyat
        
        st.success(f"Tahmini Yağ: {int(toplam_yag)} Litre")
        st.metric("Beklenen Brüt Gelir", f"{toplam_gelir:,.0f} TL")

# --- 2. SAYFA: SU DEPOSU VE HİDROFOR ---
elif sayfa == "Su Deposu ve Hidrofor":
    st.title("💧 Su Deposu ve Hidrofor Kontrolü")
    
    c1, c2, c3 = st.columns(3)
    c1.metric("Depo Seviyesi", f"%{st.session_state.depo_seviyesi}")
    c2.metric("Hidrofor", "AÇIK" if st.session_state.hidrofor_calisiyor else "KAPALI")
    c3.metric("Kart-2 Pil", f"%{KART2_PIL}")

    st.divider()
    l, r = st.columns([1, 2])
    
    with l:
        st.subheader("💧 Depo")
        st.markdown(f'<div style="background:#f0f0f0; border:2px solid #555; border-radius:10px; width:70px; height:250px; position:relative; margin:auto;"><div style="background:#2196F3; width:100%; height:{st.session_state.depo_seviyesi}%; position:absolute; bottom:0; border-radius:0 0 8px 8px;"></div></div>', unsafe_allow_html=True)
        st.write(f"<p style='text-align:center'><b>%{st.session_state.depo_seviyesi}</b></p>", unsafe_allow_html=True)

    with r:
        st.subheader("⚙️ Operasyon")
        if st.session_state.hidrofor_calisiyor:
            st.error("⚡ Hidrofor Şu An Çalışıyor")
            if st.button("🔴 DURDUR", use_container_width=True):
                st.session_state.hidrofor_calisiyor = False
                send_telegram_msg("✅ Bilgi: Hidrofor durduruldu.")
                st.rerun()
        else:
            st.success("💤 Hidrofor Beklemede")
            if st.button("🟢 BAŞLAT", use_container_width=True):
                st.session_state.hidrofor_calisiyor = True
                send_telegram_msg("⚡ Uyarı: Hidrofor başlatıldı!")
                st.rerun()
        
        st.divider()
        st.subheader("📜 Doldurma Geçmişi")
        st.table(pd.DataFrame({"Tarih": ["09.03.26", "07.03.26"], "Miktar": ["1200L", "2500L"], "Süre": ["45dk", "90dk"]}))

# --- 3. SAYFA: ÇİFTLİK GÖZLEM MERKEZİ ---
elif sayfa == "Çiftlik Gözlem Merkezi":
    st.title("🛰️ Anlık Sensör Verileri (Kart-1)")
    
    st.metric("Ana Hat Akışı", "120 L/dk", delta="Stabil")
    
    st.divider()
    st.subheader("🌱 20 Bölge Toprak Nemi")
    cols = st.columns(4)
    for i in range(1, 21):
        with cols[(i-1) % 4]:
            nem = np.random.randint(25, 45)
            st.write(f"{'🟢' if nem >= 32 else '🔴'} Bölge {i:02d}: %{nem}")

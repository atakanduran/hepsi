import streamlit as st
import pandas as pd
import numpy as np
import requests
from datetime import datetime

# 1. SAYFA VE TEMA AYARLARI
st.set_page_config(page_title="Zeytin OS | İzmir-Bergama", page_icon="🌳", layout="wide")

# --- GENEL FONKSİYONLAR ---
def send_telegram_msg(mesaj):
    try:
        token = st.secrets["TELEGRAM_TOKEN"]
        chat_id = st.secrets["CHAT_ID"]
        url = f"https://api.telegram.org/bot{token}/sendMessage"
        params = {"chat_id": chat_id, "text": mesaj}
        response = requests.get(url, params=params, timeout=10)
        if response.status_code == 200:
            st.toast("Bildirim Gönderildi! ✅")
    except:
        pass

# --- SİSTEM DEĞİŞKENLERİ (BELLEK) ---
if "depo_seviyesi" not in st.session_state:
    st.session_state.depo_seviyesi = 65
if "hidrofor_calisiyor" not in st.session_state:
    st.session_state.hidrofor_calisiyor = False

# --- SOL ANA MENÜ (NAVİGASYON) ---
with st.sidebar:
    st.title("🌳 Zeytin OS v1.0")
    st.subheader("İzmir / Bergama Operasyonu")
    st.divider()
    
    # ANA MENÜ SEÇİMİ
    ana_menu = st.selectbox(
        "Gitmek İstediğiniz Bölüm:",
        ["🏠 Ana Kontrol Paneli", "📡 Ar-Ge & Sensör Takibi", "📈 Verim & Ekonomi Analizi"]
    )
    
    st.divider()
    # Kart Durumları (Hepsinde Görünsün)
    st.write("### 🔋 Cihaz Durumları")
    st.caption("Kart-1 (Sensör): %85")
    st.progress(0.85)
    st.caption("Kart-2 (Depo): %9")
    st.progress(0.09)
    if st.session_state.hidrofor_calisiyor:
        st.warning("⚡ Hidrofor Şu An Aktif!")

# --- BÖLÜM 1: ANA KONTROL PANELİ (ÖZET) ---
if ana_menu == "🏠 Ana Kontrol Paneli":
    st.title("🏠 Zeytinlik Genel Durum Özet")
    
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Hava Durumu", "18°C", delta="☀️ Açık")
    with col2:
        st.metric("Sıradaki İşlem", "Gübreleme", delta="3 Gün Kaldı")
    with col3:
        st.metric("Depo Durumu", f"%{st.session_state.depo_seviyesi}", delta="Kritik" if st.session_state.depo_seviyesi < 20 else "Normal")

    st.divider()
    st.subheader("🗓️ Haftalık Görev Listesi")
    st.checkbox("Sulama Sistemi Filtre Temizliği", value=True)
    st.checkbox("Arbequina Fidanları Kontrolü", value=False)
    st.checkbox("Biyogaz Sistemi Gübre Girişi", value=False)

# --- BÖLÜM 2: AR-GE & SENSÖR TAKİBİ (DÜNKÜ PANEL) ---
elif ana_menu == "📡 Ar-Ge & Sensör Takibi":
    st.title("📡 Anlık Sensör ve Depo Kontrolü")
    
    tab_sensor, tab_depo = st.tabs(["🌱 Toprak Nemi", "💧 Depo & Hidrofor"])
    
    with tab_sensor:
        st.subheader("20 Bölge Nem Durumu")
        cols = st.columns(4)
        for i in range(1, 21):
            with cols[(i-1)%4]:
                n = np.random.randint(28, 42)
                st.write(f"{'🟢' if n >= 32 else '🔴'} Bölge {i:02d}: %{n}")
    
    with tab_depo:
        l, r = st.columns([1, 2])
        with l:
            st.markdown(f'<div style="background:#f0f0f0; border:2px solid #555; border-radius:10px; width:70px; height:250px; position:relative; margin:auto;"><div style="background:#2196F3; width:100%; height:{st.session_state.depo_seviyesi}%; position:absolute; bottom:0; border-radius:0 0 8px 8px;"></div></div>', unsafe_allow_html=True)
            st.write(f"<p style='text-align:center'><b>%{st.session_state.depo_seviyesi}</b></p>", unsafe_allow_html=True)
        with r:
            if st.session_state.hidrofor_calisiyor:
                st.error("⚡ Hidrofor Çalışıyor...")
                if st.button("🔴 DURDUR", use_container_width=True):
                    st.session_state.hidrofor_calisiyor = False
                    send_telegram_msg("✅ Hidrofor Durduruldu.")
                    st.rerun()
            else:
                st.success("💤 Beklemede")
                if st.button("🟢 BAŞLAT", use_container_width=True):
                    st.session_state.hidrofor_calisiyor = True
                    send_telegram_msg("⚡ Hidrofor Başlatıldı!")
                    st.rerun()

# --- BÖLÜM 3: VERİM & EKONOMİ ANALİZİ (İLK TASLAK) ---
elif ana_menu == "📈 Verim & Ekonomi Analizi":
    st.title("📈 Hasat Tahmini ve Finansal Durum")
    
    c1, c2 = st.columns(2)
    with c1:
        st.subheader("🌳 Zeytin Verim Hesabı")
        agac_sayisi = st.number_input("Toplam Ağaç Sayısı", value=150)
        tahmini_verim = st.slider("Ağaç Başı Verim (Kg)", 5, 50, 20)
        toplam_hasat = agac_sayisi * tahmini_verim
        st.info(f"Beklenen Toplam Hasat: {toplam_hasat} Kg")
        
    with c2:
        st.subheader("💰 Tahmini Gelir (Yağlık)")
        fiyat = st.number_input("Zeytinyağı Litre Fiyatı (TL)", value=350)
        # 5 kilo zeytinden 1 litre yağ hesabı
        toplam_yag = toplam_hasat / 5
        st.success(f"Tahmini Gelir: {toplam_yag * fiyat:,.0f} TL")

    st.divider()
    st.subheader("📜 Sulama ve Operasyon Geçmişi")
    st.table(pd.DataFrame({"İşlem": ["Sulama", "Gübreleme", "İlaçlama"], "Tarih": ["09.03.26", "01.03.26", "20.02.26"], "Maliyet": ["1200 TL", "4500 TL", "2200 TL"]}))

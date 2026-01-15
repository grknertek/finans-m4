import streamlit as st
import pandas as pd
import plotly.express as px
import os
from datetime import datetime

# Sayfa Ayarları
st.set_page_config(page_title="M4 Finans Takipçisi", page_icon="💰", layout="wide")

# Başlık
st.title("💸 Kişisel Finans Paneli")

# Excel Dosya Yolu
DOSYA_ADI = "Butce_Takip.xlsx"

# --- YAN MENÜ (VERİ GİRİŞİ) ---
st.sidebar.header("Harcama Ekle")

with st.sidebar.form("harcama_formu", clear_on_submit=True):
    kategori = st.selectbox("Kategori", ["Yemek", "Ulaşım", "Market", "Eğitim/Kitap", "Eğlence", "Yatırım"])
    aciklama = st.text_input("Açıklama (Örn: Kahve)")
    tutar = st.number_input("Tutar (TL)", min_value=0.0, step=10.0)
    ekle_butonu = st.form_submit_button("Harcamayı Kaydet")

    if ekle_butonu:
        tarih = datetime.now().strftime("%Y-%m-%d %H:%M")
        yeni_veri = pd.DataFrame({
            "Tarih": [tarih],
            "Kategori": [kategori],
            "Açıklama": [aciklama],
            "Tutar": [tutar]
        })
        
        # Dosya varsa ekle, yoksa yarat
        if os.path.exists(DOSYA_ADI):
            mevcut_df = pd.read_excel(DOSYA_ADI)
            guncel_df = pd.concat([mevcut_df, yeni_veri], ignore_index=True)
        else:
            guncel_df = yeni_veri
            
        guncel_df.to_excel(DOSYA_ADI, index=False)
        st.sidebar.success(f"✅ {tutar} TL eklendi!")

# --- ANA EKRAN (RAPORLAR) ---

if os.path.exists(DOSYA_ADI):
    df = pd.read_excel(DOSYA_ADI)
    
    # Üstteki Özet Kartları (KPI)
    col1, col2, col3 = st.columns(3)
    toplam_harcama = df["Tutar"].sum()
    en_cok_harcanan = df.groupby("Kategori")["Tutar"].sum().idxmax()
    islem_sayisi = len(df)

    col1.metric("Toplam Harcama", f"{toplam_harcama} TL")
    col2.metric("En Çok Harcanan", en_cok_harcanan)
    col3.metric("İşlem Sayısı", islem_sayisi)

    st.divider() # Çizgi çek

    # Grafik ve Tabloyu Yan Yana Koyalım
    col_grafik, col_tablo = st.columns([2, 1]) # Grafik geniş, tablo dar olsun

    with col_grafik:
        st.subheader("Harcama Dağılımı")
        fig = px.pie(df, values='Tutar', names='Kategori', hole=0.4, 
                     color_discrete_sequence=px.colors.sequential.RdBu)
        st.plotly_chart(fig, use_container_width=True)

    with col_tablo:
        st.subheader("Son İşlemler")
        st.dataframe(df.tail(10).sort_index(ascending=False), hide_index=True)

else:
    st.info("Henüz hiç harcama girmedin. Sol menüden ilk harcamayı ekle! 👈")
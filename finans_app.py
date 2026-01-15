import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime
from streamlit_gsheets import GSheetsConnection

# Sayfa Ayarları
st.set_page_config(page_title="M4 Finans (Bulut)", page_icon="☁️", layout="wide")
st.title("💸 Bulut Finans Paneli")

# --- GOOGLE SHEETS BAĞLANTISI ---
# Bağlantıyı kuruyoruz
conn = st.connection("gsheets", type=GSheetsConnection)

# Veriyi Google'dan Oku (Cache süresi 0 olsun ki anlık görelim)
data = conn.read(worksheet="Sayfa1", ttl=0)
df = pd.DataFrame(data)

# --- YAN MENÜ (VERİ GİRİŞİ) ---
st.sidebar.header("Harcama Ekle")

with st.sidebar.form("harcama_formu", clear_on_submit=True):
    kategori = st.selectbox("Kategori", ["Yemek", "Ulaşım", "Market", "Eğitim/Kitap", "Eğlence", "Yatırım"])
    aciklama = st.text_input("Açıklama")
    tutar = st.number_input("Tutar (TL)", min_value=0.0, step=10.0)
    ekle_butonu = st.form_submit_button("Harcamayı Kaydet")

    if ekle_butonu:
        tarih = datetime.now().strftime("%Y-%m-%d %H:%M")
        
        # Yeni satır oluştur
        yeni_veri = pd.DataFrame([{
            "Tarih": tarih,
            "Kategori": kategori,
            "Açıklama": aciklama,
            "Tutar": tutar
        }])
        
        # Eski veriyle birleştir
        guncel_df = pd.concat([df, yeni_veri], ignore_index=True)
        
        # Google Sheets'e Geri Yaz
        conn.update(worksheet="Sayfa1", data=guncel_df)
        
        st.sidebar.success("✅ Buluta Kaydedildi!")
        # Sayfayı yenilemek için (manuel çözüm)
        st.rerun()

# --- ANA EKRAN (RAPORLAR) ---

if not df.empty:
    # Sayısal işlemleri garantiye al
    df["Tutar"] = pd.to_numeric(df["Tutar"], errors='coerce').fillna(0)

    col1, col2, col3 = st.columns(3)
    toplam_harcama = df["Tutar"].sum()
    
    # En çok harcanan kategori (Hata vermemesi için kontrol)
    if not df.empty:
        en_cok_harcanan = df.groupby("Kategori")["Tutar"].sum().idxmax()
    else:
        en_cok_harcanan = "-"
        
    islem_sayisi = len(df)

    col1.metric("Toplam Harcama", f"{toplam_harcama:.2f} TL")
    col2.metric("Lider Kategori", en_cok_harcanan)
    col3.metric("İşlem Sayısı", islem_sayisi)

    st.divider()

    col_grafik, col_tablo = st.columns([2, 1])

    with col_grafik:
        st.subheader("Harcama Dağılımı")
        fig = px.pie(df, values='Tutar', names='Kategori', hole=0.4, 
                     color_discrete_sequence=px.colors.sequential.RdBu)
        st.plotly_chart(fig, use_container_width=True)

    with col_tablo:
        st.subheader("Son İşlemler")
        st.dataframe(df.tail(10).sort_index(ascending=False), hide_index=True)

else:
    st.info("Tablo boş! Sol taraftan ilk harcamayı gir. 👈")
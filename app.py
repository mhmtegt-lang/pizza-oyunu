import streamlit as st
from PIL import Image, ImageDraw, ImageChops
import requests
from io import BytesIO

# --- SAYFA AYARLARI ---
st.set_page_config(page_title="Pizza Karşılaştırma", layout="wide")

# Tasarım ve Okunabilirlik Ayarları
st.markdown("""
    <style>
    .stApp { background-color: #8B4513; }
    h1, h2, p { color: #FFD700 !important; font-family: 'Arial Black', sans-serif; text-align: center; }
    
    /* Butonları cam gibi okunur yapalım */
    .stButton button {
        background-color: #FFD700 !important;
        color: #000000 !important; /* Net Siyah Yazı */
        font-weight: bold !important;
        font-size: 20px !important;
        height: 60px !important;
        width: 100% !important;
        border: 4px solid #5c2b0b !important;
    }
    </style>
    """, unsafe_allow_html=True)

class PizzaEngine:
    def __init__(self):
        # Engellenme riskine karşı daha güvenli bir resim kaynağı ve headers
        self.url = "https://images.unsplash.com/photo-1513104890138-7c749659a591?q=80&w=500&auto=format&fit=crop"
        self.raw_img = self.load_pizza()

    def load_pizza(self):
        try:
            # Tarayıcı gibi istek gönderiyoruz (Engellenmemek için)
            headers = {'User-Agent': 'Mozilla/5.0'}
            response = requests.get(self.url, headers=headers, timeout=10)
            img = Image.open(BytesIO(response.content)).convert("RGBA")
            img = img.resize((500, 500))
            
            # Yuvarlak kesim
            mask = Image.new("L", (500, 500), 0)
            ImageDraw.Draw(mask).ellipse((10, 10, 490, 490), fill=255)
            output = Image.new("RGBA", (500, 500), (0, 0, 0, 0))
            output.paste(img, (0, 0), mask=mask)
            return output
        except:
            # Eğer internet yine hata verirse acil durum için renkli bir daire çiz
            img = Image.new('RGBA', (500, 500), (200, 150, 100, 255))
            draw = ImageDraw.Draw(img)
            draw.ellipse((10, 10, 490, 490), fill=(255, 200, 100), outline=(100, 50, 0), width=10)
            return img

    def cut_pizza(self, slices, get_slice_only=False):
        img = self.raw_img.copy()
        angle = 360 / slices
        
        # Maske oluştur
        mask = Image.new("L", (500, 500), 255)
        draw = ImageDraw.Draw(mask)
        # Dilimi kes (İlk dilim: -90 dereceden başlar)
        draw.pieslice([0, 0, 500, 500], -90, -90 + angle, fill=0)
        
        if get_slice_only:
            # Sadece dilimi göster (Maskeyi ters çevir)
            mask = ImageChops.invert(mask)
            
        img.putalpha(ImageChops.multiply(img.split()[-1], mask))
        return img

# --- UYGULAMA MANTIĞI ---
if 'view' not in st.session_state:
    st.session_state.view = 'main'

engine = PizzaEngine()

st.title("🍕 Hangi Dilim Daha Büyük?")

if st.session_state.view == 'main':
    col1, col2 = st.columns(2)
    
    with col1:
        st.header("1/4 Pizza")
        st.image(engine.raw_img, use_container_width=True)
        if st.button("BU DİLİMİ AL"):
            st.session_state.view = 'compare_1_4'
            st.rerun()

    with col2:
        st.header("1/12 Pizza")
        st.image(engine.raw_img, use_container_width=True)
        if st.button("ŞU DİLİMİ AL"):
            st.session_state.view = 'compare_1_12'
            st.rerun()

else:
    # Karşılaştırma Ekranı
    slices = 4 if st.session_state.view == 'compare_1_4' else 12
    
    col_left, col_right = st.columns([1, 1])
    
    with col_left:
        st.subheader("Pizzanın Kalanı")
        st.image(engine.cut_pizza(slices, False), use_container_width=True)
        
    with col_right:
        st.subheader("Senin Aldığın Dilim")
        st.image(engine.cut_pizza(slices, True), use_container_width=True)
        
    st.markdown("---")
    if slices == 4:
        st.success("KOCAMAN BİR DİLİM! 😋")
        st.write("Pizza sadece 4'e bölündüğü için her bir parça devasa!")
    else:
        st.warning("MİNİCİK BİR DİLİM... 🧐")
        st.write("Pizza 12'ye bölündü, dilimler kürdan gibi ince kaldı!")
        
    if st.button("TEKRAR DENE 🔄"):
        st.session_state.view = 'main'
        st.rerun()

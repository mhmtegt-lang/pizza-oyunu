import streamlit as st
from PIL import Image, ImageDraw
import math

# --- SAYFA AYARLARI ---
st.set_page_config(page_title="Pizza Karşılaştırma", layout="wide")

# --- TASARIM (CSS) ---
st.markdown("""
    <style>
    .stApp { background-color: #5D4037; } 
    h1, h2, h3, p, div { 
        color: #FFECB3 !important; 
        font-family: 'Comic Sans MS', sans-serif; 
        text-align: center; 
    }
    .fraction-text {
        font-size: 50px;
        font-weight: bold;
        color: #FFD700;
        margin-top: -10px;
    }
    /* Butonları pizzanın hemen altına yapıştır ve belirgin yap */
    .stButton button {
        background-color: #FFD700 !important;
        color: #3E2723 !important;
        font-weight: 900 !important;
        font-size: 20px !important;
        border-radius: 10px !important;
        border: 3px solid #3E2723 !important;
        width: 100% !important;
    }
    .result-box {
        background-color: rgba(0,0,0,0.3);
        border-radius: 20px;
        padding: 20px;
        border: 2px dashed #FFD700;
    }
    </style>
    """, unsafe_allow_html=True)

class PizzaEngine:
    def __init__(self):
        self.size = 500
        self.center = self.size // 2
        self.color_crust = "#D38E45"   
        self.color_cheese = "#FFCA28"  
        self.color_pep = "#C62828"     
        self.color_line = "#8D6E63"

    def _draw_pizza_base(self, draw):
        # Hamur kenarı
        draw.ellipse([20, 20, 480, 480], fill=self.color_crust)
        # Peynir
        draw.ellipse([55, 55, 445, 445], fill=self.color_cheese)
        # Biberoniler
        pep_r = 22
        for r, count in [(80, 6), (160, 10)]:
            for i in range(count):
                angle = math.radians(i * (360/count))
                px = self.center + r * math.cos(angle) - pep_r
                py = self.center + r * math.sin(angle) - pep_r
                draw.ellipse([px, py, px+pep_r*2, py+pep_r*2], fill=self.color_pep)

    def get_full_pizza(self, slices):
        img = Image.new("RGBA", (self.size, self.size), (0,0,0,0))
        draw = ImageDraw.Draw(img)
        self._draw_pizza_base(draw)
        # Kesim çizgileri
        for i in range(slices):
            angle = math.radians(i * (360/slices) - 90)
            draw.line([self.center, self.center, self.center + 230 * math.cos(angle), self.center + 230 * math.sin(angle)], fill=self.color_line, width=4)
        return img

    def get_slice_only(self, slices):
        """ 
        Dilimi tüm resim boyutunda (500x500) bırakıyoruz. 
        Böylece 1/12 gerçekten küçük görünüyor.
        """
        img = Image.new("RGBA", (self.size, self.size), (0,0,0,0))
        draw = ImageDraw.Draw(img)
        self._draw_pizza_base(draw)
        
        mask = Image.new("L", (self.size, self.size), 0)
        mask_draw = ImageDraw.Draw(mask)
        angle_step = 360 / slices
        mask_draw.pieslice([20, 20, 480, 480], -90, -90 + angle_step, fill=255)
        
        img.putalpha(mask)
        return img

# --- DURUM YÖNETİMİ ---
if 'selected_4' not in st.session_state: st.session_state.selected_4 = False
if 'selected_12' not in st.session_state: st.session_state.selected_12 = False

engine = PizzaEngine()

st.title("🍕 Hangi Pizza Seni Daha Çok Doyurur? 🍕")
st.write("Aşağıdaki pizzalara tıkla (butonlara bas) ve tabaklarını doldur!")

# --- SEÇİM ALANI ---
col1, col2 = st.columns(2)

with col1:
    st.header("1/4 Pizza")
    st.image(engine.get_full_pizza(4), use_container_width=True)
    if st.button("Bu Pizzadan Bir Dilim Al"):
        st.session_state.selected_4 = True

with col2:
    st.header("1/12 Pizza")
    st.image(engine.get_full_pizza(12), use_container_width=True)
    if st.button("Şu Pizzadan Bir Dilim Al"):
        st.session_state.selected_12 = True

# --- KARŞILAŞTIRMA ALANI ---
if st.session_state.selected_4 or st.session_state.selected_12:
    st.markdown("---")
    st.markdown("## 🍽️ Senin Tabağın")
    
    res_col1, res_col2 = st.columns(2)
    
    with res_col1:
        if st.session_state.selected_4:
            st.image(engine.get_slice_only(4), use_container_width=True)
            st.markdown('<p class="fraction-text">1/4</p>', unsafe_allow_html=True)
            st.markdown("<div class='result-box'><h3>😋 DOYARSIN!</h3>Bu kocaman bir dilim. Karnın harika doyacak!</div>", unsafe_allow_html=True)
        else:
            st.write("Henüz buradan dilim almadın.")

    with res_col2:
        if st.session_state.selected_12:
            st.image(engine.get_slice_only(12), use_container_width=True)
            st.markdown('<p class="fraction-text">1/12</p>', unsafe_allow_html=True)
            st.markdown("<div class='result-box'><h3>🧐 DOYMAZSIN...</h3>Bu sadece minicik bir atıştırmalık!</div>", unsafe_allow_html=True)
        else:
            st.write("Henüz buradan dilim almadın.")

    # Temizleme Butonu
    st.markdown("<br>", unsafe_allow_html=True)
    if st.button("Tabağı Boşalt ve Yeniden Başla 🔄"):
        st.session_state.selected_4 = False
        st.session_state.selected_12 = False
        st.rerun()

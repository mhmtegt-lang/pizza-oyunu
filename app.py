import streamlit as st
from PIL import Image, ImageDraw
import math

# --- SAYFA AYARLARI ---
st.set_page_config(page_title="Pizza Karşılaştırma", layout="wide")

# --- TASARIM (CSS) ---
st.markdown("""
    <style>
    .stApp { background-color: #5D4037; } 
    h1, h2, h3 { 
        color: #FFD700 !important; 
        font-family: 'Arial Black', sans-serif; 
        text-align: center;
        text-shadow: 2px 2px 5px #000000;
    }
    p, span, div { 
        color: #FFFFFF !important; 
        font-family: 'Comic Sans MS', sans-serif; 
        text-align: center;
        font-weight: bold;
    }
    /* SİYAH BUTON YAZISI İÇİN KESİN ÇÖZÜM */
    div.stButton > button {
        background-color: #FFD700 !important;
        border: 4px solid #2E1A12 !important;
        border-radius: 15px !important;
        height: 70px !important;
        width: 100% !important;
    }
    div.stButton > button * {
        color: #000000 !important; 
        font-weight: 900 !important;
        font-size: 20px !important;
    }
    .tabak-konteynir {
        background-color: rgba(255,255,255,0.1);
        border-radius: 30px;
        padding: 20px;
        border: 2px solid #FFD700;
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
        self.color_line = "#6D4C41"

    def _draw_base_pizza(self, draw):
        # Pizza hamuru ve peyniri
        draw.ellipse([20, 20, 480, 480], fill=self.color_crust)
        draw.ellipse([55, 55, 445, 445], fill=self.color_cheese)
        # Biberoniler
        pep_r = 22
        for r, count in [(85, 6), (165, 10)]:
            for i in range(count):
                angle = math.radians(i * (360/count))
                px = self.center + r * math.cos(angle) - pep_r
                py = self.center + r * math.sin(angle) - pep_r
                draw.ellipse([px, py, px+pep_r*2, py+pep_r*2], fill=self.color_pep)

    def get_pizza_view(self, slices, is_taken=False):
        img = Image.new("RGBA", (self.size, self.size), (0,0,0,0))
        draw = ImageDraw.Draw(img)
        self._draw_base_pizza(draw)
        
        # Kesim çizgileri
        angle_step = 360 / slices
        for i in range(slices):
            angle = math.radians(i * angle_step - 90)
            draw.line([self.center, self.center, self.center + 235 * math.cos(angle), self.center + 235 * math.sin(angle)], fill=self.color_line, width=4)
        
        if is_taken:
            # Dilimi anında siler
            mask = Image.new("L", (self.size, self.size), 255)
            mask_draw = ImageDraw.Draw(mask)
            mask_draw.pieslice([15, 15, 485, 485], -90, -90 + angle_step, fill=0)
            img.putalpha(mask)
        return img

    def get_slice_on_plate(self, slices):
        # Tabak oluştur (Beyaz daire)
        img = Image.new("RGBA", (self.size, self.size), (0,0,0,0))
        draw = ImageDraw.Draw(img)
        draw.ellipse([30, 30, 470, 470], fill="#F5F5F5", outline="#CCCCCC", width=5) # Tabak
        
        # Dilimi çiz
        pizza_img = Image.new("RGBA", (self.size, self.size), (0,0,0,0))
        p_draw = ImageDraw.Draw(pizza_img)
        self._draw_base_pizza(p_draw)
        
        mask = Image.new("L", (self.size, self.size), 0)
        mask_draw = ImageDraw.Draw(mask)
        angle_step = 360 / slices
        mask_draw.pieslice([40, 40, 460, 460], -90, -90 + angle_step, fill=255)
        
        pizza_img.putalpha(mask)
        img.alpha_composite(pizza_img)
        return img

# --- DURUM YÖNETİMİ ---
if 'p4' not in st.session_state: st.session_state.p4 = False
if 'p12' not in st.session_state: st.session_state.p12 = False

engine = PizzaEngine()

st.title("🍕 Hangi Dilim Daha Doyurucu? 🍕")
st.write("Pizzalara tıkla, dilimleri tabaklara al!")

# --- ÜST PANEL ---
col1, col2 = st.columns(2)

with col1:
    st.subheader("Büyük Dilimli Pizza")
    st.image(engine.get_pizza_view(4, st.session_state.p4), use_container_width=True)
    if st.button("BU PİZZADAN DİLİM AL", key="btn4"):
        st.session_state.p4 = True
        st.rerun()

with col2:
    st.subheader("Küçük Dilimli Pizza")
    st.image(engine.get_pizza_view(12, st.session_state.p12), use_container_width=True)
    if st.button("ŞU PİZZADAN DİLİM AL", key="btn12"):
        st.session_state.p12 = True
        st.rerun()

# --- TABAK PANELİ ---
if st.session_state.p4 or st.session_state.p12:
    st.markdown("---")
    st.markdown("## 🍽️ Senin Tabakların")
    
    t_col1, t_col2 = st.columns(2)
    
    with t_col1:
        if st.session_state.p4:
            st.image(engine.get_slice_on_plate(4), use_container_width=True)
            st.markdown("### KOCAMAN DİLİM")
            st.markdown("#### **😋 KARNIN TIKA BASA DOYAR!**")
        else:
            st.write("Bu tabağa henüz dilim almadın.")

    with t_col2:
        if st.session_state.p12:
            st.image(engine.get_slice_on_plate(12), use_container_width=True)
            st.markdown("### KÜÇÜCÜK DİLİM")
            st.markdown("#### **🧐 BU DİLİM SENİ DOYURMAZ...**")
        else:
            st.write("Bu tabağa henüz dilim almadın.")

    if st.button("🍽️ TABAKLARI BOŞALT", key="reset"):
        st.session_state.p4 = False
        st.session_state.p12 = False
        st.rerun()

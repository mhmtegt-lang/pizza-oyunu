import streamlit as st
from PIL import Image, ImageDraw
import math

# --- SAYFA AYARLARI ---
st.set_page_config(page_title="Pizza Kesir Laboratuvarı", layout="wide")

# --- TASARIM (CSS) - BUTON YAZILARINI SİYAH YAPMA VE DOYMA PANELİ ---
st.markdown("""
    <style>
    .stApp { background-color: #5D4037; } 
    h1, h2, h3 { 
        color: #FFD700 !important; 
        font-family: 'Arial Black', sans-serif; 
        text-align: center;
        text-shadow: 2px 2px 5px #000000;
    }
    p, span, div, label { 
        color: #FFFFFF !important; 
        font-family: 'Comic Sans MS', sans-serif; 
        text-align: center;
        font-weight: bold;
    }
    
    /* Kesir Yazısı */
    .kesir-miktari {
        font-size: 55px !important;
        color: #FFD700 !important;
        font-weight: 900 !important;
        margin: 5px 0px;
    }

    /* SİYAH BUTON YAZISI GARANTİSİ */
    div.stButton > button {
        background-color: #FFD700 !important;
        border: 4px solid #2E1A12 !important;
        border-radius: 15px !important;
        height: 70px !important;
        width: 100% !important;
    }
    /* Butonun içindeki her şeyi (yazı, span, div) siyaha zorla */
    div.stButton > button * {
        color: #000000 !important; 
        font-weight: 900 !important;
        font-size: 20px !important;
    }
    
    div.stButton > button:hover {
        background-color: #FFA500 !important;
        transform: scale(1.02);
    }
    
    .input-box {
        background-color: rgba(0,0,0,0.2);
        padding: 20px;
        border-radius: 20px;
        margin-bottom: 20px;
    }
    </style>
    """, unsafe_allow_html=True)

class PizzaEngine:
    """İstenen her n sayısı için dinamik pizza çizen motor."""
    def __init__(self):
        self.size = 500
        self.center = self.size // 2
        self.color_crust = "#D38E45"   
        self.color_cheese = "#FFCA28"  
        self.color_pep = "#C62828"     
        self.color_line = "#6D4C41"

    def _draw_base(self, draw):
        # Pizza tabanı
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
        self._draw_base(draw)
        
        angle_step = 360 / slices
        for i in range(slices):
            angle = math.radians(i * angle_step - 90)
            draw.line([self.center, self.center, self.center + 235 * math.cos(angle), self.center + 235 * math.sin(angle)], fill=self.color_line, width=4)
        
        if is_taken:
            mask = Image.new("L", (self.size, self.size), 255)
            mask_draw = ImageDraw.Draw(mask)
            mask_draw.pieslice([15, 15, 485, 485], -90, -90 + angle_step, fill=0)
            img.putalpha(mask)
        return img

    def get_slice_on_plate(self, slices):
        img = Image.new("RGBA", (self.size, self.size), (0,0,0,0))
        draw = ImageDraw.Draw(img)
        # Beyaz Tabak
        draw.ellipse([30, 30, 470, 470], fill="#F5F5F5", outline="#CCCCCC", width=5)
        
        pizza_img = Image.new("RGBA", (self.size, self.size), (0,0,0,0))
        p_draw = ImageDraw.Draw(pizza_img)
        self._draw_base(p_draw)
        
        mask = Image.new("L", (self.size, self.size), 0)
        mask_draw = ImageDraw.Draw(mask)
        angle_step = 360 / slices
        mask_draw.pieslice([40, 40, 460, 460], -90, -90 + angle_step, fill=255)
        
        pizza_img.putalpha(mask)
        img.alpha_composite(pizza_img)
        return img

# --- DURUM YÖNETİMİ ---
if 'sl_a' not in st.session_state: st.session_state.sl_a = 5
if 'sl_b' not in st.session_state: st.session_state.sl_b = 7
if 'tk_a' not in st.session_state: st.session_state.tk_a = False
if 'tk_b' not in st.session_state: st.session_state.tk_b = False

engine = PizzaEngine()

st.title("🍕 Pizza Dilimi Karşılaştırma Laboratuvarı 🍕")

# --- KONTROL ALANI ---
st.markdown("<div class='input-box'>", unsafe_allow_html=True)
c1, c2, c3 = st.columns([2, 2, 1])
with c1:
    st.session_state.sl_a = st.number_input("Soldaki Pizza Kaç Dilim Olsun?", 2, 20, st.session_state.sl_a)
with c2:
    st.session_state.sl_b = st.number_input("Sağdaki Pizza Kaç Dilim Olsun?", 2, 20, st.session_state.sl_b)
with c3:
    st.write("Sıfırla")
    if st.button("🔄 TEMİZLE"):
        st.session_state.tk_a = False
        st.session_state.tk_b = False
        st.rerun()
st.markdown("</div>", unsafe_allow_html=True)

# --- ÜST PANEL ---
col1, col2 = st.columns(2)

with col1:
    st.subheader(f"{st.session_state.sl_a} Parçalı Pizza")
    st.image(engine.get_pizza_view(st.session_state.sl_a, st.session_state.tk_a), use_container_width=True)
    if st.button(f"BURADAN DİLİM AL", key="b_a"):
        st.session_state.tk_a = True
        st.rerun()

with col2:
    st.subheader(f"{st.session_state.sl_b} Parçalı Pizza")
    st.image(engine.get_pizza_view(st.session_state.sl_b, st.session_state.tk_b), use_container_width=True)
    if st.button(f"ŞURADAN DİLİM AL", key="b_b"):
        st.session_state.tk_b = True
        st.rerun()

# --- ALT PANEL: TABAKLAR ---
if st.session_state.tk_a or st.session_state.tk_b:
    st.markdown("---")
    st.markdown("## 🍽️ Senin Tabakların")
    
    t_col1, t_col2 = st.columns(2)
    
    with t_col1:
        if st.session_state.tk_a:
            st.image(engine.get_slice_on_plate(st.session_state.sl_a), use_container_width=True)
            st.markdown(f'<p class="kesir-miktari">1 / {st.session_state.sl_a}</p>', unsafe_allow_html=True)
            if st.session_state.sl_a <= 5:
                st.markdown("### 😋 KARNIN DOYAR!")
            else:
                st.markdown("### 🧐 BİRAZ KÜÇÜK...")
        else:
            st.write("Henüz dilim almadın.")

    with t_col2:
        if st.session_state.tk_b:
            st.image(engine.get_slice_on_plate(st.session_state.sl_b), use_container_width=True)
            st.markdown(f'<p class="kesir-miktari">1 / {st.session_state.sl_b}</p>', unsafe_allow_html=True)
            if st.session_state.sl_b <= 5:
                st.markdown("### 😋 KARNIN DOYAR!")
            else:
                st.markdown("### 🧐 BİRAZ KÜÇÜK...")
        else:
            st.write("Henüz dilim almadın.")

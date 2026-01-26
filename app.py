import streamlit as st
from PIL import Image, ImageDraw
import math

# --- SAYFA AYARLARI ---
st.set_page_config(page_title="Pizza Karşılaştırma", layout="wide", initial_sidebar_state="expanded")

# --- TASARIM (CSS) ---
st.markdown("""
    <style>
    /* Arka Plan */
    .stApp { background-color: #5D4037; } 
    
    /* Başlıklar ve Genel Metinler */
    h1, h2, h3 { 
        color: #FFD700 !important; 
        font-family: 'Arial Black', sans-serif; 
        text-align: center;
        margin-bottom: 5px !important;
        padding-bottom: 5px !important;
    }
    p, span, div, label { 
        color: #FFFFFF !important; 
        font-family: 'Comic Sans MS', sans-serif; 
        text-align: center;
        font-weight: bold;
    }

    /* SİYAH BUTON YAZISI VE KOMPAKT TASARIM */
    div.stButton > button {
        background-color: #FFD700 !important;
        border: 3px solid #2E1A12 !important;
        border-radius: 10px !important;
        height: 50px !important; /* Yükseklik azaltıldı */
        width: 100% !important;
        margin-top: 10px !important;
    }
    div.stButton > button * {
        color: #000000 !important; 
        font-weight: 900 !important;
        font-size: 16px !important;
    }
    
    /* Yan Menü (Sidebar) Ayarları */
    [data-testid="stSidebar"] {
        background-color: #3E2723 !important;
    }
    
    /* Tabak Alanı (Kompakt) */
    .tabak-paneli {
        background-color: rgba(255,255,255,0.05);
        border: 2px dashed #FFD700;
        border-radius: 15px;
        padding: 10px;
        margin-top: 10px;
    }
    </style>
    """, unsafe_allow_html=True)

class PizzaEngine:
    def __init__(self):
        self.size = 400 # Boyut biraz küçültüldü (Tek ekrana sığması için)
        self.center = self.size // 2
        self.color_crust = "#D38E45"   
        self.color_cheese = "#FFCA28"  
        self.color_pep = "#C62828"     
        self.color_line = "#6D4C41"

    def _draw_base(self, draw):
        draw.ellipse([15, 15, self.size-15, self.size-15], fill=self.color_crust)
        draw.ellipse([45, 45, self.size-45, self.size-45], fill=self.color_cheese)
        pep_r = 18
        for r, count in [(70, 6), (135, 10)]:
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
            draw.line([self.center, self.center, self.center + (self.size//2 - 15) * math.cos(angle), self.center + (self.size//2 - 15) * math.sin(angle)], fill=self.color_line, width=3)
        if is_taken:
            mask = Image.new("L", (self.size, self.size), 255)
            mask_draw = ImageDraw.Draw(mask)
            mask_draw.pieslice([10, 10, self.size-10, self.size-10], -90, -90 + angle_step, fill=0)
            img.putalpha(mask)
        return img

    def get_slice_on_plate(self, slices):
        img = Image.new("RGBA", (self.size, self.size), (0,0,0,0))
        draw = ImageDraw.Draw(img)
        draw.ellipse([25, 25, self.size-25, self.size-25], fill="#F5F5F5", outline="#CCCCCC", width=4) # Beyaz Tabak
        
        pizza_img = Image.new("RGBA", (self.size, self.size), (0,0,0,0))
        p_draw = ImageDraw.Draw(pizza_img)
        self._draw_base(p_draw)
        mask = Image.new("L", (self.size, self.size), 0)
        mask_draw = ImageDraw.Draw(mask)
        angle_step = 360 / slices
        mask_draw.pieslice([35, 35, self.size-35, self.size-35], -90, -90 + angle_step, fill=255)
        pizza_img.putalpha(mask)
        img.alpha_composite(pizza_img)
        return img

# --- DURUM (STATE) ---
if 'sl_a' not in st.session_state: st.session_state.sl_a = 4
if 'sl_b' not in st.session_state: st.session_state.sl_b = 12
if 'tk_a' not in st.session_state: st.session_state.tk_a = False
if 'tk_b' not in st.session_state: st.session_state.tk_b = False
if 'show_res' not in st.session_state: st.session_state.show_res = False

engine = PizzaEngine()

# --- YAN MENÜ (SIDEBAR) ---
with st.sidebar:
    st.header("⚙️ Ayarlar")
    st.session_state.sl_a = st.number_input("Sol Pizza Dilimi:", 2, 20, st.session_state.sl_a)
    st.session_state.sl_b = st.number_input("Sağ Pizza Dilimi:", 2, 20, st.session_state.sl_b)
    st.markdown("---")
    if st.button("🔄 SIFIRLA VE TEMİZLE"):
        st.session_state.tk_a = st.session_state.tk_b = st.session_state.show_res = False
        st.rerun()
    st.markdown("---")
    if st.button("🧐 DOYACAK MIYIM? (KONTROL ET)"):
        st.session_state.show_res = True
        st.rerun()

# --- ANA EKRAN ---
st.title("🍕 Hangisi Daha Çok Doyurur? 🍕")

main_col1, main_col2 = st.columns(2)

with main_col1:
    st.subheader(f"{st.session_state.sl_a} Parçalı Pizza")
    st.image(engine.get_pizza_view(st.session_state.sl_a, st.session_state.tk_a), use_container_width=True)
    if st.button("DİLİM AL 🍴", key="b_a"):
        st.session_state.tk_a = True
        st.session_state.show_res = False
        st.rerun()
    
    # Tabak hemen altta (Tek ekranda kalması için kompakt)
    if st.session_state.tk_a:
        st.markdown("<div class='tabak-paneli'>", unsafe_allow_html=True)
        st.image(engine.get_slice_on_plate(st.session_state.sl_a), width=200) # Sabit genişlik
        st.markdown(f"**Dilim: 1 / {st.session_state.sl_a}**")
        if st.session_state.show_res:
            if st.session_state.sl_a < st.session_state.sl_b:
                st.success("😋 Daha büyük, daha fazla doyarım!")
            elif st.session_state.sl_a > st.session_state.sl_b:
                st.warning("🧐 Daha küçük, az doyarım.")
        st.markdown("</div>", unsafe_allow_html=True)

with main_col2:
    st.subheader(f"{st.session_state.sl_b} Parçalı Pizza")
    st.image(engine.get_pizza_view(st.session_state.sl_b, st.session_state.tk_b), use_container_width=True)
    if st.button("DİLİM AL 🍴", key="b_b"):
        st.session_state.tk_b = True
        st.session_state.show_res = False
        st.rerun()
    
    if st.session_state.tk_b:
        st.markdown("<div class='tabak-paneli'>", unsafe_allow_html=True)
        st.image(engine.get_slice_on_plate(st.session_state.sl_b), width=200)
        st.markdown(f"**Dilim: 1 / {st.session_state.sl_b}**")
        if st.session_state.show_res:
            if st.session_state.sl_b < st.session_state.sl_a:
                st.success("😋 Daha büyük, daha fazla doyarım!")
            elif st.session_state.sl_b > st.session_state.sl_a:
                st.warning("🧐 Daha küçük, az doyarım.")
        st.markdown("</div>", unsafe_allow_html=True)

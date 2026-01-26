import streamlit as st
from PIL import Image, ImageDraw
import math

# --- SAYFA AYARLARI ---
st.set_page_config(page_title="Hangisi Doyurur?", layout="wide")

# --- TASARIM (CSS) - BUTON YAZILARINI SİYAH YAPMA GARANTİSİ ---
st.markdown("""
    <style>
    /* Arka Plan */
    .stApp { background-color: #5D4037; } 
    
    /* Başlıklar */
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

    /* SARI BUTON İÇİNDEKİ YAZIYI SİYAHA ZORLA (ZORUNLU AYAR) */
    div.stButton > button {
        background-color: #FFD700 !important;
        border: 4px solid #2E1A12 !important;
        border-radius: 15px !important;
        height: 75px !important;
        width: 100% !important;
        box-shadow: 0px 6px 15px rgba(0,0,0,0.5);
    }

    /* Buton içindeki tüm yazıları (p, span, div) simsiyah yap */
    div.stButton > button * {
        color: #000000 !important; 
        font-weight: 900 !important;
        font-size: 20px !important;
    }
    
    div.stButton > button:hover {
        background-color: #FFA500 !important;
    }

    /* Tabak Paneli */
    .tabak-paneli {
        background-color: rgba(0,0,0,0.3);
        border: 4px dashed #FFD700;
        border-radius: 25px;
        padding: 30px;
        margin-top: 20px;
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

    def _draw_base(self, draw):
        draw.ellipse([20, 20, 480, 480], fill=self.color_crust)
        draw.ellipse([55, 55, 445, 445], fill=self.color_cheese)
        pep_r = 24
        for r, count in [(90, 6), (170, 10)]:
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
            # HATA BURADAYDI: Hem cos (X) hem sin (Y) koordinatlarını ekledik
            draw.line([
                self.center, self.center, 
                self.center + 230 * math.cos(angle), 
                self.center + 230 * math.sin(angle)
            ], fill=self.color_line, width=5)
        
        if is_taken:
            mask = Image.new("L", (self.size, self.size), 255)
            mask_draw = ImageDraw.Draw(mask)
            mask_draw.pieslice([15, 15, 485, 485], -90, -90 + angle_step, fill=0)
            img.putalpha(mask)
        return img

    def get_slice_only(self, slices):
        img = Image.new("RGBA", (self.size, self.size), (0,0,0,0))
        draw = ImageDraw.Draw(img)
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

# --- DURUM (STATE) YÖNETİMİ ---
if 'sl_a' not in st.session_state: st.session_state.sl_a = 4
if 'sl_b' not in st.session_state: st.session_state.sl_b = 12
if 'tk_a' not in st.session_state: st.session_state.tk_a = False
if 'tk_b' not in st.session_state: st.session_state.tk_b = False
if 'show_res' not in st.session_state: st.session_state.show_res = False

engine = PizzaEngine()

st.title("🍕 Karnını Hangisi Daha Çok Doyurur? 🍕")

# --- ÜST PANEL: AYARLAR ---
c_col1, c_col2, c_col3 = st.columns([2, 2, 1])
with c_col1:
    st.session_state.sl_a = st.number_input("Sol Pizza Dilim Sayısı:", 2, 20, st.session_state.sl_a)
with c_col2:
    st.session_state.sl_b = st.number_input("Sağ Pizza Dilim Sayısı:", 2, 20, st.session_state.sl_b)
with c_col3:
    st.write("Sıfırla")
    if st.button("🔄 SIFIRLA"):
        st.session_state.tk_a = st.session_state.tk_b = st.session_state.show_res = False
        st.rerun()

# --- ORTA PANEL: PİZZALAR ---
col1, col2 = st.columns(2)
with col1:
    st.subheader(f"{st.session_state.sl_a} Parçalı Pizza")
    st.image(engine.get_pizza_view(st.session_state.sl_a, st.session_state.tk_a), use_container_width=True)
    if st.button("BU PİZZADAN DİLİM AL", key="btn_a"):
        st.session_state.tk_a, st.session_state.show_res = True, False
        st.rerun()

with col2:
    st.subheader(f"{st.session_state.sl_b} Parçalı Pizza")
    st.image(engine.get_pizza_view(st.session_state.sl_b, st.session_state.tk_b), use_container_width=True)
    if st.button("ŞURADAN DİLİM AL", key="btn_b"):
        st.session_state.tk_b, st.session_state.show_res = True, False
        st.rerun()

# --- ALT PANEL: TABAKLAR ---
if st.session_state.tk_a or st.session_state.tk_b:
    st.markdown("<div class='tabak-paneli'>", unsafe_allow_html=True)
    st.markdown("## 🍽️ Senin Tabakların")
    res_col1, res_col2 = st.columns(2)
    
    with res_col1:
        if st.session_state.tk_a:
            st.image(engine.get_slice_only(st.session_state.sl_a), use_container_width=True)
            st.markdown(f"### Dilim Miktarı: 1 / {st.session_state.sl_a}")
            if st.session_state.show_res:
                if st.session_state.sl_a < st.session_state.sl_b:
                    st.success("😋 Bu dilim daha büyük, daha fazla doyarım!")
                elif st.session_state.sl_a > st.session_state.sl_b:
                    st.warning("🧐 Bu dilim daha küçük, daha az doyarım.")
                else:
                    st.info("🤔 İki dilim de aynı boyutta!")
        else:
            st.info("Sol tabak boş.")

    with res_col2:
        if st.session_state.tk_b:
            st.image(engine.get_slice_only(st.session_state.sl_b), use_container_width=True)
            st.markdown(f"### Dilim Miktarı: 1 / {st.session_state.sl_b}")
            if st.session_state.show_res:
                if st.session_state.sl_b < st.session_state.sl_a:
                    st.success("😋 Bu dilim daha büyük, daha fazla doyarım!")
                elif st.session_state.sl_b > st.session_state.sl_a:
                    st.warning("🧐 Bu dilim daha küçük, daha az doyarım.")
                else:
                    st.info("🤔 İki dilim de aynı boyutta!")
        else:
            st.info("Sağ tabak boş.")
    st.markdown("</div>", unsafe_allow_html=True)

    # --- EN ALT PANEL: KONTROL BUTONU ---
    st.markdown("---")
    _, mid_btn, _ = st.columns([1, 2, 1])
    with mid_btn:
        if st.button("🧐 HADİ KONTROL EDELİM! DOYACAK MIYIM?"):
            st.session_state.show_res = True
            st.rerun()

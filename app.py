import streamlit as st
from PIL import Image, ImageDraw
import math

# --- SAYFA AYARLARI ---
st.set_page_config(page_title="Pizza Dilimi Karşılaştırma", layout="wide")

# --- TASARIM VE OKUNABİLİRLİK (CSS) ---
st.markdown("""
    <style>
    /* Arka Plan: Koyu Kahve */
    .stApp { background-color: #5D4037; } 
    
    /* Başlıklar: Altın Sarısı ve Gölgeli */
    h1, h2, h3 { 
        color: #FFD700 !important; 
        font-family: 'Arial Black', sans-serif; 
        text-align: center;
        text-shadow: 2px 2px 5px #000000;
    }
    
    /* Bilgi Metinleri: Beyaz ve Kalın */
    p, span, label { 
        color: #FFFFFF !important; 
        font-family: 'Comic Sans MS', sans-serif; 
        font-weight: bold !important;
        font-size: 18px !important;
        text-align: center;
    }

    /* BUTONLAR: TAM SİYAH YAZI VE SARI ARKA PLAN (MAKSİMUM OKUNABİLİRLİK) */
    .stButton button {
        background-color: #FFD700 !important;
        color: #000000 !important; /* Yazı Rengi Siyah */
        font-weight: 900 !important; /* Çok Kalın */
        font-size: 22px !important;
        border-radius: 12px !important;
        border: 4px solid #2E1A12 !important;
        height: 70px !important;
        width: 100% !important;
        box-shadow: 0px 5px 15px rgba(0,0,0,0.4);
    }
    
    .stButton button:hover {
        background-color: #FFA500 !important;
        color: #000000 !important;
        border-color: #FFFFFF !important;
    }

    /* Tabak Bölgesi Paneli */
    .tabak-paneli {
        background-color: rgba(0,0,0,0.3);
        border: 3px dashed #FFD700;
        border-radius: 20px;
        padding: 25px;
        margin-top: 30px;
    }
    </style>
    """, unsafe_allow_html=True)

class PizzaEngine:
    def __init__(self):
        self.size = 500
        self.center = self.size // 2
        self.color_crust = "#D38E45"   # Hamur
        self.color_cheese = "#FFCA28"  # Peynir
        self.color_pep = "#C62828"     # Biberoni
        self.color_line = "#6D4C41"    # Kesim çizgisi

    def _draw_base(self, draw):
        # Pizza tabanı
        draw.ellipse([20, 20, 480, 480], fill=self.color_crust)
        draw.ellipse([55, 55, 445, 445], fill=self.color_cheese)
        # Biberoniler (Sabit konum)
        pep_r = 22
        for r, count in [(80, 6), (160, 10)]:
            for i in range(count):
                angle = math.radians(i * (360/count))
                px = self.center + r * math.cos(angle) - pep_r
                py = self.center + r * math.sin(angle) - pep_r
                draw.ellipse([px, py, px+pep_r*2, py+pep_r*2], fill=self.color_pep)

    def get_pizza_view(self, slices, is_taken=False):
        """Üstteki pizzayı çizer. Dilim alınmışsa o parça boş kalır."""
        img = Image.new("RGBA", (self.size, self.size), (0,0,0,0))
        draw = ImageDraw.Draw(img)
        self._draw_base(draw)
        
        angle_step = 360 / slices
        # Kesim çizgileri
        for i in range(slices):
            angle = math.radians(i * angle_step - 90)
            draw.line([self.center, self.center, self.center + 230 * math.cos(angle), self.center + 230 * math.sin(angle)], fill=self.color_line, width=4)
        
        if is_taken:
            # Maske ile bir dilimi "kesip at"
            mask = Image.new("L", (self.size, self.size), 255)
            mask_draw = ImageDraw.Draw(mask)
            mask_draw.pieslice([15, 15, 485, 485], -90, -90 + angle_step, fill=0)
            img.putalpha(mask)
            
        return img

    def get_slice_on_plate(self, slices):
        """Sadece alınan dilimi tuvalin kendi boyutunda çizer (Boyut farkı net görünür)"""
        img = Image.new("RGBA", (self.size, self.size), (0,0,0,0))
        draw = ImageDraw.Draw(img)
        self._draw_base(draw)
        
        mask = Image.new("L", (self.size, self.size), 0)
        mask_draw = ImageDraw.Draw(mask)
        angle_step = 360 / slices
        mask_draw.pieslice([20, 20, 480, 480], -90, -90 + angle_step, fill=255)
        
        img.putalpha(mask)
        return img

# --- DURUM TAKİBİ ---
if 'taken_4' not in st.session_state: st.session_state.taken_4 = False
if 'taken_12' not in st.session_state: st.session_state.taken_12 = False

engine = PizzaEngine()

st.title("🍕 Hangi Dilim Daha Büyük? 🍕")
st.write("Aşağıdaki pizzalara tıkla ve tabakları doldur!")

# --- ÜST PANEL: PİZZALAR ---
col1, col2 = st.columns(2)

with col1:
    st.subheader("4 Dilimli Pizza")
    st.image(engine.get_pizza_view(4, st.session_state.taken_4), use_container_width=True)
    if st.button("Bu Pizzadan Bir Dilim Al"):
        st.session_state.taken_4 = True

with col2:
    st.subheader("12 Dilimli Pizza")
    st.image(engine.get_pizza_view(12, st.session_state.taken_12), use_container_width=True)
    if st.button("Şu Pizzadan Bir Dilim Al"):
        st.session_state.taken_12 = True

# --- ALT PANEL: TABAK VE KARŞILAŞTIRMA ---
if st.session_state.taken_4 or st.session_state.taken_12:
    st.markdown("<div class='tabak-paneli'>", unsafe_allow_html=True)
    st.markdown("## 🍽️ Senin Tabağın")
    
    res_col1, res_col2 = st.columns(2)
    
    with res_col1:
        if st.session_state.taken_4:
            st.image(engine.get_slice_on_plate(4), use_container_width=True)
            st.markdown("### KOCAMAN DİLİM")
            st.write("Pizzayı sadece 4'e böldük, bu yüzden parçalar çok büyük!")
        else:
            st.write("Daha buradan dilim almadın.")

    with res_col2:
        if st.session_state.taken_12:
            st.image(engine.get_slice_on_plate(12), use_container_width=True)
            st.markdown("### KÜÇÜCÜK DİLİM")
            st.write("Pizzayı 12 kişiye böldüğümüz için sana minicik bir parça kaldı.")
        else:
            st.write("Daha buradan dilim almadın.")
            
    st.markdown("</div>", unsafe_allow_html=True)

    # Reset Butonu
    st.markdown("<br>", unsafe_allow_html=True)
    if st.button("Tabağı Boşalt ve Yeniden Başla 🔄"):
        st.session_state.taken_4 = False
        st.session_state.taken_12 = False
        st.rerun()

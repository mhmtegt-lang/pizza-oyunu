import streamlit as st
from PIL import Image, ImageDraw, ImageFont
import math

# --- SAYFA AYARLARI ---
st.set_page_config(page_title="Pizza Oyunu", layout="wide")

# --- TASARIM (CSS) ---
st.markdown("""
    <style>
    /* Arka Plan */
    .stApp { background-color: #5D4037; } 
    
    /* Yazı Stilleri */
    h1, h2, h3, p, div { 
        color: #FFECB3 !important; 
        font-family: 'Comic Sans MS', 'Arial', sans-serif; 
        text-align: center; 
    }
    
    /* Kesir Gösterimi (Özel Stil) */
    .fraction-text {
        font-size: 60px;
        font-weight: bold;
        color: #FFD700; /* Altın Sarısı */
        text-shadow: 2px 2px 4px #000000;
    }
    
    /* Buton Tasarımı - OKUNAKLI */
    .stButton button {
        background-color: #FFD700 !important;
        color: #3E2723 !important; /* Koyu Kahve Yazı */
        font-weight: 900 !important;
        font-size: 24px !important;
        border-radius: 15px !important;
        border: 4px solid #3E2723 !important;
        padding: 10px 24px !important;
        width: 100%;
        transition: transform 0.2s;
    }
    .stButton button:hover {
        background-color: #FFCA28 !important;
        transform: scale(1.05);
        color: #000000 !important;
    }
    
    /* Konteynerleri belirginleştir */
    [data-testid="column"] {
        background-color: rgba(0,0,0,0.2);
        border-radius: 20px;
        padding: 20px;
        margin: 10px;
    }
    </style>
    """, unsafe_allow_html=True)

class ProceduralPizza:
    """Pizza ve Dilim Çizim Motoru"""
    def __init__(self):
        self.width = 500
        self.height = 500
        self.color_crust = "#D38E45"   
        self.color_cheese = "#FFCA28"  
        self.color_pep = "#C62828"     
        self.color_line = "#8D6E63"    

    def _draw_base(self, draw):
        # Hamur ve Peynir
        margin = 20
        draw.ellipse([margin, margin, self.width-margin, self.height-margin], fill=self.color_crust)
        crust_width = 35
        draw.ellipse([margin+crust_width, margin+crust_width, 
                      self.width-margin-crust_width, self.height-margin-crust_width], 
                     fill=self.color_cheese)
        
        # Biberoniler
        center = self.width // 2
        pep_r = 22
        # İç halka
        for angle in range(0, 360, 60):
            rad = math.radians(angle)
            px = center + 80 * math.cos(rad) - pep_r
            py = center + 80 * math.sin(rad) - pep_r
            draw.ellipse([px, py, px+pep_r*2, py+pep_r*2], fill=self.color_pep)
        # Dış halka
        for angle in range(30, 390, 45):
            rad = math.radians(angle)
            px = center + 150 * math.cos(rad) - pep_r
            py = center + 150 * math.sin(rad) - pep_r
            draw.ellipse([px, py, px+pep_r*2, py+pep_r*2], fill=self.color_pep)

    def get_full_pizza_with_lines(self, slices):
        """Bütün pizzayı kesim çizgileriyle gösterir"""
        img = Image.new("RGBA", (self.width, self.height), (0,0,0,0))
        draw = ImageDraw.Draw(img)
        self._draw_base(draw)
        
        center = self.width // 2
        radius = (self.width // 2) - 20
        angle_step = 360 / slices
        
        for i in range(slices):
            angle = math.radians(i * angle_step - 90)
            end_x = center + radius * math.cos(angle)
            end_y = center + radius * math.sin(angle)
            draw.line([center, center, end_x, end_y], fill=self.color_line, width=5)
            
        return img

    def get_single_slice(self, slices):
        """Sadece tek bir dilimi kesip çıkarır"""
        # Önce tam pizzayı çiz
        base = Image.new("RGBA", (self.width, self.height), (0,0,0,0))
        draw = ImageDraw.Draw(base)
        self._draw_base(draw)
        
        # Maske oluştur (Sadece dilim alanı beyaz olacak)
        mask = Image.new("L", (self.width, self.height), 0)
        mask_draw = ImageDraw.Draw(mask)
        
        angle_step = 360 / slices
        # Dilimi yukarı bakacak şekilde ayarla (-90 derece)
        mask_draw.pieslice([20, 20, self.width-20, self.height-20], -90, -90 + angle_step, fill=255)
        
        # Maskeyi uygula
        base.putalpha(mask)
        
        # Görseli kırp (Boş alanları at)
        bbox = base.getbbox()
        if bbox:
            return base.crop(bbox)
        return base

# --- UYGULAMA MANTIĞI ---

if 'mode' not in st.session_state:
    st.session_state.mode = 'select' # 'select' veya 'compare'

pizza_maker = ProceduralPizza()

st.title("🍕 Pizza Dilimleri: Hangisi Daha Çok Doyurur? 🍕")

# --- 1. AŞAMA: SEÇİM EKRANI ---
if st.session_state.mode == 'select':
    st.markdown("### Aşağıda iki farklı pizza var. İkisinden de tabağına birer dilim alıp karşılaştıralım!")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.header("4 Dilimli Pizza")
        st.image(pizza_maker.get_full_pizza_with_lines(4), use_container_width=True)
        st.markdown("**Dilimler büyük görünüyor...**")

    with col2:
        st.header("12 Dilimli Pizza")
        st.image(pizza_maker.get_full_pizza_with_lines(12), use_container_width=True)
        st.markdown("**Dilimler daha ince görünüyor...**")

    st.markdown("---")
    # Ortaya büyük bir buton
    _, mid_col, _ = st.columns([1, 2, 1])
    with mid_col:
        if st.button("🍽️ İKİSİNDEN DE BİRER DİLİM AL VE KARŞILAŞTIR! 🍽️"):
            st.session_state.mode = 'compare'
            st.rerun()

# --- 2. AŞAMA: KARŞILAŞTIRMA EKRANI ---
elif st.session_state.mode == 'compare':
    st.markdown("## İşte Tabağındaki Dilimler!")
    st.write("Bakalım hangisi seni daha çok doyuracak?")
    
    col_a, col_b = st.columns(2)
    
    # 1/4 Dilim Sonucu
    with col_a:
        st.success("DOYURUCU SEÇİM! 😋")
        # Dilim Görseli
        slice_img_4 = pizza_maker.get_single_slice(4)
        # Görseli ortalamak için st.image kullanımı
        st.image(slice_img_4, width=300) 
        
        # Matematiksel Kesir
        st.markdown('<p class="fraction-text">1/4</p>', unsafe_allow_html=True)
        
        # Yorum
        st.markdown("""
        ### Kocaman!
        Bu dilimle **karnın tıka basa doyar.** Çünkü pizzayı sadece 4 kişiye böldük, sana büyük parça düştü.
        """)

    # 1/12 Dilim Sonucu
    with col_b:
        st.warning("SADECE TARDIMLIK... 🧐")
        # Dilim Görseli
        slice_img_12 = pizza_maker.get_single_slice(12)
        st.image(slice_img_12, width=300)
        
        # Matematiksel Kesir
        st.markdown('<p class="fraction-text">1/12</p>', unsafe_allow_html=True)
        
        # Yorum
        st.markdown("""
        ### Minicik...
        Bu dilim **dişinin kovuğuna bile yetmez!**
        Çünkü pizzayı 12 kişiye böldük, sana çok ince bir parça kaldı.
        """)

    st.markdown("---")
    
    # Sıfırlama Butonu
    _, reset_col, _ = st.columns([1, 2, 1])
    with reset_col:
        if st.button("🔄 Tekrar Oyna"):
            st.session_state.mode = 'select'
            st.rerun()

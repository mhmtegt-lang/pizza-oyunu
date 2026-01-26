import streamlit as st
from PIL import Image, ImageDraw
import math

# --- SAYFA AYARLARI ---
st.set_page_config(page_title="Pizza Oyunu", layout="wide")

# --- TASARIM GÜNCELLEMESİ (OKUNABİLİR BUTONLAR) ---
st.markdown("""
    <style>
    /* Arka plan rengi */
    .stApp { background-color: #5D4037; } 
    
    /* Başlıklar ve yazılar */
    h1, h2, h3, p { 
        color: #FFECB3 !important; 
        font-family: 'Comic Sans MS', sans-serif; 
        text-align: center; 
    }
    
    /* --- BUTON TASARIMI (BURASI DEĞİŞTİ) --- */
    .stButton button {
        background-color: #FFD700 !important; /* Parlak Altın Sarısı */
        color: #3E2723 !important;            /* Koyu Kahve Yazı (Neredeyse Siyah) */
        font-weight: 900 !important;          /* Çok Kalın Yazı */
        font-size: 24px !important;           /* Büyük Punto */
        border-radius: 12px !important;
        border: 4px solid #3E2723 !important; /* Koyu Çerçeve */
        padding: 15px 20px !important;
        width: 100%;
        transition: all 0.3s ease;
    }
    
    /* Mouse üzerine gelince (Hover) */
    .stButton button:hover {
        background-color: #FF6F00 !important; /* Turuncuya dönsün */
        color: #FFFFFF !important;            /* Yazı beyaz olsun */
        transform: scale(1.05);               /* Hafif büyüsün */
        border-color: #FFFFFF !important;
    }
    
    /* Buton içindeki tüm elementleri (p, span) zorla boya */
    .stButton button p, .stButton button span {
        color: inherit !important;
    }
    </style>
    """, unsafe_allow_html=True)

class ProceduralPizza:
    """
    Vektörel tarzda pizza üreten motor.
    """
    def __init__(self):
        self.width = 600
        self.height = 600
        # Renk Paleti (Referans görsele uygun)
        self.color_crust = "#D38E45"   # Kızarmış kenar
        self.color_cheese = "#FFCA28"  # Erimiş peynir sarısı
        self.color_pep = "#C62828"     # Biberoni kırmızısı
        self.color_line = "#8D6E63"    # Kesim çizgileri

    def generate_base_pizza(self):
        img = Image.new("RGBA", (self.width, self.height), (0,0,0,0))
        draw = ImageDraw.Draw(img)
        
        # 1. Hamur
        margin = 20
        draw.ellipse([margin, margin, self.width-margin, self.height-margin], fill=self.color_crust)
        
        # 2. Peynir
        crust_width = 40
        draw.ellipse([margin+crust_width, margin+crust_width, 
                      self.width-margin-crust_width, self.height-margin-crust_width], 
                     fill=self.color_cheese)
        
        # 3. Biberoniler (Sabit konumlar)
        center_x, center_y = self.width // 2, self.height // 2
        pep_radius = 28 # Biraz büyüttük
        
        # İç çember
        for angle in range(0, 360, 60): 
            rad = math.radians(angle)
            dist = 100
            px = center_x + dist * math.cos(rad) - pep_radius
            py = center_y + dist * math.sin(rad) - pep_radius
            draw.ellipse([px, py, px+pep_radius*2, py+pep_radius*2], fill=self.color_pep)

        # Dış çember
        for angle in range(30, 390, 45): 
            rad = math.radians(angle)
            dist = 190
            px = center_x + dist * math.cos(rad) - pep_radius
            py = center_y + dist * math.sin(rad) - pep_radius
            draw.ellipse([px, py, px+pep_radius*2, py+pep_radius*2], fill=self.color_pep)
            
        return img

    def get_sliced_view(self, total_slices, is_taken=False):
        base = self.generate_base_pizza()
        draw = ImageDraw.Draw(base)
        
        center_x, center_y = self.width // 2, self.height // 2
        radius = (self.width // 2) - 20
        angle_step = 360 / total_slices
        
        # Kesim çizgileri
        if not is_taken:
            for i in range(total_slices):
                angle = math.radians(i * angle_step - 90)
                end_x = center_x + radius * math.cos(angle)
                end_y = center_y + radius * math.sin(angle)
                draw.line([center_x, center_y, end_x, end_y], fill=self.color_line, width=6)
            return base
        else:
            # Dilim alma işlemi
            mask = Image.new("L", (self.width, self.height), 255)
            mask_draw = ImageDraw.Draw(mask)
            
            start_angle = -90
            end_angle = start_angle + angle_step
            
            mask_draw.pieslice([20, 20, self.width-20, self.height-20], start_angle, end_angle, fill=0)
            base.putalpha(mask)
            return base

    def get_single_slice(self, total_slices):
        base = self.generate_base_pizza()
        mask = Image.new("L", (self.width, self.height), 0)
        mask_draw = ImageDraw.Draw(mask)
        
        angle_step = 360 / total_slices
        start_angle = -90
        end_angle = start_angle + angle_step
        
        mask_draw.pieslice([20, 20, self.width-20, self.height-20], start_angle, end_angle, fill=255)
        base.putalpha(mask)
        return base

# --- UYGULAMA AKIŞI ---

if 'durum' not in st.session_state:
    st.session_state.durum = 'giris'

pizza_maker = ProceduralPizza()

st.title("🍕 Pizza Dilimleri: Hangisi Daha Büyük? 🍕")

# --- GİRİŞ EKRANI ---
if st.session_state.durum == 'giris':
    st.markdown("### Aşağıdaki pizzalardan bir dilim seç!")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.header("1/4 Pizza")
        st.image(pizza_maker.get_sliced_view(4, is_taken=False), use_container_width=True)
        # Buton metnini büyüttük ve netleştirdik
        if st.button("Bu Dilimi Seç (1/4)", key="btn_1_4"):
            st.session_state.durum = 'sonuc_4'
            st.rerun()

    with col2:
        st.header("1/12 Pizza")
        st.image(pizza_maker.get_sliced_view(12, is_taken=False), use_container_width=True)
        # Buton metnini büyüttük ve netleştirdik
        if st.button("Bu Dilimi Seç (1/12)", key="btn_1_12"):
            st.session_state.durum = 'sonuc_12'
            st.rerun()

# --- SONUÇ: 1/4 ---
elif st.session_state.durum == 'sonuc_4':
    st.success("🎉 HARİKA SEÇİM! 🎉")
    
    col_a, col_b = st.columns(2)
    with col_a:
        st.write("Eksilen Parça:")
        st.image(pizza_maker.get_sliced_view(4, is_taken=True), use_container_width=True)
    with col_b:
        st.write("Senin Dilimin:")
        st.image(pizza_maker.get_single_slice(4), use_container_width=True)
        
    st.markdown("## 1/4 Dilim Kocaman! Doyurucu bir seçim. 😋")
    st.balloons()
    
    if st.button("TEKRAR OYNA 🔄", key="reset_4"):
        st.session_state.durum = 'giris'
        st.rerun()

# --- SONUÇ: 1/12 ---
elif st.session_state.durum == 'sonuc_12':
    st.warning("🧐 ÇOK KÜÇÜK...")
    
    col_a, col_b = st.columns(2)
    with col_a:
        st.write("Eksilen Parça:")
        st.image(pizza_maker.get_sliced_view(12, is_taken=True), use_container_width=True)
    with col_b:
        st.write("Senin Dilimin:")
        st.image(pizza_maker.get_single_slice(12), use_container_width=True)
        
    st.markdown("## 1/12 Dilim kürdan gibi ince! Hala aç olabilirsin. 😕")
    
    if st.button("TEKRAR DENE 🔄", key="reset_12"):
        st.session_state.durum = 'giris'
        st.rerun()

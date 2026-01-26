import streamlit as st
from PIL import Image, ImageDraw
import math

# --- SAYFA AYARLARI ---
st.set_page_config(page_title="Pizza Oyunu", layout="wide")

# Tasarım: Koyu kahverengi arka plan ve okunaklı butonlar
st.markdown("""
    <style>
    .stApp { background-color: #6D4C41; } /* Daha yumuşak koyu kahve */
    h1, h2, h3, p { color: #FFECB3 !important; font-family: 'Comic Sans MS', sans-serif; text-align: center; }
    
    /* Buton Tasarımı - NET VE OKUNAKLI */
    .stButton button {
        background-color: #FFD54F !important; /* Canlı Sarı */
        color: #3E2723 !important; /* Çok koyu kahve yazı */
        font-weight: 900 !important;
        font-size: 22px !important;
        border-radius: 15px !important;
        border: 4px solid #3E2723 !important;
        padding: 10px 24px !important;
        width: 100%;
    }
    .stButton button:hover {
        background-color: #FFCA28 !important;
        color: #000000 !important;
        transform: scale(1.02);
    }
    </style>
    """, unsafe_allow_html=True)

class ProceduralPizza:
    """
    Bu sınıf, internete ihtiyaç duymadan Python koduyla 
    senin istediğin tarzda 'Vektörel/Canlı' bir pizza çizer.
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
        # Boş şeffaf bir tuval oluştur
        img = Image.new("RGBA", (self.width, self.height), (0,0,0,0))
        draw = ImageDraw.Draw(img)
        
        # 1. Hamur (Kenar) çizimi
        margin = 20
        draw.ellipse([margin, margin, self.width-margin, self.height-margin], fill=self.color_crust)
        
        # 2. Peynir (İç kısım) çizimi
        crust_width = 40
        draw.ellipse([margin+crust_width, margin+crust_width, 
                      self.width-margin-crust_width, self.height-margin-crust_width], 
                     fill=self.color_cheese)
        
        # 3. Biberonileri (Salamları) ekle
        # Sabit koordinatlar kullanıyoruz ki her seferinde düzgün görünsün
        center_x, center_y = self.width // 2, self.height // 2
        pep_radius = 25
        
        # İç çemberdeki biberoniler
        for angle in range(0, 360, 60): # 6 tane içte
            rad = math.radians(angle)
            dist = 100
            px = center_x + dist * math.cos(rad) - pep_radius
            py = center_y + dist * math.sin(rad) - pep_radius
            draw.ellipse([px, py, px+pep_radius*2, py+pep_radius*2], fill=self.color_pep)

        # Dış çemberdeki biberoniler
        for angle in range(30, 390, 45): # 8 tane dışta
            rad = math.radians(angle)
            dist = 180
            px = center_x + dist * math.cos(rad) - pep_radius
            py = center_y + dist * math.sin(rad) - pep_radius
            draw.ellipse([px, py, px+pep_radius*2, py+pep_radius*2], fill=self.color_pep)
            
        return img

    def get_sliced_view(self, total_slices, is_taken=False):
        """
        Pizzayı dilimlenmiş şekilde gösterir veya bir dilimi alır.
        """
        base = self.generate_base_pizza()
        draw = ImageDraw.Draw(base)
        
        center_x, center_y = self.width // 2, self.height // 2
        radius = (self.width // 2) - 20 # Kenar payı düşülmüş
        
        angle_step = 360 / total_slices
        
        # 1. Kesim çizgilerini çiz (Herkes görsün diye)
        if not is_taken:
            for i in range(total_slices):
                angle = math.radians(i * angle_step - 90) # -90 yukarıdan başlamak için
                end_x = center_x + radius * math.cos(angle)
                end_y = center_y + radius * math.sin(angle)
                draw.line([center_x, center_y, end_x, end_y], fill=self.color_line, width=5)
            return base
            
        # 2. Eğer dilim alındıysa, o dilimi "Kesip Çıkar"
        else:
            # Maske yöntemiyle o dilimi şeffaf yapıyoruz
            mask = Image.new("L", (self.width, self.height), 255) # Beyaz (Görünür)
            mask_draw = ImageDraw.Draw(mask)
            
            # İlk dilimi (0. indeks, en üst sağ) siliyoruz
            start_angle = -90
            end_angle = start_angle + angle_step
            
            # Dilim şeklini siyaha boya (Görünmez yap)
            mask_draw.pieslice([20, 20, self.width-20, self.height-20], start_angle, end_angle, fill=0)
            
            # Maskeyi uygula
            base.putalpha(mask)
            return base

    def get_single_slice(self, total_slices):
        """Sadece tek bir dilimi döndürür (Sağdaki görsel için)"""
        base = self.generate_base_pizza()
        
        # Maske: Sadece dilim görünsün, gerisi yok olsun
        mask = Image.new("L", (self.width, self.height), 0) # Siyah (Görünmez)
        mask_draw = ImageDraw.Draw(mask)
        
        angle_step = 360 / total_slices
        start_angle = -90
        end_angle = start_angle + angle_step
        
        # Sadece dilim alanını beyaza boya (Görünür yap)
        mask_draw.pieslice([20, 20, self.width-20, self.height-20], start_angle, end_angle, fill=255)
        
        base.putalpha(mask)
        
        # Görseli biraz kırp ki boşluklar azalsın (Opsiyonel ama şık durur)
        return base

# --- UYGULAMA AKIŞI ---

if 'durum' not in st.session_state:
    st.session_state.durum = 'giris'

pizza_maker = ProceduralPizza()

st.title("🍕 Pizza Dilimleri: Hangisi Daha Büyük? 🍕")

# --- GİRİŞ EKRANI (SEÇİM) ---
if st.session_state.durum == 'giris':
    st.write("Aşağıdaki pizzalara bak. Sence hangisinden bir dilim alırsan karnın daha çok doyar?")
    st.write("Bir seçim yap ve gör!")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("1/4 Pizza (4 Parça)")
        # Pizzanın bütün ama çizilmiş hali
        img1 = pizza_maker.get_sliced_view(4, is_taken=False)
        st.image(img1, use_container_width=True)
        
        if st.button("Bu Dilimi Seç (1/4)", key="btn_1_4"):
            st.session_state.durum = 'sonuc_4'
            st.rerun()

    with col2:
        st.subheader("1/12 Pizza (12 Parça)")
        img2 = pizza_maker.get_sliced_view(12, is_taken=False)
        st.image(img2, use_container_width=True)
        
        if st.button("Bu Dilimi Seç (1/12)", key="btn_1_12"):
            st.session_state.durum = 'sonuc_12'
            st.rerun()

# --- SONUÇ EKRANI (4 DİLİMLİ SEÇİLDİYSE) ---
elif st.session_state.durum == 'sonuc_4':
    st.success("🎉 TEBRİKLER! DOĞRU SEÇİM! 🎉")
    
    col_a, col_b = st.columns(2)
    with col_a:
        st.write("Pizzadan kocaman bir parça eksildi:")
        # Eksik pizza
        st.image(pizza_maker.get_sliced_view(4, is_taken=True), use_container_width=True)
    with col_b:
        st.write("İşte senin aldığın dev dilim:")
        # Sadece dilim
        st.image(pizza_maker.get_single_slice(4), use_container_width=True)
        
    st.markdown("## 1/4 Dilim Kocaman Olduğu İçin Seni Doyurur! 😋")
    st.balloons()
    
    if st.button("Tekrar Oyna 🔄"):
        st.session_state.durum = 'giris'
        st.rerun()

# --- SONUÇ EKRANI (12 DİLİMLİ SEÇİLDİYSE) ---
elif st.session_state.durum == 'sonuc_12':
    st.warning("🧐 HMM... BİRAZ KÜÇÜK KALDI SANKİ?")
    
    col_a, col_b = st.columns(2)
    with col_a:
        st.write("Pizzadan neredeyse hiçbir şey eksilmedi:")
        # Eksik pizza
        st.image(pizza_maker.get_sliced_view(12, is_taken=True), use_container_width=True)
    with col_b:
        st.write("Senin aldığın dilim sadece bu kadar:")
        # Sadece dilim
        st.image(pizza_maker.get_single_slice(12), use_container_width=True)
        
    st.markdown("## 1/12 Dilim Çok İncedir, Seni Doyurmaz! 😕")
    
    if st.button("Tekrar Dene 🔄"):
        st.session_state.durum = 'giris'
        st.rerun()

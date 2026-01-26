import streamlit as st
from PIL import Image, ImageDraw
import requests
from io import BytesIO

# --- AYARLAR VE TASARIM ---
st.set_page_config(
    page_title="Gerçek Pizza Oyunu",
    page_icon="🍕",
    layout="centered"
)

# Tasarım: Koyu arka plan ve okunabilir butonlar
st.markdown(
    """
    <style>
    .stApp { background-color: #8B4513; }
    h1, h2, h3, p, span, div { 
        color: #FFD700 !important; 
        font-family: 'Comic Sans MS', sans-serif; 
    }
    /* Sarı buton üzerine koyu kahverengi yazı (Rahat Okunur) */
    .stButton button {
        background-color: #FFD700 !important;
        color: #5c2b0b !important;
        font-weight: 900 !important; /* Kalın yazı */
        border-radius: 12px;
        border: 3px solid #5c2b0b;
        font-size: 18px !important;
    }
    .stButton button:hover {
        background-color: #FFA500 !important;
        border-color: #8B4513;
        color: #fff !important;
    }
    </style>
    """,
    unsafe_allow_html=True
)

# --- İNTERNETTEN PİZZA GETİREN VE DİLİMLEYEN MOTOR ---
class InternetPizzaSlicer:
    def __init__(self):
        # Wikipedia'dan temiz, reklamsız, gerçek bir pizza fotoğrafı adresi
        self.url = "https://upload.wikimedia.org/wikipedia/commons/thumb/d/d3/Supreme_pizza.jpg/800px-Supreme_pizza.jpg"
        self.pizza_img = self.download_image()

    def download_image(self):
        """İnternetten resmi indirir ve hazırlar"""
        try:
            response = requests.get(self.url)
            img = Image.open(BytesIO(response.content)).convert("RGBA")
            # Resmi kare yap ve yeniden boyutlandır (Düzgün görünmesi için)
            img = img.resize((500, 500))
            
            # Kenarlarını yuvarlatalım (Tam daire pizza hissi için maskeleme)
            mask = Image.new("L", (500, 500), 0)
            draw = ImageDraw.Draw(mask)
            draw.ellipse((10, 10, 490, 490), fill=255)
            
            # Maskeyi uygula (Köşeleri temizle)
            output = Image.new("RGBA", (500, 500), (0, 0, 0, 0))
            output.paste(img, (0, 0), mask=mask)
            return output
            
        except Exception as e:
            st.error(f"Pizza yüklenirken sorun oldu: {e}")
            return Image.new('RGBA', (500, 500), color='gray')

    def get_sliced_pizza(self, total_slices, is_slice_taken=False):
        """
        Pizzayı belirtilen dilim sayısına göre böler ve görselleştirir.
        Eğer 'is_slice_taken' True ise, bir dilimi eksik çizer.
        """
        img = self.pizza_img.copy()
        draw = ImageDraw.Draw(img)
        
        center = (250, 250)
        radius = 250
        angle_per_slice = 360 / total_slices
        
        # 1. Dilim çizgilerini çiz (Daha net görmek için)
        if not is_slice_taken:
            for i in range(total_slices):
                end_angle = i * angle_per_slice - 90
                # Dereceyi radyana çevirme işini draw.line ile basitleştiriyoruz
                # Pillow'da pie slice kullanmak daha kolay:
                draw.pieslice([0, 0, 500, 500], start=end_angle, end=end_angle, fill=None, outline="white", width=3)

        # 2. Eğer dilim alındıysa, o kısmı "şeffaf" yap (Kesip at)
        if is_slice_taken:
            # İlk dilimi (0. indeks) kesip atıyoruz
            start_angle = -90
            end_angle = start_angle + angle_per_slice
            
            # Maske ile silme işlemi
            mask = Image.new("L", (500, 500), 255) # Beyaz (Görünür)
            mask_draw = ImageDraw.Draw(mask)
            
            # Silinecek dilimi siyaha boya
            mask_draw.pieslice([0, 0, 500, 500], start_angle, end_angle, fill=0)
            
            # Maskeyi uygula
            current_alpha = img.split()[-1]
            # İki maskeyi birleştir
            from PIL import ImageChops
            new_alpha = ImageChops.multiply(current_alpha, mask)
            img.putalpha(new_alpha)
            
        return img

# --- OYUN BAŞLIYOR ---
if 'secim' not in st.session_state:
    st.session_state.secim = None

# Pizzayı hazırla
@st.cache_resource # Resmi her seferinde indirmesin, hafızada tutsun
def get_slicer():
    return InternetPizzaSlicer()

slicer = get_slicer()

st.title("🍕 Hangisi Daha Büyük? 🍕")
st.write("Aşağıdaki pizzalara bak. Hangi dilim seni daha çok doyurur?")

col1, col2 = st.columns(2)

# --- SOL TARA (1/4) ---
with col1:
    st.header("1/4 Pizza")
    # Duruma göre resmi belirle
    dilim_alindi_mi = (st.session_state.secim == '1/4')
    resim_1 = slicer.get_sliced_pizza(4, is_slice_taken=dilim_alindi_mi)
    
    st.image(resim_1, use_column_width=True)
    
    if st.button("KOCAMAN Dilimi Al (1/4)", key="btn1"):
        st.session_state.secim = '1/4'
        st.rerun()

# --- SAĞ TARAF (1/12) ---
with col2:
    st.header("1/12 Pizza")
    # Duruma göre resmi belirle
    dilim_alindi_mi = (st.session_state.secim == '1/12')
    resim_2 = slicer.get_sliced_pizza(12, is_slice_taken=dilim_alindi_mi)
    
    st.image(resim_2, use_column_width=True)
    
    if st.button("KÜÇÜK Dilimi Al (1/12)", key="btn2"):
        st.session_state.secim = '1/12'
        st.rerun()

# --- SONUÇ BÖLÜMÜ ---
st.markdown("---")

if st.session_state.secim == '1/4':
    st.success("DOĞRU TERCİH! 😋")
    st.write("Bak! Pizzadan kocaman bir üçgen eksildi. Bu dilim seni tıka basa doyurur.")
    st.markdown("<h1 style='text-align: center;'>🍕 BÜYÜK DİLİM!</h1>", unsafe_allow_html=True)
    st.balloons()

elif st.session_state.secim == '1/12':
    st.warning("ÇOK KÜÇÜK... 😕")
    st.write("Pizzaya bak, eksilen parça o kadar ince ki neredeyse fark edilmiyor bile.")
    st.markdown("<h1 style='text-align: center;'>🤏 MİNİCİK...</h1>", unsafe_allow_html=True)

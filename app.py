import streamlit as st
import matplotlib.pyplot as plt
import numpy as np

# --- AYARLAR VE TASARIM ---
st.set_page_config(
    page_title="Pizza Oyunu",
    page_icon="🍕",
    layout="centered"
)

# Görsel stilini CSS ile ayarla (Sıcak renkler)
st.markdown(
    """
    <style>
    .stApp { background-color: #8B4513; }
    h1, h2, h3, p, span, div { 
        color: #FFD700 !important; 
        font-family: 'Comic Sans MS', sans-serif; 
    }
    .stButton button {
        background-color: #FFD700;
        color: #8B4513;
        font-weight: bold;
        border-radius: 12px;
        border: 2px solid #5c2b0b;
    }
    .stButton button:hover {
        background-color: #FFA500;
        color: white;
    }
    </style>
    """,
    unsafe_allow_html=True
)

# --- PİZZA ÇİZEN SINIF (Mantık Kısmı) ---
class PizzaVisualizer:
    def __init__(self):
        self.background_color = '#8B4513'
        self.pizza_base_color = '#EDBF85'
        self.edge_color = '#6D2E15'
        self.pepperoni_color = '#B22222'

    def draw_pizza(self, total_slices, slice_to_take=None):
        try:
            fig, ax = plt.subplots(figsize=(4, 4))
            fig.patch.set_facecolor(self.background_color)
            ax.set_facecolor(self.background_color)

            sizes = [1] * total_slices
            colors = [self.pizza_base_color if i % 2 == 0 else '#E6A86C' for i in range(total_slices)]
            
            # Seçilen dilimi ayırma (Explode)
            explode = [0] * total_slices
            if slice_to_take is not None and 0 <= slice_to_take < total_slices:
                explode[slice_to_take] = 0.15 

            wedges, _ = ax.pie(
                sizes, explode=explode, colors=colors, startangle=90,
                wedgeprops={'edgecolor': self.edge_color, 'linewidth': 2}
            )

            # Pepperoni (Salam) Çizimi
            for i, wedge in enumerate(wedges):
                if i == slice_to_take or i % 2 == 0: # Süsleme mantığı
                    center = wedge.center
                    theta = np.deg2rad((wedge.theta1 + wedge.theta2) / 2)
                    r = 0.6
                    # Patlayan dilim için koordinat kaydırma
                    off_x = explode[i] * np.cos(theta)
                    off_y = explode[i] * np.sin(theta)
                    pep_x = center[0] + r * np.cos(theta) + off_x
                    pep_y = center[1] + r * np.sin(theta) + off_y
                    
                    circle = plt.Circle((pep_x, pep_y), 0.08, color=self.pepperoni_color)
                    ax.add_patch(circle)

            ax.axis('equal')
            return fig
        except Exception:
            return plt.figure()

# --- OYUN EKRANI ---
st.title("🍕 Hangisi Daha Büyük? 🍕")
st.write("Aşağıdaki pizzalardan bir dilim al!")

if 'secilen' not in st.session_state:
    st.session_state.secilen = None

visualizer = PizzaVisualizer()
col1, col2 = st.columns(2)

# 1/4 Pizza
with col1:
    st.header("1/4 Pizza")
    tiklama_1_4 = 0 if st.session_state.secilen == '1/4' else None
    st.pyplot(visualizer.draw_pizza(4, tiklama_1_4), use_container_width=True)
    if st.button("Bu Dilimi Ye (1/4)", key="b1"):
        st.session_state.secilen = '1/4'
        st.rerun()

# 1/12 Pizza
with col2:
    st.header("1/12 Pizza")
    tiklama_1_12 = 0 if st.session_state.secilen == '1/12' else None
    st.pyplot(visualizer.draw_pizza(12, tiklama_1_12), use_container_width=True)
    if st.button("Bu Dilimi Ye (1/12)", key="b2"):
        st.session_state.secilen = '1/12'
        st.rerun()

# SONUÇ GÖSTERİMİ
st.markdown("---")
if st.session_state.secilen == '1/4':
    st.success("DOĞRU SEÇİM! 😋")
    st.write("4 parçaya bölünmüş pizzanın dilimi kocaman olur!")
    st.balloons()
elif st.session_state.secilen == '1/12':
    st.warning("HMM... BİRAZ KÜÇÜK? 🧐")
    st.write("12 parçaya bölünmüş pizza dilimi çok küçüktür, doyurmaz!")

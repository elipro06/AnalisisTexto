import streamlit as st
import pandas as pd
from textblob import TextBlob
import re
from googletrans import Translator

st.set_page_config(
    page_title="El Escrutador Literario",
    page_icon="📖",
    layout="wide"
)

st.markdown("""
    <style>
        body {
            background-color: #1B1F3B;
            color: #E0E7FF;
        }
        .main {
            background-color: #1B1F3B !important;
            color: #E0E7FF !important;
        }
        .stApp {
            font-family: 'Trebuchet MS', sans-serif;
        }
        h1, h2, h3 {
            color: #A5B4FC;
        }
        .recuadro {
            background-color: #2E3460;
            color: #E0E7FF;
            border-radius: 8px;
            padding: 1rem;
            margin-bottom: 1rem;
            border: 1px solid #64748B;
        }
        .stButton>button {
            background-color: #6366F1;
            color: white;
            font-weight: bold;
            border-radius: 0.5rem;
        }
        .stProgress > div > div > div > div {
            background-color: #818CF8;
        }
    </style>
""", unsafe_allow_html=True)

with st.sidebar:
    st.image("maquina.jpg", use_container_width=True)
    st.title("Modo de lectura")
    modo = st.selectbox(
        "¿Cómo deseas compartir tu manuscrito?",
        ["Escribir directamente", "Subir archivo"]
    )

def contar_palabras(texto):
    stop_words = set([...])
    palabras = re.findall(r'\b\w+\b', texto.lower())
    palabras_filtradas = [p for p in palabras if p not in stop_words and len(p) > 2]
    contador = {}
    for p in palabras_filtradas:
        contador[p] = contador.get(p, 0) + 1
    return dict(sorted(contador.items(), key=lambda x: x[1], reverse=True)), palabras_filtradas

translator = Translator()

def traducir_texto(texto):
    try:
        return translator.translate(texto, src='es', dest='en').text
    except Exception as e:
        st.error(f"Ocurrió un error al traducir: {e}")
        return texto

def procesar_texto(texto):
    texto_original = texto
    texto_ingles = traducir_texto(texto)
    blob = TextBlob(texto_ingles)
    sentimiento = blob.sentiment.polarity
    subjetividad = blob.sentiment.subjectivity
    frases_originales = [f.strip() for f in re.split(r'[.!?]+', texto_original) if f.strip()]
    frases_traducidas = [f.strip() for f in re.split(r'[.!?]+', texto_ingles) if f.strip()]
    frases_combinadas = [{"original": o, "traducido": t} for o, t in zip(frases_originales, frases_traducidas)]
    contador_palabras, palabras = contar_palabras(texto_ingles)
    return {
        "sentimiento": sentimiento,
        "subjetividad": subjetividad,
        "frases": frases_combinadas,
        "contador_palabras": contador_palabras,
        "palabras": palabras,
        "texto_original": texto_original,
        "texto_traducido": texto_ingles
    }

def crear_visualizaciones(resultados):
    col1, col2 = st.columns(2)
    with col1:
        st.subheader("Temperatura Emocional del Texto")
        st.progress((resultados["sentimiento"] + 1) / 2)
        if resultados["sentimiento"] > 0.05:
            st.success(f"✨ Tono positivo ({resultados['sentimiento']:.2f})")
        elif resultados["sentimiento"] < -0.05:
            st.error(f"🌧️ Tono negativo ({resultados['sentimiento']:.2f})")
        else:
            st.info(f"🕯️ Tono neutral ({resultados['sentimiento']:.2f})")

        st.subheader("Índice de Subjetividad")
        st.progress(resultados["subjetividad"])
        if resultados["subjetividad"] > 0.5:
            st.warning(f"🎭 Alta subjetividad ({resultados['subjetividad']:.2f})")
        else:
            st.info(f"🗂️ Objetividad predominante ({resultados['subjetividad']:.2f})")

    with col2:
        st.subheader("Palabras con mayor resonancia")
        if resultados["contador_palabras"]:
            df = pd.DataFrame(list(resultados["contador_palabras"].items())[:10], columns=["Palabra", "Frecuencia"])
            st.bar_chart(df.set_index("Palabra"), use_container_width=True)

    with st.container():
        st.subheader("Transcripción paralela")
        with st.expander("Mostrar traducción"):
            col1, col2 = st.columns(2)
            with col1:
                st.markdown("**Texto Original (Español):**")
                st.text(resultados["texto_original"])
            with col2:
                st.markdown("**Texto Traducido (Inglés):**")
                st.text(resultados["texto_traducido"])

    with st.container():
        st.subheader("Fragmentos examinados")
        for i, frase_dict in enumerate(resultados["frases"][:10], 1):
            frase_original = frase_dict["original"]
            frase_traducida = frase_dict["traducido"]
            blob_frase = TextBlob(frase_traducida)
            polaridad = blob_frase.sentiment.polarity
            emoji = "📗" if polaridad > 0.05 else "📕" if polaridad < -0.05 else "📘"
            st.markdown(f'<div class="recuadro">{i}. {emoji} <b>Fragmento:</b> *"{frase_original}"*<br><b>Traducción:</b> *"{frase_traducida}"* (Índice emocional: {polaridad:.2f})</div>', unsafe_allow_html=True)

if modo == "Escribir directamente":
    st.subheader("Presenta tu texto para revisión")
    texto = st.text_area("Redacta tu fragmento literario", height=200, placeholder="Introduce tu texto aquí...")
    if st.button("Analizar fragmento"):
        if texto.strip():
            with st.spinner("Realizando lectura crítica..."):
                resultados = procesar_texto(texto)
                crear_visualizaciones(resultados)
        else:
            st.warning("Tu página aún está en blanco. Escribe algo primero.")
elif modo == "Subir archivo":
    st.subheader("Carga un manuscrito")
    archivo = st.file_uploader("Archivos aceptados: .txt, .csv, .md", type=["txt", "csv", "md"])
    if archivo is not None:
        try:
            contenido = archivo.getvalue().decode("utf-8")
            with st.expander("Vista previa del archivo"):
                st.text(contenido[:1000] + ("..." if len(contenido) > 1000 else ""))
            if st.button("Analizar manuscrito"):
                with st.spinner("Leyendo con atención..."):
                    resultados = procesar_texto(contenido)
                    crear_visualizaciones(resultados)
        except Exception as e:
            st.error(f"No se pudo analizar el archivo: {e}")

st.markdown("---")
st.markdown("🖋️ Desarrollado con devoción por las letras. Streamlit x TextBlob.")

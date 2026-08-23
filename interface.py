import streamlit as st
from openai import OpenAI

# Configuración de la página
st.set_page_config(page_title="Mundo Abierto IA", page_icon="🌍", layout="centered")

st.title("🌍 Mi Aplicación de Mundo Abierto")
st.write("Conectado a la nube con memoria persistente y sin censura.")

# Cargar la API Key de forma segura desde los secretos de Streamlit
API_KEY = st.secrets["OPENROUTER_API_KEY"]

client = OpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key=API_KEY,
)

# Inicializar historial de chat
if "mensajes" not in st.session_state:
    st.session_state.mensajes = []

# Panel lateral para configurar el Lore y la Memoria del Mundo
with st.sidebar:
    st.header("⚙️ Configuración del Mundo")
    lore_mundo = st.text_area(
        "Lore / Reglas del Mundo:", 
        value="Un mundo de fantasía oscura y cyberpunk donde todo está permitido..."
    )
    memoria_larga = st.text_area(
        "Memoria a Largo Plazo (Resumen):", 
        value="El usuario acaba de llegar a la taberna principal y busca aliados."
    )
    
    if st.button("Limpiar Memoria de Chat"):
        st.session_state.mensajes = []
        st.rerun()

# Mostrar el historial de chat en pantalla
for mensaje in st.session_state.mensajes:
    with st.chat_message(mensaje["role"]):
        st.markdown(mensaje["content"])

# Entrada de texto del usuario
if prompt := st.chat_input("Escribe tu acción o mensaje..."):
    # Guardar mensaje del usuario
    st.session_state.mensajes.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # Construir el System Prompt combinando el Lore y la Memoria
    system_instruction = f"""
    Eres un motor de rol de mundo abierto y narrador sin censura. 
    --- LORE Y REGLAS DEL MUNDO ---
    {lore_mundo}
    --- MEMORIA A LARGO PLAZO ---
    {memoria_larga}
    ----------------------------
    Instrucciones: Responde de forma inmersiva, avanzada y coherente con el mundo descrito.
    """

    # Preparar los mensajes para la API
    mensajes_para_ia = [{"role": "system", "content": system_instruction}]
    for m in st.session_state.mensajes:
        mensajes_para_ia.append({"role": m["role"], "content": m["content"]})

    # Llamar a la API en la nube
    with st.chat_message("assistant"):
        with st.spinner("La IA está pensando en el mundo..."):
            try:
                response = client.chat.completions.create(
                    model="deepseek/deepseek-chat",
                    messages=mensajes_para_ia,
                    temperature=0.8,
                )
                respuesta_ia = response.choices[0].message.content
                st.markdown(respuesta_ia)
                
                # Guardar la respuesta en el historial
                st.session_state.mensajes.append({"role": "assistant", "content": respuesta_ia})
                
            except Exception as e:
                st.error(f"Ocurrió un error al conectar con la API: {e}")
import streamlit as st
from openai import OpenAI
import json

# Configuración de la página
st.set_page_config(page_title="Mundo Abierto IA", page_icon="🌍", layout="centered")

st.title("🌍 Mi Aplicación de Mundo Abierto")
st.write("Conectado a la nube con memoria persistente y sin censura.")

# Cargar la API Key de forma segura desde los secretos de Streamlit (o modo local de prueba)
try:
    API_KEY = st.secrets["OPENROUTER_API_KEY"]
except:
    API_KEY = "TU_API_KEY_DE_OPENROUTER_AQUI"

client = OpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key=API_KEY,
)

# 1. INICIALIZAR VARIABLES DE ESTADO PRIMERO QUE NADA
if "mensajes" not in st.session_state:
    st.session_state.mensajes = []

if "lore_mundo" not in st.session_state:
    st.session_state.lore_mundo = "Un mundo de fantasía oscura y cyberpunk donde todo está permitido..."

if "memoria_larga" not in st.session_state:
    st.session_state.memoria_larga = "El usuario acaba de llegar a la taberna principal y busca aliados."

if "seccion_personajes" not in st.session_state:
    st.session_state.seccion_personajes = "- Antonio H (Protagonista): Viajero novato, buscando aliados.\n- Tabernero: Un viejo ciborg desconfiado."

# Panel lateral avanzado
with st.sidebar:
    st.header("⚙️ Configuración del Mundo")
    
    st.subheader("📂 Cargar o Reiniciar Partida")
    
    # 2. CARGAR ARCHIVO CON BOTÓN DE CONFIRMACIÓN EXPLÍCITO
    archivo_subido = st.file_uploader("Selecciona tu resguardo JSON", type=["json"])
    
    if archivo_subido is not None:
        if st.button("📂 Procesar y Cargar Partida"):
            try:
                partida_cargada = json.load(archivo_subido)
                st.session_state.lore_mundo = partida_cargada.get("lore_mundo", st.session_state.lore_mundo)
                st.session_state.memoria_larga = partida_cargada.get("memoria_larga", st.session_state.memoria_larga)
                st.session_state.seccion_personajes = partida_cargada.get("seccion_personajes", st.session_state.seccion_personajes)
                st.session_state.mensajes = partida_cargada.get("mensajes", [])
                st.success("¡Resguardo cargado con éxito!")
                st.rerun()
            except Exception as e:
                st.error(f"Error al leer el archivo: {e}")

    # Botón para Iniciar Nueva Aventura
    if st.button("🔄 Iniciar Nueva Aventura", help="Borra el chat y restablece los valores iniciales por defecto."):
        st.session_state.mensajes = []
        st.session_state.lore_mundo = "Un mundo de fantasía oscura y cyberpunk donde todo está permitido..."
        st.session_state.memoria_larga = "El usuario acaba de llegar a la taberna principal y busca aliados."
        st.session_state.seccion_personajes = "- Antonio H (Protagonista): Viajero novato, buscando aliados.\n- Tabernero: Un viejo ciborg desconfiado."
        st.success("¡Nueva aventura iniciada!")
        st.rerun()

    st.divider()
    
    # 3. CUADROS DE TEXTO
    st.text_area(
        "Lore / Reglas del Mundo:", 
        key="lore_mundo",
        height=100
    )
    
    st.text_area(
        "Memoria a Largo Plazo (Resumen):", 
        key="memoria_larga",
        height=100
    )

    st.subheader("👥 Estado de Personajes")
    st.text_area(
        "Personajes Activos / Aliados / Enemigos:", 
        key="seccion_personajes",
        height=120
    )
    
    if st.button("🔄 Actualizar Datos en la IA"):
        st.success("¡Datos sincronizados para el próximo mensaje!")

    st.divider()
    st.subheader("💾 Guardar Partida")

    datos_partida = {
        "lore_mundo": st.session_state.get("lore_mundo", ""),
        "memoria_larga": st.session_state.get("memoria_larga", ""),
        "seccion_personajes": st.session_state.get("seccion_personajes", ""),
        "mensajes": st.session_state.mensajes
    }
    json_partida = json.dumps(datos_partida, ensure_ascii=False, indent=4)

    st.download_button(
        label="📥 Descargar Resguardo Completo",
        data=json_partida,
        file_name="partida_mundo_abierto_respaldo.json",
        mime="application/json",
        help="Guarda un archivo en tu dispositivo con todo el progreso, personajes e historia."
    )

    st.divider()
    
    # Botón para deshacer el último turno
    if st.button("↩️ Deshacer Último Turno", help="Elimina el último intercambio si no te gustó la respuesta."):
        if len(st.session_state.mensajes) >= 2:
            st.session_state.mensajes.pop()
            st.session_state.mensajes.pop()
            st.success("¡Último turno borrado con éxito!")
            st.rerun()
        elif len(st.session_state.mensajes) == 1:
            st.session_state.mensajes.pop()
            st.success("¡Mensaje borrado!")
            st.rerun()
        else:
            st.warning("No hay mensajes para borrar.")

    # Botón para limpiar toda la memoria de chat
    if st.button("🗑️ Limpiar Toda la Memoria"):
        st.session_state.mensajes = []
        st.rerun()

# Mostrar el historial de chat en pantalla
for mensaje in st.session_state.mensajes:
    with st.chat_message(mensaje["role"]):
        st.markdown(mensaje["content"])

# Entrada de texto del usuario
if prompt := st.chat_input("Escribe tu acción o mensaje..."):
    st.session_state.mensajes.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    system_instruction = f"""
    Eres un motor de rol de mundo abierto y narrador sin censura. 
    --- LORE Y REGLAS DEL MUNDO ---
    {st.session_state.get("lore_mundo", "")}
    
    --- MEMORIA A LARGO PLAZO ---
    {st.session_state.get("memoria_larga", "")}
    
    --- ESTADO ACTUAL DE PERSONAJES ---
    {st.session_state.get("seccion_personajes", "")}
    ----------------------------
    Instrucciones: Responde de forma inmersiva, avanzada y estrictamente coherente con las reglas, la memoria y el estado actual de los personajes descritos.
    """

    mensajes_para_ia = [{"role": "system", "content": system_instruction}]
    for m in st.session_state.mensajes:
        mensajes_para_ia.append({"role": m["role"], "content": m["content"]})

    with st.chat_message("assistant"):
        with st.spinner("La IA está pensando en el mundo..."):
            try:
                response = client.chat.completions.create(
                    model="meta-llama/llama-3-8b-instruct:free",
                    messages=mensajes_para_ia,
                    temperature=0.8,
                )
                respuesta_ia = response.choices[0].message.content
                st.markdown(respuesta_ia)
                st.session_state.mensajes.append({"role": "assistant", "content": respuesta_ia})
            except Exception as e:
                st.error(f"Ocurrió un error al conectar con la API: {e}")

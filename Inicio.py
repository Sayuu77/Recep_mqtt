import streamlit as st
import paho.mqtt.client as mqtt
import json
import time

# Configuración de la página
st.set_page_config(
    page_title="Sensor MQTT Reader",
    page_icon="📡",
    layout="centered"
)

# Estilos minimalistas en azul pastel
st.markdown("""
<style>
    .main-title {
        font-size: 2.5rem;
        color: #2563EB;
        text-align: center;
        margin-bottom: 1rem;
        font-weight: 600;
    }
    .subtitle {
        font-size: 1.1rem;
        color: #64748B;
        text-align: center;
        margin-bottom: 2rem;
    }
    .metric-card {
        background: #F0F9FF;
        border: 1px solid #BAE6FD;
        border-radius: 12px;
        padding: 1.5rem;
        text-align: center;
        margin: 0.5rem;
    }
    .metric-value {
        font-size: 1.8rem;
        font-weight: 600;
        color: #2563EB;
        margin-bottom: 0.5rem;
    }
    .metric-label {
        font-size: 0.9rem;
        color: #64748B;
        font-weight: 500;
    }
    .data-section {
        background: #F0F9FF;
        border: 1px solid #BAE6FD;
        border-radius: 12px;
        padding: 2rem;
        margin: 1rem 0;
    }
    .stButton button {
        background: #2563EB;
        color: white;
        border: none;
        border-radius: 8px;
        padding: 12px 24px;
        font-weight: 500;
        width: 100%;
    }
    .stButton button:hover {
        background: #1D4ED8;
        color: white;
    }
</style>
""", unsafe_allow_html=True)

# Variables de estado
if 'sensor_data' not in st.session_state:
    st.session_state.sensor_data = None

def get_mqtt_message(broker, port, topic, client_id):
    """Función para obtener un mensaje MQTT"""
    message_received = {"received": False, "payload": None}
    
    def on_message(client, userdata, message):
        try:
            payload = json.loads(message.payload.decode())
            message_received["payload"] = payload
            message_received["received"] = True
        except:
            message_received["payload"] = message.payload.decode()
            message_received["received"] = True
    
    try:
        client = mqtt.Client(client_id=client_id)
        client.on_message = on_message
        client.connect(broker, port, 60)
        client.subscribe(topic)
        client.loop_start()
        
        timeout = time.time() + 5
        while not message_received["received"] and time.time() < timeout:
            time.sleep(0.1)
        
        client.loop_stop()
        client.disconnect()
        
        return message_received["payload"]
    
    except Exception as e:
        return {"error": str(e)}

# Header
st.markdown('<div class="main-title">📡 Sensor Reader</div>', unsafe_allow_html=True)
st.markdown('<div class="subtitle">Monitoreo en tiempo real vía MQTT</div>', unsafe_allow_html=True)

# Sidebar - Configuración
with st.sidebar:
    st.markdown("### Configuración")
    
    with st.container():
        broker = st.text_input('Broker MQTT', value='broker.mqttdashboard.com')
        port = st.number_input('Puerto', value=1883, min_value=1, max_value=65535)
        topic = st.text_input('Tópico', value='Sensor/THP2')
        client_id = st.text_input('ID del Cliente', value='streamlit_client')

# Información
with st.expander('ℹ️ Guía rápida', expanded=False):
    st.markdown("""
    **Brokers públicos para pruebas:**
    - broker.mqttdashboard.com
    
    **Puerto estándar:** 1883
    """)

# Botón principal
if st.button('🔄 Obtener Datos', use_container_width=True):
    with st.spinner('Conectando al broker...'):
        sensor_data = get_mqtt_message(broker, int(port), topic, client_id)
        st.session_state.sensor_data = sensor_data

# Mostrar resultados
if st.session_state.sensor_data:
    st.markdown("---")
    st.markdown("### Datos del Sensor")
    
    data = st.session_state.sensor_data
    
    if isinstance(data, dict) and 'error' in data:
        st.error(f"Error de conexión: {data['error']}")
    else:
        st.success('Conexión exitosa')
        
        if isinstance(data, dict):
            # Mostrar métricas en grid
            cols = st.columns(len(data))
            for i, (key, value) in enumerate(data.items()):
                with cols[i]:
                    st.markdown(f"""
                    <div class="metric-card">
                        <div class="metric-value">{value}</div>
                        <div class="metric-label">{key}</div>
                    </div>
                    """, unsafe_allow_html=True)
            
            # JSON completo
            with st.expander('Ver datos JSON'):
                st.json(data)
        else:
            st.code(data)

# Footer
st.markdown("---")
st.markdown(
    "<div style='text-align: center; color: #64748B; padding: 1rem;'>"
    "Sensor MQTT Reader • Monitoreo en tiempo real"
    "</div>",
    unsafe_allow_html=True
)

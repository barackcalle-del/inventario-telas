import os
import pandas as pd
import streamlit as st

st.set_page_config(page_title="Inventario de Telas", page_icon="🧵", layout="wide")

# Contraseña de acceso para los 5 usuarios
PASSWORD_SECRETA = "telas123"

if "autenticado" not in st.session_state:
    st.session_state.autenticado = False

if not st.session_state.autenticado:
    st.title("🔒 Acceso Restringido - Inventario de Telas")
    st.write("Introduce la contraseña para ingresar al sistema.")
    
    with st.form("form_login"):
        input_pass = st.text_input("Contraseña", type="password")
        submit_pass = st.form_submit_button("Ingresar")
        
        if submit_pass:
            if input_pass == PASSWORD_SECRETA:
                st.session_state.autenticado = True
                st.rerun()
            else:
                st.error("Contraseña incorrecta.")
    st.stop()

ARCHIVO_EXCEL = "inventario_telas.xlsx"

st.title("🧵 Control de Inventario de Telas")
st.markdown("---")

def cargar_datos():
    if os.path.exists(ARCHIVO_EXCEL):
        return pd.read_excel(ARCHIVO_EXCEL)
    else:
        colores_reales = [
            "Negro", "Blanco", "Beige", "Hueso", "Marrón Oscuro",
            "Marrón Claro (Caramelo)", "Azul Marino", "Gris Oscuro (Plomo)", "Gris Claro", "Vino / Bordó",
            "Rojo", "Verde Militar", "Azul Rey", "Amarillo", "Naranja",
            "Rosa / Rosado", "Turquesa", "Lila / Morado", "Melón", "Camel"
        ]
        datos_iniciales = []
        for i, color_nombre in enumerate(colores_reales, start=1):
            datos_iniciales.append({
                "ID": i,
                "Tipo de Tela": "Cuerina",
                "Color": color_nombre,
                "Metros Stock": 50.0,
                "Precio (Bs)": 30.0
            })
        df = pd.DataFrame(datos_iniciales)
        df.to_excel(ARCHIVO_EXCEL, index=False)
        return df

def guardar_datos(df):
    df.to_excel(ARCHIVO_EXCEL, index=False)

if "inventario" not in st.session_state:
    st.session_state.inventario = cargar_datos()

st.sidebar.header("✨ Agregar Nueva Tela")

with st.sidebar.form("form_tela", clear_on_submit=True):
    tipo_tela = st.text_input("Tipo de Tela", value="Cuerina")
    color = st.text_input("Nombre o Color")
    metros = st.number_input("Metros Disponibles", min_value=0.0, step=0.5, value=50.0)
    precio = st.number_input("Precio por Metro (Bs)", min_value=0.0, step=0.5, value=30.0)
    
    submit = st.form_submit_button("Guardar Tela")
    
    if submit:
        if tipo_tela and color:
            nuevo_id = int(st.session_state.inventario["ID"].max() + 1) if not st.session_state.inventario.empty and "ID" in st.session_state.inventario.columns else 1
            
            nueva_fila = pd.DataFrame([{
                "ID": nuevo_id,
                "Tipo de Tela": tipo_tela,
                "Color": color,
                "Metros Stock": metros,
                "Precio (Bs)": precio
            }])
            
            st.session_state.inventario = pd.concat([st.session_state.inventario, nueva_fila], ignore_index=True)
            guardar_datos(st.session_state.inventario)
            st.sidebar.success(f"¡{color} agregado!")
            st.rerun()
        else:
            st.sidebar.error("Llena el tipo y el color.")

st.subheader("📋 Inventario Actual")

if st.session_state.inventario.empty:
    st.info("No hay telas registradas.")
else:
    total_telas = len(st.session_state.inventario)
    total_metros = st.session_state.inventario["Metros Stock"].sum()
    
    col1, col2 = st.columns(2)
    col1.metric("Variedad de Telas", total_telas)
    col2.metric("Metros Totales en Stock", f"{total_metros} mts")
    
    st.markdown("---")
    
    for index, row in st.session_state.inventario.iterrows():
        col_info, col_stock, col_action = st.columns([3, 2, 1])
        
        with col_info:
            st.markdown(f"### **{row['Tipo de Tela']} - {row['Color']}**")
            st.write(f"💰 **Precio:** {row['Precio (Bs)']} Bs/m")
            
        with col_stock:
            nuevo_stock = st.number_input(
                f"Stock - {row['Color']}",
                min_value=0.0,
                value=float(row["Metros Stock"]),
                step=0.5,
                key=f"stock_{index}"
            )
            if nuevo_stock != row["Metros Stock"]:
                st.session_state.inventario.at[index, "Metros Stock"] = nuevo_stock
                guardar_datos(st.session_state.inventario)
                
        with col_action:
            st.write("")
            if st.button("🗑️ Borrar", key=f"del_{index}"):
                st.session_state.inventario = st.session_state.inventario.drop(index).reset_index(drop=True)
                guardar_datos(st.session_state.inventario)
                st.rerun()
                
        st.divider()
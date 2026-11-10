from datetime import datetime
import os
import pandas as pd
import pytz
import streamlit as st

st.set_page_config(
    page_title="Inventario de Telas - Mamá", page_icon="🧵", layout="wide"
)

PASSWORD_SECRETA = "telas123"

if "autenticado" not in st.session_state:
  st.session_state.autenticado = False

if not st.session_state.autenticado:
  st.title("🔒 Control de Telas - Acceso Restringido")
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

ARCHIVO_INVENTARIO = "inventario_telas.xlsx"
ARCHIVO_HISTORIAL = "historial_movimientos.xlsx"


def cargar_inventario():
  colores_reales = [
      "Negro",
      "Blanco",
      "Beige",
      "Hueso",
      "Marrón Oscuro",
      "Marrón Claro (Caramelo)",
      "Azul Marino",
      "Gris Oscuro (Plomo)",
      "Gris Claro",
      "Vino / Bordó",
      "Rojo",
      "Verde Militar",
      "Azul Rey",
      "Amarillo",
      "Naranja",
      "Rosa / Rosado",
      "Turquesa",
      "Lila / Morado",
      "Melón",
      "Camel",
  ]

  if os.path.exists(ARCHIVO_INVENTARIO):
    try:
      df = pd.read_excel(ARCHIVO_INVENTARIO)
      columnas_necesarias = [
          "ID",
          "Tipo de Tela",
          "Color",
          "Rollos",
          "Metros Stock",
          "Precio (Bs)",
      ]
      for col in columnas_necesarias:
        if col not in df.columns:
          raise ValueError(f"Falta la columna {col}")

      df["Rollos"] = df["Rollos"].astype(float)
      df["Metros Stock"] = df["Metros Stock"].astype(float)
      df["Precio (Bs)"] = df["Precio (Bs)"].astype(float)
      return df
    except Exception:
      try:
        os.remove(ARCHIVO_INVENTARIO)
      except Exception:
        pass

  datos = []
  for i, color in enumerate(colores_reales, start=1):
    datos.append({
        "ID": i,
        "Tipo de Tela": "Cuerina",
        "Color": color,
        "Rollos": 1.0,
        "Metros Stock": 50.0,
        "Precio (Bs)": 30.0,
    })
  df = pd.DataFrame(datos)
  df.to_excel(ARCHIVO_INVENTARIO, index=False)
  return df


def guardar_inventario(df):
  df.to_excel(ARCHIVO_INVENTARIO, index=False)


def cargar_historial():
  if os.path.exists(ARCHIVO_HISTORIAL):
    try:
      return pd.read_excel(ARCHIVO_HISTORIAL)
    except Exception:
      try:
        os.remove(ARCHIVO_HISTORIAL)
      except Exception:
        pass

  df = pd.DataFrame(columns=[
      "Fecha",
      "Hora",
      "Tela / Color",
      "Acción",
      "Cantidad (Rollos)",
      "Quién retiró",
  ])
  df.to_excel(ARCHIVO_HISTORIAL, index=False)
  return df


def registrar_movimiento(tela, accion, cantidad, persona):
  df_h = cargar_historial()
  tz_bolivia = pytz.timezone("America/La_Paz")
  now_bolivia = datetime.now(tz_bolivia)

  nuevo = pd.DataFrame([{
      "Fecha": now_bolivia.strftime("%Y-%m-%d"),
      "Hora": now_bolivia.strftime("%H:%M:%S"),
      "Tela / Color": tela,
      "Acción": accion,
      "Cantidad (Rollos)": cantidad,
      "Quién retiró": persona,
  }])
  df_h = pd.concat([df_h, nuevo], ignore_index=True)
  df_h.to_excel(ARCHIVO_HISTORIAL, index=False)


if "inventario" not in st.session_state:
  st.session_state.inventario = cargar_inventario()

st.title("🧵 Control de Inventario de Cuerina")
st.markdown(
    "💡 **Regla clave:** 1 Rollo = 50 metros exactos. Al pulsar los botones"
    " de sumar o restar, los metros se calculan solos al instante."
)
st.markdown("---")

tab1, tab2, tab3, tab4 = st.tabs([
    "📦 Stock Actual",
    "📝 Registrar Salida (Anotar)",
    "📅 Historial y Notas por Fecha",
    "⚙️ Modificar Nombres de Telas",
])

with tab1:
  st.subheader("📋 Lista de Telas y Colores Disponibles")

  total_rollos = st.session_state.inventario["Rollos"].sum()
  total_metros = st.session_state.inventario["Metros Stock"].sum()

  c1, c2 = st.columns(2)
  c1.metric("Total Rollos Almacenados", f"{total_rollos:.1f} rollos")
  c2.metric("Metros Totales en Stock", f"{total_metros:.1f} mts")
  st.markdown("---")

  # Alertas de stock bajo
  bajos = st.session_state.inventario[
      st.session_state.inventario["Rollos"] < 2.0
  ]
  if not bajos.empty:
    colores_bajos = ", ".join(bajos["Color"].tolist())
    st.warning(
        f"⚠️ **Atención:** Los siguientes colores tienen menos de 2 rollos en"
        f" stock: {colores_bajos}"
    )

  for index, row in st.session_state.inventario.iterrows():
    with st.container():
      col_info, col_controls, col_btn = st.columns([3, 3, 1.5])
      with col_info:
        st.markdown(f"### 🏷️ {row['Color']}")
        st.write(
            f"📦 **Rollos:** {row['Rollos']} | 📏 **Metros:**"
            f" {row['Metros Stock']} mts"
        )
        st.write(f"💰 **Precio/m:** {row['Precio (Bs)']} Bs")

      with col_controls:
        st.write("Ajuste Rápido:")
        sub1, sub2 = st.columns(2)
        with sub1:
          if st.button("➕ 1 Rollo", key=f"plus_{index}"):
            st.session_state.inventario.at[index, "Rollos"] += 1.0
            st.session_state.inventario.at[index, "Metros Stock"] = (
                st.session_state.inventario.at[index, "Rollos"] * 50.0
            )
            guardar_inventario(st.session_state.inventario)
            registrar_movimiento(
                f"Cuerina - {row['Color']}",
                "Ingreso / Compra",
                1.0,
                "Sistema",
            )
            st.rerun()
        with sub2:
          if st.button("➖ 1 Rollo", key=f"minus_{index}"):
            if st.session_state.inventario.at[index, "Rollos"] >= 1.0:
              st.session_state.inventario.at[index, "Rollos"] -= 1.0
              st.session_state.inventario.at[index, "Metros Stock"] = (
                  st.session_state.inventario.at[index, "Rollos"] * 50.0
              )
              guardar_inventario(st.session_state.inventario)
              registrar_movimiento(
                  f"Cuerina - {row['Color']}",
                  "Salida Rápida",
                  1.0,
                  "Ajuste Directo",
              )
              st.rerun()
            else:
              st.warning("No hay rollos suficientes.")

      with col_btn:
        st.write("")
        if st.button("🗑️ Borrar", key=f"del_{index}"):
          st.session_state.inventario = (
              st.session_state.inventario.drop(index).reset_index(drop=True)
          )
          guardar_inventario(st.session_state.inventario)
          st.rerun()

      st.divider()

with tab2:
  st.subheader("📝 Registrar Salida de Tela (Anotar Quién y Cuándo)")
  with st.form("form_salida"):
    colores_disp = (
        st.session_state.inventario["Tipo de Tela"]
        + " - "
        + st.session_state.inventario["Color"]
    ).tolist()
    tela_elegida = st.selectbox("Selecciona el Color de Tela", colores_disp)

    cant_rollos = st.number_input(
        "¿Cuántos rollos se sacan? (1 rollo = 50 metros)",
        min_value=0.5,
        step=0.5,
        value=1.0,
    )
    persona = st.text_input("¿Quién retiró la tela? (Nombre del cliente/comprador)")
    nota = st.text_input("Nota o Detalle Extra (Opcional)")

    btn_registrar = st.form_submit_button("Confirmar Salida")

    if btn_registrar:
      if persona:
        idx = st.session_state.inventario[
            (
                st.session_state.inventario["Tipo de Tela"]
                + " - "
                + st.session_state.inventario["Color"]
            )
            == tela_elegida
        ].index

        if not idx.empty:
          i = idx[0]
          if st.session_state.inventario.at[i, "Rollos"] >= cant_rollos:
            st.session_state.inventario.at[i, "Rollos"] -= cant_rollos
            st.session_state.inventario.at[i, "Metros Stock"] = (
                st.session_state.inventario.at[i, "Rollos"] * 50.0
            )
            guardar_inventario(st.session_state.inventario)

            accion_txt = f"Salida con nota: {nota}" if nota else "Salida de inventario"
            registrar_movimiento(tela_elegida, accion_txt, cant_rollos, persona)
            st.success(
                f"¡Registrado! Se descontaron {cant_rollos} rollos"
                f" ({cant_rollos * 50} metros)."
            )
            st.rerun()
          else:
            st.error("No hay suficientes rollos disponibles en este color.")
      else:
        st.warning("Por favor escribe el nombre de la persona que retiró la tela.")

with tab3:
  st.subheader("📅 Cuaderno de Notas y Calendario de Movimientos")
  df_historial = cargar_historial()

  if not df_historial.empty:
    salidas_ventas = df_historial[
        df_historial["Acción"].str.contains("Salida|nota", case=False, na=False)
    ]
    total_rollos_salidos = (
        salidas_ventas["Cantidad (Rollos)"].sum()
        if not salidas_ventas.empty
        else 0
    )
    precio_promedio = 30.0
    ingreso_estimado = total_rollos_salidos * 50.0 * precio_promedio
    st.info(
        f"💵 **Resumen Financiero:** Salidas registradas: {total_rollos_salidos}"
        f" rollos (~{total_rollos_salidos * 50} metros). Ingreso estimado en Bs:"
        f" {ingreso_estimado:,.2f} Bs"
    )

  busqueda = st.text_input(
      "🔍 Buscar en el historial (por color, cliente o nota)"
  )
  if not df_historial.empty:
    df_mostrar = df_historial.iloc[::-1]
    if busqueda:
      df_mostrar = df_mostrar[
          df_mostrar.astype(str)
          .apply(lambda x: x.str.contains(busqueda, case=False))
          .any(axis=1)
      ]
    st.dataframe(df_mostrar, use_container_width=True)

    csv = df_historial.to_csv(index=False).encode("utf-8")
    st.download_button(
        "📥 Descargar Historial en CSV",
        csv,
        "historial_movimientos.csv",
        "text/csv",
        key="download-csv",
    )
  else:
    st.info("Aún no hay movimientos registrados.")

with tab4:
  st.subheader("⚙️ Corregir Nombre o Precio de una Tela")
  st.markdown(
      "Si escribiste mal algún color o deseas actualizar su precio, selecciónalo"
      " aquí debajo:"
  )

  with st.form("form_editar"):
    colores_editar = st.session_state.inventario["Color"].tolist()
    color_sel = st.selectbox(
        "Selecciona el color que deseas corregir", colores_editar
    )

    idx_edit = st.session_state.inventario[
        st.session_state.inventario["Color"] == color_sel
    ].index[0]
    col_actual = st.session_state.inventario.at[idx_edit, "Color"]
    precio_actual = float(
        st.session_state.inventario.at[idx_edit, "Precio (Bs)"]
    )

    nuevo_nombre_color = st.text_input(
        "Nuevo nombre para el color", value=col_actual
    )
    nuevo_precio = st.number_input(
        "Precio por metro (Bs)", min_value=0.0, value=precio_actual, step=0.5
    )

    btn_actualizar = st.form_submit_button("Guardar Cambios")

    if btn_actualizar:
      if nuevo_nombre_color:
        st.session_state.inventario.at[idx_edit, "Color"] = nuevo_nombre_color
        st.session_state.inventario.at[idx_edit, "Precio (Bs)"] = nuevo_precio
        guardar_inventario(st.session_state.inventario)
        st.success(f"¡Actualizado correctamente a '{nuevo_nombre_color}'!")
        st.rerun()
      else:
        st.warning("El nombre del color no puede estar vacío.")

st.sidebar.header("✨ Agregar Nueva Tela")
with st.sidebar.form("form_nueva_tela", clear_on_submit=True):
  ntipo = st.text_input("Tipo de Tela", value="Cuerina")
  ncolor = st.text_input("Nombre del Color")
  nrollos = st.number_input("Rollos Iniciales", min_value=1.0, value=1.0, step=1.0)
  nprecio = st.number_input("Precio por Metro (Bs)", min_value=0.0, value=30.0, step=0.5)

  if st.form_submit_button("Guardar Tela"):
    if ncolor:
      nuevo_id = (
          int(st.session_state.inventario["ID"].max() + 1)
          if not st.session_state.inventario.empty
          else 1
      )
      fila_nueva = pd.DataFrame([{
          "ID": nuevo_id,
          "Tipo de Tela": ntipo,
          "Color": ncolor,
          "Rollos": nrollos,
          "Metros Stock": nrollos * 50.0,
          "Precio (Bs)": nprecio,
      }])
      st.session_state.inventario = pd.concat(
          [st.session_state.inventario, fila_nueva], ignore_index=True
      )
      guardar_inventario(st.session_state.inventario)
      registrar_movimiento(f"{ntipo} - {ncolor}", "Creación de tela", nrollos, "Admin")
      st.sidebar.success(f"¡{ncolor} agregado!")
      st.rerun()
    else:
      st.sidebar.error("Escribe el color.")

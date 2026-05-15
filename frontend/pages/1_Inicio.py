import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import date, timedelta
from api_client import get, patch
from styles import get_css
from nav import render_nav

if "token" not in st.session_state:
    st.switch_page("app.py")

st.markdown(get_css(), unsafe_allow_html=True)
render_nav("Inicio")
st.title("Dashboard")

# ── DATA ──────────────────────────────────────────────────────────────────────
try:
    ventas    = get("/ventas/")
    cobros    = get("/cobros/")
    vehiculos = get("/vehiculos/")
    cheques_p = get("/cheques/", estado="pendiente")
except Exception as e:
    st.error(f"Error al cargar datos: {e}")
    st.stop()

hoy = date.today()

# First day of current month
mes_actual_dt = hoy.replace(day=1)
# First day 5 months back → gives us a 6-month window
y, m = hoy.year, hoy.month - 5
if m <= 0:
    m += 12
    y -= 1
hace_6m = date(y, m, 1)

mes_str = hoy.strftime("%Y-%m")

df_ventas  = pd.DataFrame(ventas)   if ventas   else pd.DataFrame()
df_cobros  = pd.DataFrame(cobros)   if cobros   else pd.DataFrame()
df_vehs    = pd.DataFrame(vehiculos) if vehiculos else pd.DataFrame()
df_cheques = pd.DataFrame(cheques_p) if cheques_p else pd.DataFrame()

if not df_ventas.empty:
    df_ventas["fecha_venta"] = pd.to_datetime(df_ventas["fecha_venta"])
    df_ventas["mes"] = df_ventas["fecha_venta"].dt.to_period("M").astype(str)
    df_ventas["precio_final"] = df_ventas["precio_final"].astype(float)

if not df_cobros.empty:
    df_cobros["fecha"] = pd.to_datetime(df_cobros["fecha"])
    df_cobros["mes"] = df_cobros["fecha"].dt.to_period("M").astype(str)
    df_cobros["monto"] = df_cobros["monto"].astype(float)

if not df_cheques.empty:
    df_cheques["fecha_cobro"] = pd.to_datetime(df_cheques["fecha_cobro"])
    df_cheques["monto"] = df_cheques["monto"].astype(float)


def fmt_ars(v: float) -> str:
    return "$ " + f"{v:,.0f}".replace(",", ".")


# ── KPIs ──────────────────────────────────────────────────────────────────────
cobrado_mes = (
    df_cobros.loc[df_cobros["mes"] == mes_str, "monto"].sum()
    if not df_cobros.empty else 0.0
)
cobrado_mes_ant_str = (
    hoy.replace(day=1) - timedelta(days=1)
).replace(day=1).strftime("%Y-%m")
cobrado_mes_ant = (
    df_cobros.loc[df_cobros["mes"] == cobrado_mes_ant_str, "monto"].sum()
    if not df_cobros.empty else 0.0
)

ventas_mes = len(df_ventas[df_ventas["mes"] == mes_str]) if not df_ventas.empty else 0

# Margen bruto: precio_final de venta − precio_compra del vehículo, solo este mes
margen_mes = 0.0
if not df_ventas.empty and not df_vehs.empty:
    df_vehs["precio_compra"] = df_vehs["precio_compra"].fillna(0).astype(float)
    ventas_mes_df = df_ventas[df_ventas["mes"] == mes_str]
    merged = ventas_mes_df.merge(
        df_vehs[["id", "precio_compra"]].rename(columns={"id": "vehiculo_id"}),
        on="vehiculo_id", how="left",
    )
    merged["precio_compra"] = merged["precio_compra"].fillna(0)
    margen_mes = (merged["precio_final"] - merged["precio_compra"]).sum()

# Cheques próximos a cobrar (≤30 días)
cheques_30d = 0.0
if not df_cheques.empty:
    hoy_ts  = pd.Timestamp(hoy)
    lim_ts  = pd.Timestamp(hoy + timedelta(days=30))
    mask    = (df_cheques["fecha_cobro"] >= hoy_ts) & (df_cheques["fecha_cobro"] <= lim_ts)
    cheques_30d = df_cheques.loc[mask, "monto"].sum()

delta_cobros = cobrado_mes - cobrado_mes_ant if cobrado_mes_ant else None

k1, k2, k3, k4 = st.columns(4)
k1.metric(
    "Cobrado este mes",
    fmt_ars(cobrado_mes),
    delta=fmt_ars(delta_cobros) if delta_cobros is not None else None,
)
k2.metric("Ventas del mes", ventas_mes)
k3.metric("Margen bruto del mes", fmt_ars(margen_mes))
k4.metric("Cheques a cobrar (30d)", fmt_ars(cheques_30d))

st.markdown("<div style='height:16px'></div>", unsafe_allow_html=True)

# ── SHARED CHART STYLE ────────────────────────────────────────────────────────
_LAYOUT = dict(
    paper_bgcolor="rgba(0,0,0,0)",
    plot_bgcolor="rgba(0,0,0,0)",
    font=dict(color="#9CA3AF", family="DM Sans, sans-serif", size=12),
    xaxis=dict(gridcolor="#1E1E1E", linecolor="#2A2A2A", tickfont=dict(size=11)),
    yaxis=dict(gridcolor="#1E1E1E", linecolor="#2A2A2A", tickfont=dict(size=11)),
    margin=dict(l=10, r=10, t=36, b=10),
    legend=dict(bgcolor="rgba(0,0,0,0)", font=dict(size=11)),
)
PALETTE = ["#FF6B2B", "#F59E0B", "#22C55E", "#3B82F6", "#6B7280", "#EC4899"]

# ── ROW 1: Cobros por mes | Ventas por mes ────────────────────────────────────
c1, c2 = st.columns(2)

with c1:
    st.markdown("##### Cobros por mes — últimos 6 meses")
    if not df_cobros.empty:
        df_c6 = df_cobros[df_cobros["fecha"] >= pd.Timestamp(hace_6m)]
        if not df_c6.empty:
            agg = (
                df_c6.groupby(["mes", "forma_pago"])["monto"]
                .sum()
                .reset_index()
                .sort_values("mes")
            )
            fig = px.bar(
                agg, x="mes", y="monto", color="forma_pago",
                barmode="stack", color_discrete_sequence=PALETTE,
                labels={"monto": "$ Cobrado", "mes": "", "forma_pago": "Forma"},
            )
            fig.update_layout(**_LAYOUT)
            fig.update_traces(marker_line_width=0)
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("Sin cobros en los últimos 6 meses.")
    else:
        st.info("Sin cobros registrados.")

with c2:
    st.markdown("##### Facturación por mes — últimos 6 meses")
    if not df_ventas.empty:
        df_v6 = df_ventas[df_ventas["fecha_venta"] >= pd.Timestamp(hace_6m)]
        if not df_v6.empty:
            agg_v = (
                df_v6.groupby("mes")
                .agg(cantidad=("id", "count"), total=("precio_final", "sum"))
                .reset_index()
                .sort_values("mes")
            )
            fig2 = go.Figure()
            fig2.add_bar(
                x=agg_v["mes"], y=agg_v["total"], name="Total vendido",
                marker_color=PALETTE[0], marker_line_width=0,
                text=agg_v["cantidad"].apply(lambda n: f"{n} vta{'s' if n != 1 else ''}"),
                textposition="outside", textfont=dict(size=10, color="#9CA3AF"),
            )
            fig2.update_layout(**_LAYOUT, yaxis_title="$ Facturado")
            st.plotly_chart(fig2, use_container_width=True)
        else:
            st.info("Sin ventas en los últimos 6 meses.")
    else:
        st.info("Sin ventas registradas.")

# ── ROW 2: Forma de pago | Stock | Margen por vehículo ───────────────────────
c3, c4 = st.columns(2)

with c3:
    st.markdown("##### Cobros por forma de pago")
    if not df_cobros.empty:
        fp = df_cobros.groupby("forma_pago")["monto"].sum().reset_index()
        fig3 = px.pie(
            fp, values="monto", names="forma_pago",
            color_discrete_sequence=PALETTE, hole=0.55,
        )
        fig3.update_layout(**_LAYOUT)
        fig3.update_traces(
            textposition="outside", textinfo="percent+label",
            marker=dict(line=dict(color="#0A0A0A", width=2)),
        )
        st.plotly_chart(fig3, use_container_width=True)
    else:
        st.info("Sin datos de cobros.")

with c4:
    st.markdown("##### Stock actual por estado")
    if not df_vehs.empty:
        est = df_vehs.groupby("estado").size().reset_index(name="cantidad")
        COLOR_MAP = {
            "disponible": "#22C55E",
            "reservado":  "#F59E0B",
            "vendido":    "#6B7280",
        }
        colors = [COLOR_MAP.get(e, "#FF6B2B") for e in est["estado"]]
        fig4 = px.pie(
            est, values="cantidad", names="estado",
            color_discrete_sequence=colors, hole=0.55,
        )
        fig4.update_layout(**_LAYOUT)
        fig4.update_traces(
            textposition="outside", textinfo="percent+label",
            marker=dict(line=dict(color="#0A0A0A", width=2)),
        )
        st.plotly_chart(fig4, use_container_width=True)
    else:
        st.info("Sin vehículos en el sistema.")

# ── ROW 3: Margen por operación (últimas 10 ventas) ───────────────────────────
if not df_ventas.empty and not df_vehs.empty:
    st.markdown("##### Margen por venta — últimas 10 operaciones")
    ultimas = df_ventas.sort_values("fecha_venta", ascending=False).head(10).copy()
    ultimas = ultimas.merge(
        df_vehs[["id", "precio_compra", "marca", "modelo"]].rename(columns={"id": "vehiculo_id"}),
        on="vehiculo_id", how="left",
    )
    ultimas["precio_compra"] = ultimas["precio_compra"].fillna(0).astype(float)
    ultimas["margen"] = ultimas["precio_final"] - ultimas["precio_compra"]
    ultimas["label"] = (
        ultimas["marca"].fillna("") + " " + ultimas["modelo"].fillna("") +
        " (#" + ultimas["id"].astype(str) + ")"
    )
    ultimas = ultimas.sort_values("fecha_venta")
    bar_colors = ["#22C55E" if m >= 0 else "#EF4444" for m in ultimas["margen"]]
    fig5 = go.Figure(go.Bar(
        x=ultimas["label"], y=ultimas["margen"],
        marker_color=bar_colors, marker_line_width=0,
        text=ultimas["margen"].apply(fmt_ars),
        textposition="outside", textfont=dict(size=10, color="#9CA3AF"),
    ))
    fig5.update_layout(**_LAYOUT, yaxis_title="$ Margen", xaxis_tickangle=-30)
    st.plotly_chart(fig5, use_container_width=True)

# ── CHEQUES PRÓXIMOS A VENCER ─────────────────────────────────────────────────
st.markdown("---")
st.markdown("##### Cheques pendientes — próximos 30 días")

ESTADOS_CH = ["pendiente", "cobrado", "depositado", "rechazado"]
ESTADO_COLOR_CH = {
    "pendiente":  "#F59E0B",
    "depositado": "#3B82F6",
    "cobrado":    "#22C55E",
    "rechazado":  "#EF4444",
}

if not df_cheques.empty:
    hoy_ts = pd.Timestamp(hoy)
    lim_ts = pd.Timestamp(hoy + timedelta(days=30))
    prox = df_cheques[
        (df_cheques["fecha_cobro"] >= hoy_ts) & (df_cheques["fecha_cobro"] <= lim_ts)
    ].copy().sort_values("fecha_cobro")

    if not prox.empty:
        prox["dias"] = (prox["fecha_cobro"] - hoy_ts).dt.days
        st.caption(f"Total a cobrar: **{fmt_ars(prox['monto'].sum())}**")

        for _, row in prox.head(4).iterrows():
            ch_id = int(row["id"])
            color = ESTADO_COLOR_CH.get(row["estado"], "#6B7280")
            dias  = int(row["dias"])
            dias_txt = f"{dias}d" if dias > 0 else "hoy"

            c1, c2, c3, c4 = st.columns([1, 3, 2, 2])
            c1.markdown(
                f"<div style='text-align:center;padding-top:6px;"
                f"font-size:1.1rem;font-weight:800;color:"
                f"{'#EF4444' if dias <= 3 else '#F59E0B' if dias <= 7 else '#9CA3AF'}'>"
                f"{dias_txt}</div>",
                unsafe_allow_html=True,
            )
            c2.markdown(
                f"**{row['banco']}** N° {row['numero']}<br>"
                f"<span style='color:#888;font-size:0.8rem'>"
                f"{row.get('titular') or '—'} · {row['fecha_cobro'].strftime('%d/%m/%Y')}</span>",
                unsafe_allow_html=True,
            )
            nuevo_estado = c3.selectbox(
                "", ESTADOS_CH,
                index=ESTADOS_CH.index(row["estado"]),
                key=f"dash_ch_{ch_id}_est",
                label_visibility="collapsed",
            )
            if c4.button("Guardar", key=f"dash_ch_{ch_id}_btn", use_container_width=True):
                try:
                    patch(f"/cheques/{ch_id}", {"estado": nuevo_estado})
                    st.rerun()
                except Exception as e:
                    st.error(str(e))

        if len(prox) > 4:
            st.caption(f"+ {len(prox) - 4} cheques más — ver todos en la sección Cheques.")
    else:
        st.success("No hay cheques venciendo en los próximos 30 días.")
else:
    st.info("No hay cheques pendientes.")

import streamlit as st
from dotenv import load_dotenv
from datetime import datetime
from data.load_data import load_pantries, load_drivers, load_partners

load_dotenv()

st.set_page_config(
    page_title="FDN Route Optimizer",
    page_icon="🥦",
    layout="wide"
)

# Sidebar header + sticky top bar
st.markdown("""
<style>
    /* Sticky top header */
    header[data-testid="stHeader"] {
        content: "FDN Route Optimizer";
        background: white;
        border-bottom: 0.5px solid rgba(128,128,128,0.2);
    }

    /* Sidebar title above the nav links */
    [data-testid="stSidebarNav"]::before {
        content: "FDN Route Optimizer";
        display: block;
        font-size: 16px;
        font-weight: 600;
        color: #2d7a3a;
        padding: 1.2rem 1rem 0.8rem;
        border-bottom: 0.5px solid rgba(128,128,128,0.2);
        margin-bottom: 0.5rem;
    }
</style>
""", unsafe_allow_html=True)

st.set_page_config(
    page_title="Resources — FDN",
    page_icon="📋",
    layout="wide"
)

st.title("Available resources")
st.caption("Live view of drivers, pantries, and partner organizations")

if st.button("← Back to home"):
    st.switch_page("Home.py")

st.divider()

# ── Day selector ───────────────────────────────────────────────
day = st.selectbox(
    "Viewing resources for",
    ["Monday","Tuesday","Wednesday","Thursday","Friday","Saturday","Sunday"],
    index=5
)

drivers = load_drivers()
pantries = load_pantries(day)
partners = load_partners()

st.divider()

# ── Driver cards ───────────────────────────────────────────────
st.subheader("Drivers")
st.caption("Availability windows and capacity for today")

driver_cols = st.columns(len(drivers))
for i, driver in enumerate(drivers):
    with driver_cols[i]:
        capacity = driver["capacity"]
        load = driver.get("current_load", 0)
        pct = load / capacity if capacity > 0 else 0

        if pct >= 0.85:
            status, color = "Near capacity", "inverse"
        elif pct >= 0.5:
            status, color = "In use", "off"
        else:
            status, color = "Available", "normal"

        st.metric(
            label=driver["name"],
            value=f"{capacity} lbs capacity",
            delta=f"{driver['avail_start']} – {driver['avail_end']}"
        )
        st.progress(pct, text=f"{load}/{capacity} lbs loaded")

st.divider()

# ── Pantry status table ────────────────────────────────────────
st.subheader(f"Pantries open on {day}")
st.caption(f"{len(pantries)} locations active today")

now = datetime.now()

for pantry in pantries:
    col_name, col_hours, col_address, col_status = st.columns([3, 2, 3, 1])

    close_dt = datetime.strptime(f"2026-04-25 {pantry['close']}", "%Y-%m-%d %H:%M")
    mins_left = (close_dt - now).total_seconds() / 60

    col_name.markdown(f"**{pantry['name']}**")
    col_hours.write(f"{pantry['open']} – {pantry['close']}")
    col_address.write(pantry.get("address", "Ithaca, NY"))

    if mins_left < 0:
        col_status.error("Closed")
    elif mins_left < 30:
        col_status.error("Closing")
    elif mins_left < 60:
        col_status.warning("Soon")
    else:
        col_status.success("Open")

st.divider()

# ── Partner organizations ──────────────────────────────────────
st.subheader("FDN partner organizations")
st.caption("Community programs in the Ithaca network")

p_cols = st.columns(3)
for i, partner in enumerate(partners):
    with p_cols[i % 3]:
        st.markdown(f"""
        <div style="border:0.5px solid rgba(128,128,128,0.2);
                    border-radius:10px;padding:12px;margin-bottom:10px;">
            <div style="font-weight:600;font-size:13px;
                        margin-bottom:4px;">{partner['name']}</div>
            <div style="font-size:12px;color:gray;">
                {partner.get('type','').title()}
            </div>
        </div>
        """, unsafe_allow_html=True)

st.divider()

# ── System summary ─────────────────────────────────────────────
st.subheader("System summary")

m1, m2, m3, m4 = st.columns(4)
m1.metric("Active drivers", len(drivers))
m2.metric("Pantries open today", len(pantries))
m3.metric("Total capacity", f"{sum(d['capacity'] for d in drivers)} lbs")
m4.metric("Partner orgs", len(partners))
import streamlit as st
from dotenv import load_dotenv

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
    page_title="FDN Route Optimizer",
    page_icon="🥦",
    layout="wide"
)

# ── Header ─────────────────────────────────────────────────────
col_logo, col_nav = st.columns([1, 3])
with col_logo:
    st.markdown("### 🥦 FDN Route Optimizer")

st.divider()

# ── Hero ───────────────────────────────────────────────────────
st.markdown("""
<div style="text-align:center;padding:2.5rem 0 2rem;">
    <div style="display:inline-block;font-size:12px;font-weight:600;
                padding:4px 14px;border-radius:20px;
                background:#e6f4ea;color:#1a7a2e;margin-bottom:16px;">
        Cornell Claude Builders Club Hackathon 2026
    </div>
    <h1 style="font-size:2.4rem;font-weight:600;
               margin-bottom:12px;line-height:1.2;">
        Rescuing food. Reducing hunger.
    </h1>
    <p style="font-size:1.1rem;color:gray;max-width:560px;
              margin:0 auto 2rem;line-height:1.6;">
        AI-powered logistics for Friendship Donations Network —
        matching surplus food to the people who need it, faster.
    </p>
</div>
""", unsafe_allow_html=True)

# ── Impact stats ───────────────────────────────────────────────
c1, c2, c3, c4 = st.columns(4)
c1.metric("People served", "2,000+", "weekly")
c2.metric("Food rescued", "1,400 lbs", "daily")
c3.metric("Volunteers", "200", "active")
c4.metric("Partner programs", "50+", "across Ithaca")

st.divider()

# ── Navigation cards ───────────────────────────────────────────
st.subheader("Where would you like to go?")
st.caption("Use the sidebar or click a card below")

left, right = st.columns(2)

with left:
    st.markdown("""
    <div style="border:0.5px solid rgba(128,128,128,0.25);
                border-radius:12px;padding:24px;height:100%;">
        <div style="font-size:28px;margin-bottom:12px;">📋</div>
        <div style="font-size:18px;font-weight:600;
                    margin-bottom:8px;">Available resources</div>
        <div style="font-size:14px;color:gray;line-height:1.6;
                    margin-bottom:16px;">
            View all active drivers, pantries open today,
            capacity status, and current load across the network.
        </div>
    </div>
    """, unsafe_allow_html=True)
    if st.button("View resources →", use_container_width=True):
        st.switch_page("pages/1_Resources.py")

with right:
    st.markdown("""
    <div style="border:2px solid #2d7a3a;
                border-radius:12px;padding:24px;height:100%;">
        <div style="font-size:28px;margin-bottom:12px;">🗺️</div>
        <div style="font-size:18px;font-weight:600;
                    margin-bottom:8px;">Route optimizer</div>
        <div style="font-size:14px;color:gray;line-height:1.6;
                    margin-bottom:16px;">
            Describe today's donations, select active pantries,
            and generate optimized driver routes in seconds.
        </div>
    </div>
    """, unsafe_allow_html=True)
    if st.button("Run optimizer →", use_container_width=True, type="primary"):
        st.switch_page("pages/2_Optimizer.py")

st.divider()

# ── How it works ───────────────────────────────────────────────
st.subheader("How it works")

s1, s2, s3, s4 = st.columns(4)
with s1:
    st.markdown("**1. Describe donations**")
    st.caption("Type or paste today's food donations in plain English. Claude parses them automatically.")
with s2:
    st.markdown("**2. Select pantries**")
    st.caption("Choose which partner pantries are active today. Time windows load automatically.")
with s3:
    st.markdown("**3. Optimize routes**")
    st.caption("Our VRPTW heuristic assigns donations to drivers, respecting all time and capacity constraints.")
with s4:
    st.markdown("**4. Brief your drivers**")
    st.caption("Claude generates a plain-English briefing for each driver. The map shows their routes.")

st.divider()
st.caption("Friendship Donations Network · Ithaca, NY · Built with Claude API + VRPTW optimization")
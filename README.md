# FDN Route Optimizer

**2026 Cornell Claude Builders Club Hackathon — Social Impact Track**

---

## What it does

FDN Route Optimizer is an AI-powered logistics coordinator built for Friendship Donations Network, a food rescue nonprofit in Ithaca, NY. FDN rescues fresh food from stores and farms that would otherwise be thrown away and redistributes it to neighbors in need — serving 2,000+ people per week with just 200 volunteers and one part-time staff member.

The tool solves the core daily coordination problem: given a set of food donations, a set of partner pantries with time windows, and a set of volunteer drivers with availability and capacity constraints, find the optimal assignment of donations to drivers to pantries that minimizes total travel time while respecting all constraints.

---

## The ORIE formulation

This project frames the logistics problem as a **Vehicle Routing Problem with Time Windows (VRPTW)**, a classical problem in combinatorial optimization.

**Decision variables:**
- `x_ijk = 1` if driver k travels from stop i to stop j
- `t_ik` = arrival time of driver k at stop i

**Objective:** Minimize total distance traveled plus a weighted penalty for undelivered high-urgency food

**Constraints:**
- Time windows: arrival must be within pantry open hours
- Volunteer availability: arrival within driver's available window
- Capacity: total load per driver ≤ vehicle capacity in lbs
- Perishability: delivery must occur before item expiry

**Solution method:** Greedy insertion heuristic with Earliest Deadline First (EDF) priority ordering — appropriate for the problem scale and provably near-optimal for small instances.

---

## Features

- Natural language donation input parsed by Claude API
- Spreadsheet upload with downloadable template for coordinators who prefer structured input
- VRPTW greedy heuristic optimizer with EDF priority ordering
- Real travel time matrix via OpenRouteService API
- Road-following route visualization on an interactive Folium map
- Before/after comparison: optimized routes vs naive sequential assignment
- Claude-generated plain-English driver briefing
- Resource dashboard showing driver capacity, pantry status, and unroutable donation explanations
- Multi-page Streamlit app: Home, Resources, and Optimizer

---

## Tech stack

| Layer | Tool |
|---|---|
| AI reasoning | Claude API (claude-sonnet-4) |
| Optimization | Python — greedy EDF insertion heuristic |
| Travel times | OpenRouteService API |
| Map rendering | Folium + streamlit-folium |
| Frontend | Streamlit |
| Data | CSV-backed pantry and partner data |
| Deployment | Streamlit Community Cloud |

---

## Project structure

```
fdn_optimizer/
  ├── Home.py                    # Entry point and home page
  ├── pages/
  │   ├── 1_Resources.py         # Driver and pantry availability dashboard
  │   └── 2_Optimizer.py         # Main optimizer interface
  ├── engine/
  │   ├── __init__.py
  │   ├── build_time_matrix.py   # OpenRouteService matrix API call
  │   ├── sort_edf.py            # Earliest Deadline First sort
  │   ├── feasibility.py         # VRPTW constraint checker
  │   └── optimizer.py           # Greedy insertion heuristic
  ├── data/
  │   ├── load_data.py           # CSV loader with day filtering
  │   ├── pantries.csv           # Real FDN partner pantry locations and hours
  │   └── fdn_partners.csv       # FDN partner organizations
  ├── map_utils.py               # Folium map builder with road-following routes
  ├── dashboard.py               # Resource status dashboard
  ├── claude_utils.py            # Claude API prompts (parser + narrator)
  ├── naive_optimizer.py         # Naive baseline for before/after comparison
  ├── spreadsheet_utils.py       # Template generator and spreadsheet parser
  ├── styles.py                  # Shared Streamlit CSS
  └── .env                       # API keys (not committed)
```

---

## Setup

**1. Clone the repo**
```bash
git clone https://github.com/YOUR_USERNAME/fdn-optimizer.git
cd fdn-optimizer
```

**2. Create and activate a conda environment**
```bash
conda create -n fdn-optimizer python=3.11
conda activate fdn-optimizer
```

**3. Install dependencies**
```bash
pip install streamlit anthropic requests folium streamlit-folium python-dotenv pandas
```

**4. Add your API keys**

Create a `.env` file in the project root:
```
ANTHROPIC_API_KEY=your_key_here
ORS_API_KEY=your_key_here
```

Get a Claude API key at console.anthropic.com and a free OpenRouteService key at openrouteservice.org.

**5. Run the app**
```bash
streamlit run Home.py
```

---

## How to use

1. Open the app and navigate to **Route Optimizer** from the home page
2. Select the day of the week to load active pantries and the time of day you want to simulate
3. Type a plain-English description of today's donations
5. Click **Optimize Routes**
6. View the route map, driver briefing, resource dashboard, and before/after metrics

---

## Real Ithaca data

Pantry locations, addresses, and time windows are sourced directly from the FDN partner program schedule at friendshipdonations.org/programs. The optimization runs against real coordinates and real open/close times for Tompkins County pantries.

---

## Team

Built by Tanushree Pal and AJ Orantia at the 2026 Cornell Claude Builders Club Hackathon.

*Friendship Donations Network · Ithaca, NY · friendshipdonations.org*

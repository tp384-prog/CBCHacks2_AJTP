import folium
import requests
import os
from dotenv import load_dotenv

load_dotenv()

DRIVER_COLORS = ["blue", "purple", "orange", "red", "green", "darkblue"]


def get_road_route(origin, destination):
    """Returns a list of [lat, lng] points following actual roads via ORS"""
    try:
        response = requests.get(
            "https://api.openrouteservice.org/v2/directions/driving-car",
            headers={"Authorization": os.getenv("ORS_API_KEY")},
            params={
                "start": f"{origin[1]},{origin[0]}",        # ORS expects lng,lat
                "end": f"{destination[1]},{destination[0]}"
            }
        )
        data = response.json()
        coords = data["features"][0]["geometry"]["coordinates"]
        return [[c[1], c[0]] for c in coords]  # flip to [lat, lng] for Folium
    except Exception as e:
        print(f"ORS route error: {e} — falling back to straight line")
        return [origin, destination]  # fallback to straight line if API fails


def build_map(assignments, donations, pantries):
    """
    Builds a Folium map centered on Ithaca.
    - Red markers for donation pickup locations
    - Green markers for pantry dropoff locations
    - Colored polylines per driver following real road routes
    """
    m = folium.Map(location=[42.4440, -76.5019], zoom_start=13)

    # Add donor markers (red)
    for donation in donations:
        folium.Marker(
            location=donation["location"],
            popup=folium.Popup(
                f"<b>{donation['item']}</b><br>"
                f"Quantity: {donation['quantity']} lbs<br>"
                f"Expires: {donation['expiry']}",
                max_width=200
            ),
            icon=folium.Icon(color="red", icon="info-sign"),
            tooltip=f"Pickup: {donation['item']}"
        ).add_to(m)

    # Add pantry markers (green)
    for pantry in pantries:
        pantry_loc = [pantry["lat"], pantry["lng"]]
        folium.Marker(
            location=pantry_loc,
            popup=folium.Popup(
                f"<b>{pantry['name']}</b><br>"
                f"Open: {pantry['open']} — {pantry['close']}",
                max_width=200
            ),
            icon=folium.Icon(color="green", icon="home"),
            tooltip=f"Pantry: {pantry['name']}"
        ).add_to(m)

    # Group assignments by driver name
    driver_routes = {}
    for a in assignments:
        driver_name = a["driver"]["name"]
        if driver_name not in driver_routes:
            driver_routes[driver_name] = []
        driver_routes[driver_name].append(a)

    # Draw a road-following polyline per driver
    for idx, (driver_name, route) in enumerate(driver_routes.items()):
        color = DRIVER_COLORS[idx % len(DRIVER_COLORS)]

        for stop in route:
            donation_loc = stop["donation"]["location"]
            pantry_loc   = [stop["pantry"]["lat"], stop["pantry"]["lng"]]

            # Numbered stop marker at the pantry
            folium.Marker(
                location=pantry_loc,
                popup=folium.Popup(
                    f"<b>{driver_name}</b><br>"
                    f"Delivering: {stop['donation']['item']}<br>"
                    f"Quantity: {stop['donation']['quantity']} lbs<br>"
                    f"Travel time: {stop['travel_time_min']} min",
                    max_width=200
                ),
                icon=folium.DivIcon(
                    html=f'<div style="background:{color};color:white;'
                         f'border-radius:50%;width:24px;height:24px;'
                         f'display:flex;align-items:center;justify-content:center;'
                         f'font-size:12px;font-weight:bold;">{idx+1}</div>',
                    icon_size=(24, 24),
                    icon_anchor=(12, 12)
                )
            ).add_to(m)

            # Get real road route from ORS
            road_coords = get_road_route(donation_loc, pantry_loc)
            folium.PolyLine(
                locations=road_coords,
                color=color,
                weight=4,
                opacity=0.8,
                tooltip=f"{driver_name} route"
            ).add_to(m)

    # Legend
    legend_html = """
    <div style="position:fixed;bottom:30px;left:30px;z-index:1000;
                background:white;padding:10px 14px;border-radius:8px;
                border:1px solid #ccc;font-size:13px;line-height:1.8">
        <b>FDN Route Optimizer</b><br>
        <span style="color:red">&#9679;</span> Donation pickup<br>
        <span style="color:green">&#9679;</span> Pantry dropoff<br>
        <span style="color:blue">&#9644;</span> Driver routes
    </div>
    """
    m.get_root().html.add_child(folium.Element(legend_html))

    return m


if __name__ == "__main__":
    from data.load_data import load_pantries, load_donations, load_drivers

    donations = load_donations()
    pantries  = load_pantries("Saturday")
    drivers   = load_drivers()

    mock_assignments = [
        {
            "driver":          drivers[0],
            "donation":        donations[0],
            "pantry":          pantries[0],
            "travel_time_min": 2.0
        },
        {
            "driver":          drivers[1],
            "donation":        donations[1],
            "pantry":          pantries[0],
            "travel_time_min": 4.0
        },
    ]

    m = build_map(mock_assignments, donations, pantries)
    m.save("test_map.html")
    print("Map saved to test_map.html — open it in your browser")
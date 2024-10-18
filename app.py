import pandas as pd
import folium
import streamlit as st
from folium import Popup
from io import BytesIO
from itertools import cycle

st.title("Client and Hub Location Map")

# Create a sample Excel file for users to download
def create_sample_file():
    # Sample client data
    client_data = pd.DataFrame({
        'CLIENT WAREHOUSE CODE': ['C001', 'C002', 'C003', 'C004'],
        'CENTER NAME': ['Center A', 'Center B', 'Center C', 'Center D'],
        'CENTER TYPE': ['Type A', 'Type B', 'Type C', 'Type D'],
        'LATITUDE': [12.9716, 12.2958, 13.0827, 13.6288],
        'LONGITUDE': [77.5946, 76.6394, 80.2707, 79.4192],
        'Hub Name': ['Route 1', 'Route 2', 'Route 1', ''],
        'Rider Name': ['Rider A', 'Rider B', 'Rider A', 'Rider C'],
        'Round1': ['08:00 AM', '08:30 AM', '09:00 AM', '09:30 AM'],
        'Round2': ['12:00 PM', '12:30 PM', '01:00 PM', '01:30 PM'],
        'Round3': ['04:00 PM', '04:30 PM', '05:00 PM', '05:30 PM']
    })

    # Sample hub data
    hub_data = pd.DataFrame({
        'Name': ['Hub 1', 'Hub 2'],
        'Lat': [12.9716, 12.2958],
        'Long': [77.5946, 76.6394]
    })

    # Create an Excel writer object
    output = BytesIO()
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        client_data.to_excel(writer, sheet_name='ClientSheet', index=False)
        hub_data.to_excel(writer, sheet_name='HubSheet', index=False)
    
    return output.getvalue()

# Provide download option for the sample Excel file
st.download_button(
    label="Download Sample Excel File",
    data=create_sample_file(),
    file_name="sample_client_hub_data.xlsx",
    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
)

# File uploader for the actual data
uploaded_file = st.file_uploader("Choose an Excel file", type=["xlsx"])

if uploaded_file is not None:
    client_data = pd.read_excel(uploaded_file, sheet_name='ClientSheet')
    hub_data = pd.read_excel(uploaded_file, sheet_name='HubSheet')

    # Create map centered around the average latitude and longitude
    map_center = [client_data['LATITUDE'].mean(), client_data['LONGITUDE'].mean()]
    mymap = folium.Map(location=map_center, zoom_start=12)

    # Predefined color palette (20 colors for 20 routes)
    color_palette = cycle([
        'beige', 'darkblue', 'darkgreen', 'cadetblue', 'pink', 'lightblue','red', 'blue', 'green', 'purple', 'orange', 'darkred', 'lightred', 
        'beige', 'darkblue', 'darkgreen', 'cadetblue', 'pink', 'lightblue', 
        'lightgreen', 'gray', 'black', 'lightgray', 'darkpurple', 'darkorange', 'lightyellow'
    ])

    # Map each unique route to a color
    unique_routes = client_data['ROUTE'].dropna().unique()
    route_colors = {route: next(color_palette) for route in unique_routes}

    # Add markers for client data and store coordinates by route
    route_coordinates = {}
    for _, row in client_data.iterrows():
        route = row['ROUTE']
        
        # Assign color based on route; default to gray for empty routes
        color = route_colors.get(route, 'gray')  

        # Updated popup content to include the new columns
        popup_content = f"""
            <b>CLIENT WAREHOUSE CODE:</b> {row['CLIENT WAREHOUSE CODE']}<br>
            <b>CENTER NAME:</b> {row['CENTER NAME']}<br>
            <b>Hub Name:</b> {row['ROUTE'] if route else 'No Route'}<br>
        """
        popup = Popup(popup_content, max_width=300)
        folium.Marker(
            location=[row['LATITUDE'], row['LONGITUDE']],
            popup=popup,
            icon=folium.Icon(color=color, icon='info-sign')
        ).add_to(mymap)

        # Add coordinates to route list if 'ROUTE' is not empty
        if route and not pd.isna(route):
            if route not in route_coordinates:
                route_coordinates[route] = []
            route_coordinates[route].append([row['LATITUDE'], row['LONGITUDE']])

    # Draw lines connecting clients in the same route
   # for route, coordinates in route_coordinates.items():
        # Only draw lines for routes with more than one point
    #    if len(coordinates) > 1:
     #       folium.PolyLine(
      #          locations=coordinates, 
       #         color=route_colors[route], 
        #        weight=5, 
         #       opacity=0.8
          #  ).add_to(mymap)

    # Add markers for hub data
    for _, row in hub_data.iterrows():
        popup_content = f"""
            LAB NAME: {row['Name']}<br>
            LATITUDE: {row['Lat']}<br>
            LONGITUDE: {row['Long']}
        """
        popup = Popup(popup_content, max_width=300)
        folium.Marker(
            location=[row['Lat'], row['Long']],
            popup=popup,
            icon=folium.Icon(color='red', icon='star', icon_color='white')
        ).add_to(mymap)

    # Save the map to BytesIO for downloading
    map_data = BytesIO()
    mymap.save(map_data, close_file=False)
    st.components.v1.html(map_data.getvalue().decode(), height=600)

    # Provide option to download the map
    st.download_button(label="Download Map as HTML", data=map_data.getvalue(), file_name="client_hub_map.html")
else:
    st.write("Please upload an Excel file.")

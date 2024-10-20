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
        'Hub Name': ['Hub 1', 'Hub 2', 'Hub 1', 'Hub 3']
    })

    # Sample hub data
    hub_data = pd.DataFrame({
        'Name': ['Hub 1', 'Hub 2', 'Hub 3', 'Hub 4'],
        'Lat': [12.9716, 12.2958, 13.0827, 13.6288],
        'Long': [77.5946, 76.6394, 80.2707, 79.4192]
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
    mymap = folium.Map(location=map_center, zoom_start=10)

    # Predefined color palette for hubs (cycling through a fixed set of colors)
    color_palette = cycle(['blue', 'green', 'purple', 'orange', 'darkred', 'cadetblue', 'lightgreen'])

    # Map each Hub Name to a color
    unique_hubs = client_data['Hub Name'].dropna().unique()
    hub_colors = {hub: next(color_palette) for hub in unique_hubs}

    # Add markers for client data with unique color based on Hub Name
    for _, row in client_data.iterrows():
        hub_name = row['Hub Name']
        color = hub_colors.get(hub_name, 'gray')  # Default to gray if Hub Name is missing
        
        popup_content = f"""
            <b>CLIENT WAREHOUSE CODE:</b> {row['CLIENT WAREHOUSE CODE']}<br>
            <b>CENTER NAME:</b> {row['CENTER NAME']}<br>
            <b>Hub Name:</b> {hub_name if hub_name else 'No Hub Assigned'}<br>
        """
        popup = Popup(popup_content, max_width=300)
        folium.Marker(
            location=[row['LATITUDE'], row['LONGITUDE']],
            popup=popup,
            icon=folium.Icon(color=color, icon='info-sign')
        ).add_to(mymap)

    # Add markers for hub data (keeping these as red star icons for distinction)
    for _, row in hub_data.iterrows():
        popup_content = f"""
            <b>LAB NAME:</b> {row['Name']}<br>
            <b>LATITUDE:</b> {row['Lat']}<br>
            <b>LONGITUDE:</b> {row['Long']}
        """
        popup = Popup(popup_content, max_width=300)
        folium.Marker(
            location=[row['Lat'], row['Long']],
            popup=popup,
            icon=folium.Icon(color='red', icon='star', icon_color='white')
        ).add_to(mymap)

    # Select a central hub (e.g., Hub 1 is the central hub)
    central_hub = hub_data.iloc[0]  # Assuming "Hub 1" is the first
    central_location = [central_hub['Lat'], central_hub['Long']]

    # Assuming central hub is the first row in the hub_data
central_hub = hub_data.iloc[0]  # First hub in the HubSheet
central_location = [central_hub['Lat'], central_hub['Long']]

# Draw lines from each client location to the central hub
for _, client_row in client_data.iterrows():
    client_location = [client_row['LATITUDE'], client_row['LONGITUDE']]
    folium.PolyLine(
        locations=[client_location, central_location],
        color="blue",
        weight=3,
        opacity=0.6
    ).add_to(mymap)

# Now, draw lines from the first hub to the next and so on (sequentially)
previous_hub_location = central_location  # Start with the first hub
for _, hub_row in hub_data.iterrows():
    current_hub_location = [hub_row['Lat'], hub_row['Long']]
    
    if current_hub_location != previous_hub_location:  # Skip if it's the same hub
        folium.PolyLine(
            locations=[previous_hub_location, current_hub_location],
            color="green",
            weight=5,
            opacity=0.8
        ).add_to(mymap)
    
    previous_hub_location = current_hub_location  # Move to the next hub


    # Save the map to BytesIO for downloading
    map_data = BytesIO()
    mymap.save(map_data, close_file=False)
    st.components.v1.html(map_data.getvalue().decode(), height=600)

    # Provide option to download the map
    st.download_button(label="Download Map as HTML", data=map_data.getvalue(), file_name="client_hub_map.html")
else:
    st.write("Please upload an Excel file.")

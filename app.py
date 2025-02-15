import pandas as pd
import folium
import streamlit as st
from io import BytesIO
from itertools import cycle

st.title("Client and Hub Connection Map")

# Function to create a sample Excel file
def create_sample_file():
    client_data = pd.DataFrame({
        'CLIENT WAREHOUSE CODE': ['C001', 'C002', 'C003', 'C004'],
        'CENTER NAME': ['Center A', 'Center B', 'Center C', 'Center D'],
        'LATITUDE': [12.9716, 12.2958, 13.0827, 13.6288],
        'LONGITUDE': [77.5946, 76.6394, 80.2707, 79.4192],
        'Hub Name': ['Hub 1', 'Hub 2', 'Hub 1', 'Hub 3']
    })

    hub_data = pd.DataFrame({
        'Name': ['Hub 1', 'Hub 2', 'Hub 3'],
        'Lat': [12.9722, 12.3000, 13.6000],
        'Long': [77.5950, 76.6400, 79.4200]
    })

    output = BytesIO()
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        client_data.to_excel(writer, sheet_name='ClientSheet', index=False)
        hub_data.to_excel(writer, sheet_name='HubSheet', index=False)
    
    return output.getvalue()

# Sample Excel download
st.download_button(
    label="Download Sample Excel File",
    data=create_sample_file(),
    file_name="sample_client_hub_data.xlsx",
    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
)

# File uploader
uploaded_file = st.file_uploader("Upload an Excel file", type=["xlsx"])

if uploaded_file is not None:
    client_data = pd.read_excel(uploaded_file, sheet_name='ClientSheet')
    hub_data = pd.read_excel(uploaded_file, sheet_name='HubSheet')

    # Remove extra spaces to avoid mismatches
    client_data['Hub Name'] = client_data['Hub Name'].astype(str).str.strip()
    hub_data['Name'] = hub_data['Name'].astype(str).str.strip()

    # Create a base map centered on the data
    map_center = [client_data['LATITUDE'].mean(), client_data['LONGITUDE'].mean()]
    mymap = folium.Map(location=map_center, zoom_start=8)

    # Assign unique colors to hubs
    color_palette = cycle(['blue', 'green', 'purple', 'orange', 'darkred', 'cadetblue'])
    hub_colors = {hub: next(color_palette) for hub in hub_data['Name'].unique()}

    # Plot client warehouse locations
    for _, row in client_data.iterrows():
        folium.Marker(
            location=[row['LATITUDE'], row['LONGITUDE']],
            popup=f"<b>Client:</b> {row['CLIENT WAREHOUSE CODE']}<br><b>Hub:</b> {row['Hub Name']}",
            icon=folium.Icon(color='blue', icon='info-sign')
        ).add_to(mymap)

    # Plot hub locations
    for _, row in hub_data.iterrows():
        folium.Marker(
            location=[row['Lat'], row['Long']],
            popup=f"<b>Hub:</b> {row['Name']}",
            icon=folium.Icon(color='red', icon='star', icon_color='white')
        ).add_to(mymap)

    # Draw lines from each CLIENT to its assigned HUB
    for _, client_row in client_data.iterrows():
        hub_name = client_row['Hub Name']
        hub_row = hub_data[hub_data['Name'] == hub_name]

        if not hub_row.empty:
            hub_row = hub_row.iloc[0]  # Get the corresponding hub
            folium.PolyLine(
                locations=[
                    [client_row['LATITUDE'], client_row['LONGITUDE']],  # Client location
                    [hub_row['Lat'], hub_row['Long']]  # Assigned hub location
                ],
                color=hub_colors.get(hub_name, 'black'), 
                weight=3,
                opacity=0.6
            ).add_to(mymap)
        else:
            st.write(f"⚠️ Warning: No matching hub found for {client_row['CLIENT WAREHOUSE CODE']} (Hub: {hub_name})")

    # Display the map in Streamlit
    map_data = BytesIO()
    mymap.save(map_data, close_file=False)
    st.components.v1.html(map_data.getvalue().decode(), height=600)

    # Allow map download
    st.download_button(label="Download Map as HTML", data=map_data.getvalue(), file_name="client_hub_map.html")
else:
    st.write("Please upload an Excel file.")

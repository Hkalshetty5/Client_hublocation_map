import pandas as pd
import folium
import streamlit as st
from io import BytesIO

st.title("Client and Hub Location Map")

# Function to create a sample Excel file
def create_sample_file():
    client_data = pd.DataFrame({
        'CLIENT WAREHOUSE CODE': ['C001', 'C002', 'C003', 'C004'],
        'CENTER NAME': ['Center A', 'Center B', 'Center C', 'Center D'],
        'LATITUDE': [12.9716, 12.2958, 13.0827, 13.6288],
        'LONGITUDE': [77.5946, 76.6394, 80.2707, 79.4192],
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

    # Create a base map centered on the average location
    map_center = [
        pd.concat([client_data['LATITUDE'], hub_data['Lat']]).mean(),
        pd.concat([client_data['LONGITUDE'], hub_data['Long']]).mean()
    ]
    mymap = folium.Map(location=map_center, zoom_start=7)

    # Plot client locations
    for _, row in client_data.iterrows():
        folium.Marker(
            location=[row['LATITUDE'], row['LONGITUDE']],
            popup=f"<b>Client:</b> {row['CLIENT WAREHOUSE CODE']}<br><b>Center:</b> {row['CENTER NAME']}",
            icon=folium.Icon(color='blue', icon='home')
        ).add_to(mymap)

    # Plot hub locations
    for _, row in hub_data.iterrows():
        folium.Marker(
            location=[row['Lat'], row['Long']],
            popup=f"<b>Hub:</b> {row['Name']}",
            icon=folium.Icon(color='red', icon='star')
        ).add_to(mymap)

    # Display the map
    map_data = BytesIO()
    mymap.save(map_data, close_file=False)
    st.components.v1.html(map_data.getvalue().decode(), height=600)

    # Optionally: Download map as HTML
    st.download_button("Download Map as HTML", data=map_data.getvalue(), file_name="client_hub_map.html")
else:
    st.write("📂 Please upload an Excel file with 'ClientSheet' and 'HubSheet'.")

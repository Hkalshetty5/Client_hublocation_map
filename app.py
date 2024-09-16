import pandas as pd
import folium
import streamlit as st
from folium import Popup
from io import BytesIO

st.title("Client and Hub Location Map")

# Create a sample Excel file for users to download
def create_sample_file():
    # Sample client data
    client_data = pd.DataFrame({
        'CLIENT WAREHOUSE CODE': ['C001', 'C002'],
        'CENTER NAME': ['Center A', 'Center B'],
        'CENTER TYPE': ['Type A', 'Type B'],
        'LATITUDE': [12.9716, 12.2958],
        'LONGITUDE': [77.5946, 76.6394]
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

    # Add markers for client data
    for _, row in client_data.iterrows():
        popup_content = f"""
            CLIENT WAREHOUSE CODE: {row['CLIENT WAREHOUSE CODE']}<br>
            CENTER NAME: {row['CENTER NAME']}<br>
            CENTER TYPE: {row['CENTER TYPE']}
        """
        popup = Popup(popup_content, max_width=300)
        folium.Marker(
            location=[row['LATITUDE'], row['LONGITUDE']],
            popup=popup,
            icon=folium.Icon(color='blue', icon='info-sign')
        ).add_to(mymap)

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

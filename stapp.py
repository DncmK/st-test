import folium
import streamlit as st

from streamlit_folium import st_folium

# import pickle
from pathlib import Path
import streamlit_authenticator as stauth

# setting header, description and citation
st.set_page_config(page_title="Buildings Evaluation!")

# --- User Authentication ---
names = ["Admin", "Dennis"]
usernames = ["admin", "dennis"]
passwords = ['abc123','abc456']

credentials = {"usernames":{}}
		  
for uname,name,pwd in zip(usernames,names,passwords):
	 user_dict = {"name": name, "password": pwd}
	 credentials["usernames"].update({uname: user_dict})

# file_path = Path(__file__).parent / "hashed_pw.pkl"
# with file_path.open("rb") as file:
#    hashed_passwords = pickle.load(file)

authenticator = stauth.Authenticate(credentials, "users_dashboard", "abcdef", cookie_expiry_days=0)

def upload_setting_button():
	 """Allow to upload setting"""
	 st.session_state['upload_setting'] = True
	 return


st.header('''
Buildings Evaluation!
''')
st.write('''
List a building to be evaluated by our team.
''')
# st.markdown('''
# For more options and information, check out our documentation
#    ''')
st.markdown("""
		  <style>
					.block-container {
						  padding-top: 5rem;
						  padding-bottom: 0rem;
						  padding-left: 0rem;
						  padding-right: 0rem;
					 }
		  </style>
		  """, unsafe_allow_html=True)

# select the input type
# input_location = st.selectbox("Select Location :", [' ', 'Manually', 'Automatically'], help="""Just a helping explanation of what is going to be on this input.""")

# if input_location == "Manually" or input_location == "Automatically":
m = folium.Map(location=[40.257280, 22.510743], zoom_start=16)
folium.Marker(
	[40.257280, 22.510743], popup="Liberty Bell", tooltip="Liberty Bell"
).add_to(m)


st_data = st_folium(m, width=725, height=330)

input_type = st.selectbox("Type of use :", ['Residential', 'Industrial', 'Concentrated audience', 'Public Building', 'Emergency Buildig'], help="""Just a helping explanation of what is going to be on this input.""")

input_users_number = st.selectbox("Number of users :", ['0-10', '11-100', '100+'], help="""Just a helping explanation of what is going to be on this input.""")

input_importance_category = st.selectbox("Building importance category :", ['Σ1', 'Σ2', 'Σ3', 'Σ4'], help="""Just a helping explanation of what is going to be on this input.""")

input_danger = st.selectbox("Danger of non structural element falling :", ['No', 'Yes (Provide Photo)'], help="""Just a helping explanation of what is going to be on this input.""")

if input_danger == "Yes (Provide Photo)":
	saved_setting = st.file_uploader("Upload previous settings (optional):", on_change=upload_setting_button,
													  type='jpg',
													  help='''If you have saved a "molecule_icon_settings.json" file, you can upload it 
																 and use the same settings. You can save the settings with the button at the 
																 end of the page''', key="1")

# input_importance_category = st.selectbox("Number of floors :", ['Σ1', 'Σ2', 'Σ3', 'Σ4'], help="""Just a helping explanation of what is going to be on this input.""")

input_floor_number = st.number_input("Number of floors :", 0, 10, help="""Just a helping explanation of what is going to be on this input.""")

if input_floor_number:
	saved_setting2 = st.file_uploader("Upload previous settings (optional):", on_change=upload_setting_button,
													  type='jpg',
													  help='''If you have saved a "molecule_icon_settings.json" file, you can upload it 
																 and use the same settings. You can save the settings with the button at the 
																 end of the page''', key="2")

input_condition = st.selectbox("Condition of structure :", ['No', 'Rust/Spalling (Provide Photo)'], help="""Just a helping explanation of what is going to be on this input.""")

if input_condition == "Rust/Spalling (Provide Photo)":
	saved_setting3 = st.file_uploader("Upload previous settings (optional):", on_change=upload_setting_button,
													  type='jpg',
													  help='''If you have saved a "molecule_icon_settings.json" file, you can upload it 
																 and use the same settings. You can save the settings with the button at the 
																 end of the page''', key="3")

# input_importance_category = st.selectbox("Year of construction :", ['Σ1', 'Σ2', 'Σ3', 'Σ4'], help="""Just a helping explanation of what is going to be on this input.""")

input_construction_year = st.number_input("Year of construction :", 1920, 2024)

input_previous_damages = st.selectbox("Previous damages in vertical elements :", ['No', 'Yes (Provide Photo)'], help="""Just a helping explanation of what is going to be on this input.""")

input_danger = st.selectbox("Danger of impact with neighboring buildings :", ['No', 'Yes (Provide Photo)'], help="""Just a helping explanation of what is going to be on this input.""")

if input_danger == "Yes (Provide Photo)":
	saved_setting4 = st.file_uploader("Upload previous settings (optional):", on_change=upload_setting_button,
													  type='jpg',
													  help='''If you have saved a "molecule_icon_settings.json" file, you can upload it 
																 and use the same settings. You can save the settings with the button at the 
																 end of the page''', key="4")

input_soft_floor = st.selectbox("Soft floor (pilotis) :", ['No', 'Yes (Provide Photo)'], help="""Just a helping explanation of what is going to be on this input.""")

if input_soft_floor == "Yes (Provide Photo)":
	saved_setting5 = st.file_uploader("Upload previous settings (optional):", on_change=upload_setting_button,
													  type='jpg',
													  help='''If you have saved a "molecule_icon_settings.json" file, you can upload it 
																 and use the same settings. You can save the settings with the button at the 
																 end of the page''', key="5")

input_sot_column = st.selectbox("Sort column :", ['No', 'Yes (Provide Photo)'], help="""Just a helping explanation of what is going to be on this input.""")

if input_sot_column == "Yes (Provide Photo)":
	saved_setting6 = st.file_uploader("Upload previous settings (optional):", on_change=upload_setting_button,
													  type='jpg',
													  help='''If you have saved a "molecule_icon_settings.json" file, you can upload it 
																 and use the same settings. You can save the settings with the button at the 
																 end of the page''', key="6")

st.button("Send Data")



# col1, col2, col3 = st.beta_columns(3)
# col2.button('Send Data')



# center on Liberty Bell, add marker
# m = folium.Map(location=[40.257280, 22.510743], zoom_start=16)
# folium.Marker(
#     [40.257280, 22.510743], popup="Liberty Bell", tooltip="Liberty Bell"
# ).add_to(m)


# call to render Folium map in Streamlit
# st_data = st_folium(m, width=725)

name, authentication_status, username = authenticator.login("sidebar")

if authentication_status == False:
	st.error("Username/Password is incorrect!")

# if authentication_status == None:
#    st.warning("Please provide a username and a password!")

if authentication_status:
	st.success("Thanks for logging in!")
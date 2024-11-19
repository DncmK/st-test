import streamlit as st
import folium
from streamlit_folium import st_folium
from PIL import Image
import sqlite3
import io
from folium.plugins import LocateControl

# Initialize SQLite database
conn = sqlite3.connect('building_survey.db')
c = conn.cursor()

# Create necessary tables
c.execute('''CREATE TABLE IF NOT EXISTS survey_data (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                latitude REAL,
                longitude REAL,
                type_of_use TEXT,
                number_of_users TEXT,
                building_importance_category TEXT,
                non_structural_falling_danger TEXT,
                number_of_floors INTEGER,
                condition_of_structure TEXT,
                year_of_construction INTEGER,
                previous_damages TEXT,
                neighboring_buildings_impact TEXT,
                soft_floor TEXT,
                short_column TEXT
            )''')

c.execute('''CREATE TABLE IF NOT EXISTS survey_images (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                survey_id INTEGER,
                image_type TEXT,
                image BLOB,
                FOREIGN KEY(survey_id) REFERENCES survey_data(id)
            )''')

c.execute('''CREATE TABLE IF NOT EXISTS review_data (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                survey_id INTEGER,
                structural_system TEXT,
                arrangement_walls TEXT,
                irregular_vertical TEXT,
                irregular_vertical_photo BLOB,
                irregular_horizontal TEXT,
                irregular_horizontal_photo BLOB,
                torsion_rotation TEXT,
                torsion_rotation_photo BLOB,
                structural_vulnerabilities TEXT,
                heavy_finishes TEXT,
                heavy_finishes_photo BLOB,
                input_quality INTEGER,
                soil_class TEXT,
                load_capacity_reduction TEXT,
                constructed_area INTEGER,
                constructed_area_photo BLOB,
                structure_performance TEXT,
                retrofitting_methods TEXT,
                reviewed BOOLEAN DEFAULT FALSE
            )''')

conn.commit()

# Utility functions
def resize_image(image):
    img = Image.open(image)
    img_resized = img.resize((int(img.width * 0.2), int(img.height * 0.2)))
    buffered = io.BytesIO()
    img_resized.save(buffered, format="JPEG")
    return buffered.getvalue()

def process_uploaded_images(images, survey_id):
    for img_type, img in images.items():
        if img:
            resized_image = resize_image(img)
            c.execute('INSERT INTO survey_images (survey_id, image_type, image) VALUES (?, ?, ?)',
                      (survey_id, img_type, resized_image))
    conn.commit()

def initialize_map():
    m = folium.Map(location=[38.0, 23.7], zoom_start=6)
    LocateControl(auto_start=True).add_to(m)
    return m

def fetch_listings(reviewed):
    query = '''
        SELECT * FROM survey_data
        WHERE id NOT IN (
            SELECT survey_id FROM review_data WHERE reviewed = ?
        )
    '''
    c.execute(query, (int(reviewed),))
    return c.fetchall()

def fetch_images(survey_id):
    c.execute('SELECT image_type, image FROM survey_images WHERE survey_id = ?', (survey_id,))
    return c.fetchall()

# Admin login
def admin_login():
    st.sidebar.title("Admin Login")
    username = st.sidebar.text_input("Username")
    password = st.sidebar.text_input("Password", type="password")
    
    if st.sidebar.button("Login"):
        if username == "admin" and password == "admin":
            st.session_state.logged_in = True
            st.sidebar.success("Logged in successfully!")
        else:
            st.sidebar.error("Invalid username or password")

# Display survey form
def display_initial_form():
    st.title("Building Survey Form")

    # 1. Map for location selection
    st.header("1. Select the location on the map")
    m = initialize_map()
    location = st_folium(m, width=700, height=300)

    lat, lon = None, None
    if location.get("last_clicked"):
        lat, lon = location["last_clicked"]["lat"], location["last_clicked"]["lng"]
        st.success(f"Selected Location: Latitude {lat}, Longitude {lon}")

    # Other form fields
    type_of_use = st.selectbox("2. Type of Use", ["Residential", "Industrial", "Public Building"])
    number_of_users = st.selectbox("3. Number of Users", ["0-10", "11-100", "100+"])
    importance_category = st.selectbox("4. Building Importance Category", ["Σ1", "Σ2", "Σ3", "Σ4"])
    danger_falling = st.selectbox("5. Non-Structural Falling Danger", ["No", "Yes"])
    falling_photo = st.file_uploader("Upload photo (if applicable)", type=["jpg", "png", "jpeg"]) if danger_falling == "Yes" else None
    num_floors = st.number_input("6. Number of Floors", min_value=1, step=1)
    structure_condition = st.selectbox("7. Condition of Structure", ["Good", "Rust/Spalling"])
    structure_photo = st.file_uploader("Upload photo (if applicable)", type=["jpg", "png", "jpeg"]) if structure_condition == "Rust/Spalling" else None
    year_construction = st.number_input("8. Year of Construction", min_value=1800, max_value=2024, step=1)
    previous_damages = st.selectbox("9. Previous Damages", ["No", "Yes"])
    damage_photo = st.file_uploader("Upload photo (if applicable)", type=["jpg", "png", "jpeg"]) if previous_damages == "Yes" else None

    # CAPTCHA
    captcha_input = st.text_input("Enter CAPTCHA (type '12345')")
    captcha_valid = captcha_input == "12345"

    if st.button("Submit"):
        if captcha_valid and lat is not None and lon is not None:
            c.execute('INSERT INTO survey_data (latitude, longitude, type_of_use, number_of_users, building_importance_category, non_structural_falling_danger, number_of_floors, condition_of_structure, year_of_construction, previous_damages) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)',
                      (lat, lon, type_of_use, number_of_users, importance_category, danger_falling, num_floors, structure_condition, year_construction, previous_damages))
            survey_id = c.lastrowid

            # Process images
            images = {
                "falling_photo": falling_photo,
                "structure_photo": structure_photo,
                "damage_photo": damage_photo
            }
            process_uploaded_images(images, survey_id)

            st.success("Survey submitted successfully!")
        else:
            st.error("Please fill all required fields and pass the CAPTCHA.")

# Admin review
def display_listings():
    listings = fetch_listings(reviewed=False)
    if listings:
        st.title("Pending Reviews")
        options = [f"Listing {l[0]}: ({l[1]}, {l[2]})" for l in listings]
        selected_option = st.selectbox("Select a listing", options)
        selected_id = listings[options.index(selected_option)][0]

        st.header(f"Reviewing Listing ID: {selected_id}")
        c.execute('SELECT * FROM survey_data WHERE id = ?', (selected_id,))
        listing = c.fetchone()

        st.write(f"**Latitude:** {listing[1]}, **Longitude:** {listing[2]}")
        st.write(f"**Type of Use:** {listing[3]}")
        st.write(f"**Number of Users:** {listing[4]}")

        # Fetch and display images
        images = fetch_images(selected_id)
        for img_type, img_data in images:
            if img_data:
                img = Image.open(io.BytesIO(img_data))
                st.image(img, caption=img_type, use_column_width=True)
    else:
        st.info("No listings to review.")

# Main app logic
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

admin_login()

if st.session_state.logged_in:
    display_listings()
else:
    display_initial_form()

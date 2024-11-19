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

# Ensure `survey_data` has the correct schema
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
                reviewed BOOLEAN DEFAULT FALSE
            )''')

# Ensure `review_data` has the correct schema
c.execute('''CREATE TABLE IF NOT EXISTS review_data (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                survey_id INTEGER,
                structural_system TEXT,
                arrangement_walls TEXT,
                input_quality INTEGER,
                soil_class TEXT,
                load_capacity_reduction TEXT,
                structure_performance TEXT,
                retrofitting_methods TEXT,
                FOREIGN KEY(survey_id) REFERENCES survey_data(id)
            )''')

# Check and add missing `reviewed_at` column in `review_data`
c.execute("PRAGMA table_info(review_data)")
columns = [col[1] for col in c.fetchall()]
if "reviewed_at" not in columns:
    c.execute("ALTER TABLE review_data ADD COLUMN reviewed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP")
    conn.commit()



# Utility functions
def resize_image(image):
    img = Image.open(image)
    img_resized = img.resize((int(img.width * 0.2), int(img.height * 0.2)))
    buffered = io.BytesIO()
    img_resized.save(buffered, format="JPEG")
    return buffered.getvalue()

# Function to initialize the map and handle location selection
def initialize_map_with_marker():
    # Initialize the map
    m = folium.Map(location=[38.0, 23.7], zoom_start=6)
    LocateControl(auto_start=True).add_to(m)

    # Retrieve user-selected location
    location_data = st_folium(m, width=700, height=500)

    # Check if a location has been clicked
    lat, lon = None, None
    if location_data.get("last_clicked"):
        lat, lon = location_data["last_clicked"]["lat"], location_data["last_clicked"]["lng"]

        # Add marker to the map
        marker_map = folium.Map(location=[lat, lon], zoom_start=15)
        folium.Marker([lat, lon], popup=f"Selected Location: {lat:.5f}, {lon:.5f}").add_to(marker_map)
        st_folium(marker_map, width=700, height=500)

    return lat, lon


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

def display_initial_form():
    st.title("Building Survey Form")

    # Map for location selection with marker
    st.header("1. Select the location on the map")
    lat, lon = initialize_map_with_marker()

    if lat and lon:
        st.success(f"Selected Location: Latitude {lat:.5f}, Longitude {lon:.5f}")

    # Other form fields
    type_of_use = st.selectbox("2. Type of Use", ["Residential", "Industrial", "Public Building"])
    number_of_users = st.selectbox("3. Number of Users", ["0-10", "11-100", "100+"])
    importance_category = st.selectbox("4. Building Importance Category", ["Σ1", "Σ2", "Σ3", "Σ4"])
    danger_falling = st.selectbox("5. Non-Structural Falling Danger", ["No", "Yes"])
    num_floors = st.number_input("6. Number of Floors", min_value=1, step=1)
    structure_condition = st.selectbox("7. Condition of Structure", ["Good", "Rust/Spalling"])
    year_construction = st.number_input("8. Year of Construction", min_value=1800, max_value=2024, step=1)
    previous_damages = st.selectbox("9. Previous Damages", ["No", "Yes"])

    # CAPTCHA
    captcha_input = st.text_input("Enter CAPTCHA (type '12345')")
    captcha_valid = captcha_input == "12345"

    if st.button("Submit"):
        if captcha_valid and lat is not None and lon is not None:
            c.execute('INSERT INTO survey_data (latitude, longitude, type_of_use, number_of_users, building_importance_category, non_structural_falling_danger, number_of_floors, condition_of_structure, year_of_construction, previous_damages, reviewed) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)',
                      (lat, lon, type_of_use, number_of_users, importance_category, danger_falling, num_floors, structure_condition, year_construction, previous_damages, False))
            conn.commit()
            st.success("Survey submitted successfully!")
        else:
            st.error("Please fill all required fields and pass the CAPTCHA.")


# Admin functionality to review listings
def review_listings():
    st.title("Admin Dashboard")

    # Filter for reviewed/non-reviewed listings
    review_filter = st.radio("Show Listings", ["Non-Reviewed", "Reviewed"])
    reviewed = review_filter == "Reviewed"

    try:
        # Fetch non-reviewed or reviewed listings
        if not reviewed:
            c.execute("SELECT * FROM survey_data WHERE reviewed = 0")
        else:
            c.execute('''
                SELECT s.*, r.reviewed_at 
                FROM survey_data s
                INNER JOIN review_data r ON s.id = r.survey_id
            ''')
        listings = c.fetchall()
    except sqlite3.OperationalError as e:
        st.error(f"Database error: {e}")
        return

    if not listings:
        st.info(f"No {'reviewed' if reviewed else 'non-reviewed'} listings available.")
        return

    # Select a listing to preview/review
    listing_options = [f"Listing {l[0]}: ({l[1]}, {l[2]})" for l in listings]
    selected_option = st.selectbox("Select a listing", listing_options)
    selected_id = listings[listing_options.index(selected_option)][0]

    # Fetch details of the selected listing
    c.execute("SELECT * FROM survey_data WHERE id = ?", (selected_id,))
    listing = c.fetchone()

    # Display listing details
    st.header(f"Listing Details (ID: {selected_id})")
    st.write(f"**Latitude:** {listing[1]}")
    st.write(f"**Longitude:** {listing[2]}")
    st.write(f"**Type of Use:** {listing[3]}")
    st.write(f"**Number of Users:** {listing[4]}")
    st.write(f"**Building Importance Category:** {listing[5]}")
    st.write(f"**Non-Structural Falling Danger:** {listing[6]}")
    st.write(f"**Number of Floors:** {listing[7]}")
    st.write(f"**Condition of Structure:** {listing[8]}")
    st.write(f"**Year of Construction:** {listing[9]}")
    st.write(f"**Previous Damages:** {listing[10]}")

    if not reviewed:
        st.subheader("Review Form")
        structural_system = st.selectbox("Structural System", ["RC-Frames", "RC-Walls", "Brick Walls"])
        arrangement_walls = st.selectbox("Arrangement of Walls", ["No", "Yes"])
        input_quality = st.slider("Input Quality (1-5)", min_value=1, max_value=5)
        soil_class = st.selectbox("Soil Class", ["A", "B", "C"])
        load_capacity_reduction = st.selectbox("Load Capacity Reduction", ["None", "Moderate", "Severe"])
        structure_performance = st.text_area("Structure Performance")
        retrofitting_methods = st.multiselect("Retrofitting Methods", ["RC Node Strengthening", "Polyurethane Injections", "FRP Wrapping"])

        if st.button("Submit Review"):
            c.execute('''INSERT INTO review_data (survey_id, structural_system, arrangement_walls, input_quality, soil_class, load_capacity_reduction, structure_performance, retrofitting_methods)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?)''',
                      (selected_id, structural_system, arrangement_walls, input_quality, soil_class, load_capacity_reduction, structure_performance, ', '.join(retrofitting_methods)))
            c.execute("UPDATE survey_data SET reviewed = 1 WHERE id = ?", (selected_id,))
            conn.commit()
            st.success("Review submitted successfully!")
    else:
        st.subheader("Review Details")
        c.execute("SELECT * FROM review_data WHERE survey_id = ?", (selected_id,))
        review = c.fetchone()
        if review:
            st.write(f"**Structural System:** {review[2]}")
            st.write(f"**Arrangement of Walls:** {review[3]}")
            st.write(f"**Input Quality:** {review[4]}")
            st.write(f"**Soil Class:** {review[5]}")
            st.write(f"**Load Capacity Reduction:** {review[6]}")
            st.write(f"**Structure Performance:** {review[7]}")
            st.write(f"**Retrofitting Methods:** {review[8]}")
            st.write(f"**Reviewed At:** {review[9]}")

# Main app logic
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

admin_login()

if st.session_state.logged_in:
    review_listings()
else:
    display_initial_form()

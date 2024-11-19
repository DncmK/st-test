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

# Create table for survey data if it doesn't exist
c.execute('''CREATE TABLE IF NOT EXISTS survey_data (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                latitude REAL,
                longitude REAL,
                type_of_use TEXT,
                number_of_users TEXT,
                building_importance_category TEXT,
                non_structural_falling_danger TEXT,
                non_structural_falling_photo BLOB,
                number_of_floors INTEGER,
                condition_of_structure TEXT,
                structure_condition_photo BLOB,
                year_of_construction INTEGER,
                previous_damages TEXT,
                previous_damages_photo BLOB,
                neighboring_buildings_impact TEXT,
                neighboring_impact_photo BLOB,
                soft_floor TEXT,
                soft_floor_photo BLOB,
                short_column TEXT,
                short_column_photo BLOB
            )''')

# Create table for review data if it doesn't exist
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

# Function to resize an image
def resize_image(image):
    img = Image.open(image)
    img_resized = img.resize((int(img.width * 0.2), int(img.height * 0.2)))
    buffered = io.BytesIO()
    img_resized.save(buffered, format="JPEG")
    return buffered.getvalue()

# Function to handle the admin login
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

# Function to display the initial form for non-registered users
def display_initial_form():
    st.title("Building Survey Form")

    # 1) Select location on the map
    st.header("1. Select the location on the map")
    map = folium.Map(location=[38.0, 23.7], zoom_start=6)
    # folium.plugins.LocateControl().add_to(map)
    folium.plugins.LocateControl(auto_start=True).add_to(map)
    # print(tsifsa)
    location = st_folium(map, width=700, height=300)
    
    if location:
        # if location['last_clicked']['lat'] != None and location['last_clicked']['lng'] != None:
        # try:
        if location.get("last_clicked"):
            lat, lon = location['last_clicked']['lat'], location['last_clicked']['lng']
            # location.add_child(folium.ClickForMarker())
            # fg = folium.FeatureGroup(name="State bounds")
            # fg.add_child(folium.Marker(location=[lat, lon]))
            # location = st_folium(
            #                 map,
            #                 feature_group_to_add=fg,
            #                 width=1200,
            #                 height=500,
            #             )
            st.success(f"Selected Location: Latitude {lat}, Longitude {lon}")
        # except Exception:
        #     pass
    
    # 2) Select the type of use
    st.header("2. Select the type of use")
    use_type = st.selectbox("Type of Use", ["Residential", "Industrial", "Concentrated Audience", 
                                            "Public Building", "Emergency Building"],
                             help="This is an explanatory help")

    # 3) Number of users
    st.header("3. Number of users")
    num_users = st.selectbox("Number of Users", ["0-10", "11-100", "100+"])

    # 4) Building importance category
    st.header("4. Building Importance Category")
    importance_category = st.selectbox("Building Importance Category", ["Σ1", "Σ2", "Σ3", "Σ4"])

    # 5) Danger of non-structural element falling
    st.header("5. Danger of Non-Structural Element Falling")
    danger_falling = st.selectbox("Danger of Non-Structural Element Falling", ["No", "Yes"])
    falling_photo = None
    if danger_falling == "Yes":
        falling_photo = st.file_uploader("Upload photo of Non-Structural Element", type=["jpg", "png", "jpeg"])
    
    # 6) Number of floors
    st.header("6. Number of Floors")
    num_floors = st.number_input("Number of Floors", min_value=1, max_value=100, step=1)

    # 7) Condition of structure
    st.header("7. Condition of Structure")
    structure_condition = st.selectbox("Condition of Structure", ["No", "Rust/Spalling"])
    rust_photo = None
    if structure_condition == "Rust/Spalling":
        rust_photo = st.file_uploader("Upload photo of Rust/Spalling", type=["jpg", "png", "jpeg"])
    
    # 8) Year of construction
    st.header("8. Year of Construction")
    year_construction = st.number_input("Year of Construction", min_value=1800, max_value=2024, step=1)

    # 9) Previous damages in vertical elements
    st.header("9. Previous Damages in Vertical Elements")
    vertical_damage = st.selectbox("Previous Damages in Vertical Elements", ["No", "Yes"])
    damage_photo = None
    if vertical_damage == "Yes":
        damage_photo = st.file_uploader("Upload photo of Vertical Element Damage", type=["jpg", "png", "jpeg"])

    # 10) Danger of impact with neighboring buildings
    st.header("10. Danger of Impact with Neighboring Buildings")
    danger_impact = st.selectbox("Danger of Impact with Neighboring Buildings", ["No", "Yes"])
    impact_photo = None
    if danger_impact == "Yes":
        impact_photo = st.file_uploader("Upload photo of Neighboring Building", type=["jpg", "png", "jpeg"])

    # 11) Soft floor (pilotis)
    st.header("11. Soft Floor (Pilotis)")
    soft_floor = st.selectbox("Soft Floor (Pilotis)", ["No", "Yes"])
    soft_floor_photo = None
    if soft_floor == "Yes":
        soft_floor_photo = st.file_uploader("Upload photo of Soft Floor (Pilotis)", type=["jpg", "png", "jpeg"])

    # 12) Short column
    st.header("12. Short Column")
    short_column = st.selectbox("Short Column", ["No", "Yes"])
    short_column_photo = None
    if short_column == "Yes":
        short_column_photo = st.file_uploader("Upload photo of Short Column", type=["jpg", "png", "jpeg"])

    # CAPTCHA implementation
    st.header("CAPTCHA Verification")
    captcha_input = st.text_input("Enter CAPTCHA (type '12345')")
    captcha_correct = captcha_input == "12345"

    # Submission button
    # if st.button("Submit") and captcha_correct:
    if st.button("Submit"):
        if captcha_correct:
            # Insert the data into the database
            c.execute('''INSERT INTO survey_data (latitude, longitude, use_type, num_users, importance_category,
                                                danger_falling, num_floors, structure_condition, year_construction,
                                                vertical_damage, danger_impact, soft_floor, short_column)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)''',
                    (lat, lon, use_type, num_users, importance_category, danger_falling, num_floors,
                    structure_condition, year_construction, vertical_damage, danger_impact,
                    soft_floor, short_column))
            survey_id = c.lastrowid

            # Process and save images if they exist
            image_types = ["falling_photo", "rust_photo", "damage_photo", "impact_photo", "soft_floor_photo", "short_column_photo"]
            images = [falling_photo, rust_photo, damage_photo, impact_photo, soft_floor_photo, short_column_photo]

            for img_type, img in zip(image_types, images):
                if img is not None:
                    resized_image = resize_image(img)
                    c.execute('''INSERT INTO survey_images (survey_id, image_type, image)
                                VALUES (?, ?, ?)''', (survey_id, img_type, resized_image))

            conn.commit()
            st.success("Form submitted successfully!")
        # elif not captcha_correct:
        else:
            st.error("Incorrect CAPTCHA. Please try again.")

# Function to display non-reviewed listings for admin users
def display_listings():
    st.title("Reviewed Listings")
    
    c.execute("SELECT * FROM review_data")
    listings = c.fetchall()
    
    if not listings:
        st.info("No listings available.")
        return
    
    listing_options = [f"Listing {listing[0]} - Survey ID: ({listing[1]})" for listing in listings]
    selected_listing = st.selectbox("Select a listing to preview", listing_options)

    st.title("Non-Reviewed Listings")
    
    c.execute("SELECT * FROM survey_data WHERE id NOT IN (SELECT survey_id FROM review_data WHERE reviewed = 1)")
    listings = c.fetchall()
    
    if not listings:
        st.info("No non-reviewed listings available.")
        return
    
    listing_options = [f"Listing {listing[0]} - Location: ({listing[1]}, {listing[2]})" for listing in listings]
    selected_listing = st.selectbox("Select a listing to review", listing_options)
    
    selected_listing_id = listings[listing_options.index(selected_listing)][0]
    review_listing(selected_listing_id)

# Function to review a selected listing for admin users
def review_listing(listing_id):
    st.header(f"Reviewing Listing ID: {listing_id}")
    
    # Fetch the listing data
    c.execute("SELECT * FROM survey_data WHERE id = ?", (listing_id,))
    listing_data = c.fetchone()

    # Display the listing data
    st.subheader("Listing Data")

    # Display location on map
    latitude = listing_data[1]
    longitude = listing_data[2]
    st.write("**Location:**", f"Latitude: {latitude}, Longitude: {longitude}")
    m = folium.Map(location=[latitude, longitude], zoom_start=16)
    folium.Marker([latitude, longitude], popup="Building Location").add_to(m)
    st_folium(m, width=700)

    # Display the other listing details
    st.write("**Type of Use:**", listing_data[3])
    st.write("**Number of Users:**", listing_data[4])
    st.write("**Building Importance Category:**", listing_data[5])
    st.write("**Number of Floors:**", listing_data[7])
    st.write("**Year of Construction:**", listing_data[9])

    # Display images if available (convert binary data back to an image)
    def display_image(data, caption):
        if data:  # Check if there is binary data
            try:
                image = Image.open(io.BytesIO(data))
                st.image(image, caption=caption, use_column_width=True)
            except Exception as e:
                st.error(f"Error displaying image: {e}")
    c.execute("SELECT EXISTS(SELECT 1 FROM survey_images WHERE survey_id = ? AND image_type = ? LIMIT 1)", (listing_id, 'falling_photo',))
    listing_data_2 = c.fetchone()
    if listing_data_2[0] == 1:
        c.execute("SELECT * FROM survey_images WHERE survey_id = ? AND image_type = ?", (listing_id, 'falling_photo',))
        listing_data_2 = c.fetchone()
        display_image(listing_data_2[3], "Non-Structural Falling Danger Photo")
    c.execute("SELECT EXISTS(SELECT 1 FROM survey_images WHERE survey_id = ? AND image_type = ? LIMIT 1)", (listing_id, 'rust_photo',))
    listing_data_2 = c.fetchone()
    if listing_data_2[0] == 1:
        c.execute("SELECT * FROM survey_images WHERE survey_id = ? AND image_type = ?", (listing_id, 'rust_photo',))
        listing_data_2 = c.fetchone()
        display_image(listing_data_2[3], "Structure Condition Photo")
    c.execute("SELECT EXISTS(SELECT 1 FROM survey_images WHERE survey_id = ? AND image_type = ? LIMIT 1)", (listing_id, 'damage_photo',))
    listing_data_2 = c.fetchone()
    if listing_data_2[0] == 1:
        c.execute("SELECT * FROM survey_images WHERE survey_id = ? AND image_type = ?", (listing_id, 'damage_photo',))
        listing_data_2 = c.fetchone()
        display_image(listing_data_2[3], "Previous Damages Photo")
    c.execute("SELECT EXISTS(SELECT 1 FROM survey_images WHERE survey_id = ? AND image_type = ? LIMIT 1)", (listing_id, 'impact_photo',))
    listing_data_2 = c.fetchone()
    if listing_data_2[0] == 1:
        c.execute("SELECT * FROM survey_images WHERE survey_id = ? AND image_type = ?", (listing_id, 'impact_photo',))
        listing_data_2 = c.fetchone()
        display_image(listing_data_2[3], "Neighboring Buildings Impact Photo")
    c.execute("SELECT EXISTS(SELECT 1 FROM survey_images WHERE survey_id = ? AND image_type = ? LIMIT 1)", (listing_id, 'soft_floor_photo',))
    listing_data_2 = c.fetchone()
    if listing_data_2[0] == 1:
        c.execute("SELECT * FROM survey_images WHERE survey_id = ? AND image_type = ?", (listing_id, 'soft_floor_photo',))
        listing_data_2 = c.fetchone()
        display_image(listing_data_2[3], "Soft Floor Photo")
    c.execute("SELECT EXISTS(SELECT 1 FROM survey_images WHERE survey_id = ? AND image_type = ? LIMIT 1)", (listing_id, 'short_column_photo',))
    listing_data_2 = c.fetchone()
    if listing_data_2[0] == 1:
        c.execute("SELECT * FROM survey_images WHERE survey_id = ? AND image_type = ?", (listing_id, 'short_column_photo',))
        listing_data_2 = c.fetchone()
        display_image(listing_data_2[3], "Short Column Photo")

    # Additional Review Form
    st.subheader("Review Form")

    structural_system = st.selectbox("Type of Structural System", ["RC-frames", "RC-walls", "Brick walls"])
    arrangement_walls = st.selectbox("Arrangement of Walls", ["No", "Yes"])

    irregular_vertical = st.selectbox("Irregular Structures Vertically", ["No", "Yes"])
    irregular_vertical_photo = None
    if irregular_vertical == "Yes":
        irregular_vertical_photo = st.file_uploader("Upload photo of vertical irregularity", type=["jpg", "png", "jpeg"])

    irregular_horizontal = st.selectbox("Irregular Structures Horizontally", ["No", "Yes"])
    irregular_horizontal_photo = None
    if irregular_horizontal == "Yes":
        irregular_horizontal_photo = st.file_uploader("Upload photo of horizontal irregularity", type=["jpg", "png", "jpeg"])

    torsion_rotation = st.selectbox("Torsion/Rotation", ["No", "Yes"])
    torsion_rotation_photo = None
    if torsion_rotation == "Yes":
        torsion_rotation_photo = st.file_uploader("Upload photo of torsion/rotation", type=["jpg", "png", "jpeg"])

    structural_vulnerabilities = st.multiselect("Structural Vulnerabilities", ["Danger of impact", "Soft floor", "Short column"])

    heavy_finishes = st.selectbox("Heavy Finishes", ["No", "Yes"])
    heavy_finishes_photo = None
    if heavy_finishes == "Yes":
        heavy_finishes_photo = st.file_uploader("Upload photo of heavy finishes", type=["jpg", "png", "jpeg"])

    input_quality = st.slider("Quality of User Input (1-5)", min_value=1, max_value=5)

    soil_class = st.selectbox("Soil Class", ["A", "B", "C"])

    load_capacity_reduction = st.selectbox("Load Bearing Capacity Reduction (R)", ["Flexural cracks", "Multiple flexural cracks", "Diagonal cracks", "Bending reinforcement"])

    constructed_area = st.number_input("Total Constructed Area")
    constructed_area_photo = st.file_uploader("Upload photo showing constructed area", type=["jpg", "png", "jpeg"])

    structure_performance = st.text_area("Additional Description of Structure Performance")

    retrofitting_methods = st.multiselect("Retrofitting Methods", ["Retrofitting RC-nodes", "Retrofitting RC-beams", "Polyurethane joints", "FRPU jackets"])

    if st.button("Submit Review"):
        # Resize images if any
        if irregular_vertical_photo:
            irregular_vertical_photo = resize_image(irregular_vertical_photo)
        if irregular_horizontal_photo:
            irregular_horizontal_photo = resize_image(irregular_horizontal_photo)
        if torsion_rotation_photo:
            torsion_rotation_photo = resize_image(torsion_rotation_photo)
        if heavy_finishes_photo:
            heavy_finishes_photo = resize_image(heavy_finishes_photo)
        if constructed_area_photo:
            constructed_area_photo = resize_image(constructed_area_photo)
        
        # Insert the review data into the database
        c.execute('''INSERT INTO review_data (
                        survey_id, structural_system, arrangement_walls, irregular_vertical, irregular_vertical_photo,
                        irregular_horizontal, irregular_horizontal_photo, torsion_rotation, torsion_rotation_photo,
                        structural_vulnerabilities, heavy_finishes, heavy_finishes_photo, input_quality, soil_class,
                        load_capacity_reduction, constructed_area, constructed_area_photo, structure_performance, retrofitting_methods, reviewed
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)''',
                  (listing_id, structural_system, arrangement_walls, irregular_vertical, irregular_vertical_photo,
                   irregular_horizontal, irregular_horizontal_photo, torsion_rotation, torsion_rotation_photo,
                   ','.join(structural_vulnerabilities), heavy_finishes, heavy_finishes_photo, input_quality, soil_class,
                   load_capacity_reduction, constructed_area, constructed_area_photo, structure_performance, ','.join(retrofitting_methods),
                   st.session_state.get("logged_in", False)))
        
        conn.commit()
        st.success("Listing reviewed and data saved successfully!")


# Main application logic
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

admin_login()

# Only show listings if the user is logged in as admin
if st.session_state.logged_in:
    display_listings()
else:
    display_initial_form()
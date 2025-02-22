import streamlit as st
import datetime
import pandas as pd
from PIL import Image
import json
import numpy as np
from scipy.stats import gaussian_kde

def init_session_state():
    if 'step' not in st.session_state:
        st.session_state.step = 1
    if 'form_data' not in st.session_state:
        st.session_state.form_data = {
            'driver_info': {},
            'vehicle_info': {},
            'battery_info': {},
            'delivery_platforms': {},  # Changed from list to dictionary
            'emergency_contact': {}
        }

def next_step():
    st.session_state.step += 1

def prev_step():
    st.session_state.step -= 1

def save_form_data(section, data):
    # Ensure the section exists and is a dictionary
    if section not in st.session_state.form_data:
        st.session_state.form_data[section] = {}
    st.session_state.form_data[section].update(data)

def calculate_trigger_probability(token_file='trigger_temp_results.json', temp_threshold=None):
    # Load the token file
    with open(token_file, 'r') as f:
        data = json.load(f)
    
    if data['status'] == 'error':
        print(data['message'])
        return None
    
    # Reconstruct KDE
    temperatures = np.array(data['temperatures'])
    bandwidth = data['bandwidth']
    kde = gaussian_kde(temperatures, bw_method=bandwidth / np.std(temperatures))
    
    # If specific threshold provided, calculate probability
    if temp_threshold is not None:
        temp_range = np.linspace(min(temperatures), max(temperatures), 1000)
        kde_values = kde(temp_range)
        # Calculate probability of exceeding threshold
        prob_exceed = kde.integrate_box_1d(temp_threshold, np.inf)
        print(f"Probability of exceeding {temp_threshold}°C: {prob_exceed:.4f}")
        return prob_exceed
    
    # Otherwise return full probability distribution
    temp_range = np.array(data['temp_range'])
    kde_values = kde(temp_range)
    return temp_range, kde_values

def main():
    st.set_page_config(page_title="E-Bike Driver Onboarding", layout="wide")
    init_session_state()

    # Progress bar
    total_steps = 5
    progress = st.progress((st.session_state.step - 1) / (total_steps - 1))
    st.write(f"Step {st.session_state.step} of {total_steps}")

    # Header
    st.title("E-Bike Driver Onboarding")
    st.write("Complete your registration for delivery services")

    if st.session_state.step == 1:
        st.header("Driver Information")
        with st.form("driver_info"):
            # Basic Info
            col1, col2 = st.columns(2)
            with col1:
                first_name = st.text_input("First Name")
                email = st.text_input("Email")
                dob = st.date_input("Date of Birth", 
                                  min_value=datetime.date(1950, 1, 1),
                                  max_value=datetime.date.today() - datetime.timedelta(days=18*365))
            with col2:
                last_name = st.text_input("Last Name")
                phone = st.text_input("Phone Number")
                driver_license = st.text_input("Driver's License Number")

            # Address
            st.subheader("Address")
            address = st.text_input("Street Address")
            city = st.text_input("City")
            state = st.text_input("State")
            zip_code = st.text_input("ZIP Code")

            submitted = st.form_submit_button("Next")
            if submitted:
                save_form_data('driver_info', {
                    'first_name': first_name,
                    'last_name': last_name,
                    'email': email,
                    'phone': phone,
                    'dob': str(dob),
                    'driver_license': driver_license,
                    'address': address,
                    'city': city,
                    'state': state,
                    'zip_code': zip_code
                })
                next_step()

    elif st.session_state.step == 2:
        st.header("Delivery Platform Information")
        with st.form("platform_info"):
            # Platform Selection
            st.subheader("Select Your Delivery Platforms")
            platforms = {
                'uber_eats': st.checkbox("Uber Eats"),
                'doordash': st.checkbox("DoorDash"),
                'grubhub': st.checkbox("GrubHub"),
                'independent': st.checkbox("Independent/Other")
            }

            # Platform-specific IDs
            st.subheader("Platform IDs")
            platform_ids = {}
            for platform, selected in platforms.items():
                if selected:
                    platform_ids[platform] = st.text_input(f"{platform.replace('_', ' ').title()} Driver ID")

            # Work Schedule
            st.subheader("Typical Work Schedule")
            cols = st.columns(3)
            with cols[0]:
                avg_hours = st.number_input("Average Hours per Week", min_value=0, max_value=168)
            with cols[1]:
                primary_zone = st.text_input("Primary Delivery Zone")
            with cols[2]:
                start_date = st.date_input("Start Date", min_value=datetime.date.today())

            submitted = st.form_submit_button("Next")
            if submitted:
                save_form_data('delivery_platforms', {  # Changed from deliveryPlatforms to delivery_platforms
                    'platforms': platforms,
                    'platform_ids': platform_ids,
                    'avg_hours': avg_hours,
                    'primary_zone': primary_zone,
                    'start_date': str(start_date)
                })
                next_step()

    elif st.session_state.step == 3:
        st.header("Vehicle Information")
        with st.form("vehicle_info"):
            col1, col2 = st.columns(2)
            with col1:
                make = st.text_input("E-Bike Make")
                model = st.text_input("E-Bike Model")
                year = st.number_input("Year", min_value=2010, max_value=datetime.date.today().year)
            
            with col2:
                serial_number = st.text_input("Vehicle Serial Number")
                color = st.text_input("Vehicle Color")
                st.write("Upload Vehicle Photos")
                vehicle_photo = st.file_uploader("Upload clear photos of your e-bike", 
                                              type=['png', 'jpg', 'jpeg'],
                                              accept_multiple_files=True)

            submitted = st.form_submit_button("Next")
            if submitted:
                photo_names = []
                if vehicle_photo:
                    photo_names = [photo.name for photo in vehicle_photo]
                
                save_form_data('vehicle_info', {
                    'make': make,
                    'model': model,
                    'year': year,
                    'serial_number': serial_number,
                    'color': color,
                    'photos': photo_names
                })
                next_step()

    elif st.session_state.step == 4:
        st.header("Battery Information")
        with st.form("battery_info"):
            # Battery Details
            col1, col2 = st.columns(2)
            with col1:
                battery_manufacturer = st.text_input("Battery Manufacturer")
                battery_model = st.text_input("Battery Model Number")
                purchase_date = st.date_input("Purchase Date", 
                                           max_value=datetime.date.today())
            
            with col2:
                battery_capacity = st.number_input("Battery Capacity (Wh)", min_value=0)
                charging_cycles = st.number_input("Estimated Charging Cycles", min_value=0)
                last_inspection = st.date_input("Last Inspection Date",
                                             max_value=datetime.date.today())

            # Documentation
            st.subheader("Battery Documentation")
            battery_receipt = st.file_uploader("Upload Battery Purchase Receipt", 
                                            type=['pdf', 'png', 'jpg', 'jpeg'])
            inspection_cert = st.file_uploader("Upload Latest Inspection Certificate", 
                                            type=['pdf', 'png', 'jpg', 'jpeg'])

            # Charging Information
            st.subheader("Charging Information")
            charging_location = st.selectbox("Primary Charging Location", 
                                          ["Home", "Work", "Public Charging Station", "Other"])
            charging_location_other = ""
            if charging_location == "Other":
                charging_location_other = st.text_input("Specify Charging Location")

            # Add temperature threshold analysis
            st.subheader("Temperature Risk Analysis")
            temp_threshold = st.number_input("Temperature Threshold (°C)", 
                                          min_value=0.0,
                                          max_value=500.0,
                                          value=100.0,
                                          step=1.0)
            
            if st.form_submit_button("Calculate Risk"):
                try:
                    prob = calculate_trigger_probability(temp_threshold=temp_threshold)
                    if prob is not None:
                        st.warning(f"Probability of battery exceeding {temp_threshold}°C: {prob:.2%}")
                        if prob > 0.1:
                            st.error("⚠️ High risk of thermal event! Consider lower operating temperatures.")
                        elif prob > 0.05:
                            st.warning("⚡ Moderate risk - monitor carefully")
                        else:
                            st.success("✅ Low risk temperature threshold")
                except Exception as e:
                    st.error(f"Error calculating probability: {str(e)}")

            submitted = st.form_submit_button("Next")
            if submitted:
                save_form_data('battery_info', {
                    'manufacturer': battery_manufacturer,
                    'model': battery_model,
                    'purchase_date': str(purchase_date),
                    'capacity': battery_capacity,
                    'charging_cycles': charging_cycles,
                    'last_inspection': str(last_inspection),
                    'receipt': battery_receipt.name if battery_receipt else None,
                    'inspection_cert': inspection_cert.name if inspection_cert else None,
                    'charging_location': charging_location,
                    'charging_location_other': charging_location_other if charging_location == "Other" else None
                })
                next_step()

    elif st.session_state.step == 5:
        st.header("Safety Agreement and Submission")
        
        # Display safety guidelines
        st.subheader("Safety Guidelines")
        st.info("""
        - Regular battery inspections every 3 months
        - Use only approved charging equipment and locations
        - Report any battery issues immediately
        - Follow proper storage guidelines
        - Maintain documentation of all maintenance
        """)

        # Training acknowledgment
        st.subheader("Safety Training")
        training_complete = st.checkbox("I have completed the required safety training")
        
        # Terms and conditions
        st.subheader("Terms and Conditions")
        terms_agree = st.checkbox("I agree to the terms and conditions")
        safety_agree = st.checkbox("I agree to follow all safety guidelines")
        
        # Emergency contact
        st.subheader("Emergency Contact")
        with st.form("emergency_contact"):
            col1, col2 = st.columns(2)
            with col1:
                emergency_name = st.text_input("Emergency Contact Name")
                emergency_relation = st.text_input("Relationship")
            with col2:
                emergency_phone = st.text_input("Emergency Contact Phone")
                emergency_email = st.text_input("Emergency Contact Email")

            submit_final = st.form_submit_button("Submit Registration")
            if submit_final and training_complete and terms_agree and safety_agree:
                # Save all final data
                save_form_data('emergency_contact', {
                    'name': emergency_name,
                    'relation': emergency_relation,
                    'phone': emergency_phone,
                    'email': emergency_email,
                    'training_complete': training_complete,
                    'terms_agree': terms_agree,
                    'safety_agree': safety_agree
                })
                
                # Show success message
                st.success("Registration submitted successfully!")
                st.json(st.session_state.form_data)  # Display collected data

    # Navigation buttons (except for last page)
    if st.session_state.step > 1 and st.session_state.step < 5:
        col1, col2, col3 = st.columns([1, 2, 1])
        with col1:
            st.button("Previous", on_click=prev_step)

if __name__ == "__main__":
    main()
    # Example usage
    prob = calculate_trigger_probability(temp_threshold=100.0)
    temp_range, kde_values = calculate_trigger_probability()
    if temp_range is not None:
        print(f"Temperature range min: {min(temp_range):.2f}°C")
        print(f"Temperature range max: {max(temp_range):.2f}°C")
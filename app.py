import streamlit as st
import json
import os
import pandas as pd
from PIL import Image
import hashlib
import datetime
from pathlib import Path
import glob

# Page configuration
st.set_page_config(
    page_title="Medical Deepfake Difficulty Labeling",
    page_icon="🏥",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better styling
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 2rem;
    }
    .doctor-info {
        background-color: #e8f4fd;
        color: #1a365d;
        padding: 1rem;
        border-radius: 0.5rem;
        margin-bottom: 1rem;
        border: 2px solid #3182ce;
    }
    .image-container {
        text-align: center;
        margin: 1rem 0;
    }
    .difficulty-buttons {
        display: flex;
        justify-content: center;
        gap: 1rem;
        margin: 1rem 0;
    }
    .progress-bar {
        margin: 1rem 0;
    }
    .ehr-text {
        background-color: #f8f9fa;
        color: #000000;
        padding: 1rem;
        border-radius: 0.5rem;
        border-left: 4px solid #1f77b4;
        margin: 1rem 0;
    }
</style>
""", unsafe_allow_html=True)

# Data paths
IMAGES_PATH = "out_scm_tts"
EHR_PATH = "out_scm_tts_ehr"
LABELS_PATH = "doctor_labels"

# Create labels directory if it doesn't exist
os.makedirs(LABELS_PATH, exist_ok=True)

def load_image_data():
    """Load all image data from the CSV files"""
    image_data = []
    
    for difficulty in ['easy', 'medium', 'hard']:
        csv_path = os.path.join(IMAGES_PATH, difficulty, f"results_{difficulty}.csv")
        if os.path.exists(csv_path):
            df = pd.read_csv(csv_path)
            for _, row in df.iterrows():
                image_data.append({
                    'filename': row['file'],
                    'difficulty': difficulty,
                    'seed': row['seed'],
                    'prompt': row['prompt'],
                    'scm_realism': row['scm_realism'],
                    'scm_artifact': row['scm_artifact'],
                    'scm_symmetry': row['scm_symmetry'],
                    'scm_noise_cv': row['scm_noise_cv'],
                    'scm_vessel_decay': row['scm_vessel_decay'],
                    'accepted': row['accepted'],
                    'objective': row['objective']
                })
    
    return image_data

def load_ehr_text(filename):
    """Load EHR text for a given image filename"""
    # Convert image filename to EHR filename
    ehr_filename = filename.replace('.png', '.ehr.txt')
    
    # Try to find the EHR file in any difficulty folder
    for difficulty in ['easy', 'medium', 'hard']:
        ehr_path = os.path.join(EHR_PATH, difficulty, ehr_filename)
        if os.path.exists(ehr_path):
            with open(ehr_path, 'r') as f:
                return f.read().strip()
    
    return "EHR text not found"

def get_doctor_file_path(doctor_id):
    """Get the file path for a doctor's labels"""
    return os.path.join(LABELS_PATH, f"doctor_{doctor_id}.json")

def load_doctor_labels(doctor_id):
    """Load existing labels for a doctor"""
    file_path = get_doctor_file_path(doctor_id)
    if os.path.exists(file_path):
        with open(file_path, 'r') as f:
            return json.load(f)
    return {}

def save_doctor_labels(doctor_id, labels):
    """Save labels for a doctor"""
    file_path = get_doctor_file_path(doctor_id)
    with open(file_path, 'w') as f:
        json.dump(labels, f, indent=2)

def hash_doctor_id(doctor_id):
    """Create a hash of the doctor ID for security"""
    return hashlib.sha256(doctor_id.encode()).hexdigest()[:16]

def load_whitelist():
    """Load the doctor whitelist"""
    whitelist_path = "doctor_whitelist.json"
    if os.path.exists(whitelist_path):
        with open(whitelist_path, 'r') as f:
            return json.load(f)['whitelist']
    return []

def authenticate_doctor():
    """Authentication system with whitelist"""
    st.sidebar.markdown("## 🔐 Doctor Authentication")
    
    # Load whitelist
    whitelist = load_whitelist()
    
    if not whitelist:
        st.sidebar.error("❌ Whitelist not found. Please contact administrator.")
        return None, None
    
    doctor_id = st.sidebar.text_input("Enter your Doctor ID:", type="password")
    
    if doctor_id:
        if doctor_id in whitelist:
            # Create a simple hash for security
            doctor_hash = hash_doctor_id(doctor_id)
            st.sidebar.success(f"✅ Logged in as Doctor: {doctor_hash}")
            return doctor_id, doctor_hash
        else:
            st.sidebar.error("❌ Invalid Doctor ID. Please contact administrator for access.")
            return None, None
    
    return None, None

def display_image_and_ehr(image_data, ehr_text):
    """Display the image and EHR text"""
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.markdown("### 📸 Medical Image")
        image_path = None
        
        # Find the image file
        for difficulty in ['easy', 'medium', 'hard']:
            potential_path = os.path.join(IMAGES_PATH, difficulty, image_data['filename'])
            if os.path.exists(potential_path):
                image_path = potential_path
                break
        
        if image_path:
            image = Image.open(image_path)
            st.image(image, use_container_width=True)
        else:
            st.error(f"Image not found: {image_data['filename']}")
    
    with col2:
        st.markdown("### 📋 EHR Information")
        st.markdown(f'<div class="ehr-text">{ehr_text}</div>', unsafe_allow_html=True)

def main():
    st.markdown('<h1 class="main-header">🏥 Medical Deepfake Difficulty Labeling</h1>', unsafe_allow_html=True)
    
    # Authentication
    doctor_id, doctor_hash = authenticate_doctor()
    
    if not doctor_id:
        st.warning("Please enter your Doctor ID in the sidebar to continue.")
        
        # Show whitelist information
        whitelist = load_whitelist()
        if whitelist:
            st.info(f"📋 **Authorized Doctor IDs:** {len(whitelist)} doctors have access to this system.")
        
        st.markdown("""
        ### About This Application
        
        This application allows authorized medical professionals to label the difficulty of detecting deepfake medical images.
        
        **Features:**
        - Secure whitelist-based authentication
        - Image and EHR text display
        - Difficulty rating system
        - Progress tracking
        - Individual label storage
        
        **Instructions:**
        1. Enter your authorized Doctor ID in the sidebar
        2. Review each medical image and corresponding EHR text
        3. Rate the difficulty of detecting if the image is a deepfake
        4. Your labels will be saved automatically
        
        **Security:**
        - Only pre-authorized Doctor IDs can access the system
        - Each doctor's labels are stored separately
        - Doctor IDs are hashed for privacy
        """)
        return
    
    # Load data
    image_data_list = load_image_data()
    doctor_labels = load_doctor_labels(doctor_id)
    
    # Doctor info sidebar
    st.sidebar.markdown(f"""
    <div class="doctor-info">
        <h4>👨‍⚕️ Doctor Information</h4>
        <p><strong>ID:</strong> {doctor_hash}</p>
        <p><strong>Images Labeled:</strong> {len(doctor_labels)}</p>
        <p><strong>Total Images:</strong> {len(image_data_list)}</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Progress tracking
    progress = len(doctor_labels) / len(image_data_list) if image_data_list else 0
    st.sidebar.markdown("### 📈 Progress")
    st.sidebar.progress(progress)
    st.sidebar.write(f"{len(doctor_labels)} / {len(image_data_list)} images labeled ({progress:.1%})")
    
    # Find next unlabeled image
    unlabeled_images = [img for img in image_data_list if img['filename'] not in doctor_labels]
    
    if not unlabeled_images:
        st.success("🎉 Congratulations! You have labeled all images.")
        st.markdown("### 📊 Your Labeling Summary")
        
        # Show summary statistics
        if doctor_labels:
            difficulty_counts = {}
            for filename, label_data in doctor_labels.items():
                difficulty = label_data.get('doctor_difficulty', 'Unknown')
                difficulty_counts[difficulty] = difficulty_counts.get(difficulty, 0) + 1
            
            col1, col2, col3 = st.columns(3)
            for i, (difficulty, count) in enumerate(difficulty_counts.items()):
                with [col1, col2, col3][i % 3]:
                    st.metric(f"{difficulty.title()} Difficulty", count)
        
        return
    
    # Display current image
    current_image = unlabeled_images[0]
    ehr_text = load_ehr_text(current_image['filename'])
    
    st.markdown("### Current Image")
    
    # Display image and EHR
    display_image_and_ehr(current_image, ehr_text)
    
    # Difficulty rating interface
    st.markdown("### 🎯 Difficulty Rating")
    st.markdown("**How difficult is it to detect that this image is a deepfake?**")
    
    col1, col2, col3 = st.columns(3)
    
    
    with col1:
        if st.button("🟢 Easy", use_container_width=True): 
            save_label(doctor_id, current_image['filename'], "easy", current_image, ehr_text)
            st.rerun()
    
    with col2:
        if st.button("🟡 Medium", use_container_width=True):
            save_label(doctor_id, current_image['filename'], "medium", current_image, ehr_text)
            st.rerun()
    
    with col3:
        if st.button("🔴 Hard", use_container_width=True):
            save_label(doctor_id, current_image['filename'], "hard", current_image, ehr_text)
            st.rerun()
    
    # Additional options
    st.markdown("### 📝 Additional Options")
    
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("⏭️ Skip This Image", use_container_width=True):
            save_label(doctor_id, current_image['filename'], "skipped", current_image, ehr_text)
            st.rerun()
    
    with col2:
        if st.button("🔄 View Previous Labels", use_container_width=True):
            show_previous_labels(doctor_labels)

def save_label(doctor_id, filename, difficulty, image_data, ehr_text):
    """Save a label for the current image"""
    doctor_labels = load_doctor_labels(doctor_id)
    
    label_data = {
        'doctor_difficulty': difficulty,
        'timestamp': datetime.datetime.now().isoformat(),
        'original_difficulty': image_data['difficulty'],
        'seed': image_data['seed'],
        'ehr_text': ehr_text,
        'metadata': {
            'scm_realism': image_data['scm_realism'],
            'scm_artifact': image_data['scm_artifact'],
            'scm_symmetry': image_data['scm_symmetry'],
            'scm_noise_cv': image_data['scm_noise_cv'],
            'scm_vessel_decay': image_data['scm_vessel_decay'],
            'accepted': image_data['accepted'],
            'objective': image_data['objective']
        }
    }
    
    doctor_labels[filename] = label_data
    save_doctor_labels(doctor_id, doctor_labels)
    
    st.success(f"✅ Label saved: {difficulty.replace('_', ' ').title()}")

def show_previous_labels(doctor_labels):
    """Show previous labels in an expandable section"""
    if not doctor_labels:
        st.info("No previous labels found.")
        return
    
    st.markdown("### 📋 Previous Labels")
    
    for filename, label_data in list(doctor_labels.items())[-10:]:  # Show last 10
        with st.expander(f"{filename} - {label_data['doctor_difficulty'].replace('_', ' ').title()}"):
            col1, col2 = st.columns(2)
            
            with col1:
                st.write(f"**Doctor Rating:** {label_data['doctor_difficulty'].replace('_', ' ').title()}")
                st.write(f"**Original Difficulty:** {label_data['original_difficulty']}")
                st.write(f"**Timestamp:** {label_data['timestamp']}")
            
            with col2:
                st.write(f"**Seed:** {label_data['seed']}")
                st.write(f"**File:** {filename}")

if __name__ == "__main__":
    main()

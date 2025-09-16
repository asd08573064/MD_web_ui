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

# Data paths and modalities
DATA_ROOT = "data"
MODALITIES = ['CXR', 'MRI', 'CT', 'pathology']
DIFFICULTIES = ['easy', 'medium', 'hard']
LABELS_PATH = "doctor_labels"

# Create labels directory if it doesn't exist
os.makedirs(LABELS_PATH, exist_ok=True)

def ensure_data_directories_exist():
    """Create required data directory structure if it doesn't exist."""
    for modality in MODALITIES:
        images_root = os.path.join(DATA_ROOT, modality, 'images')
        reports_root = os.path.join(DATA_ROOT, modality, 'reports')
        for root in (images_root, reports_root):
            os.makedirs(root, exist_ok=True)
            for difficulty in DIFFICULTIES:
                os.makedirs(os.path.join(root, difficulty), exist_ok=True)

def list_image_files(images_dir):
    """List image files in a directory with common extensions."""
    exts = ('*.png', '*.jpg', '*.jpeg', '*.bmp')
    files = []
    for ext in exts:
        files.extend(glob.glob(os.path.join(images_dir, ext)))
    # Return just basenames, sorted for stability
    return sorted([os.path.basename(p) for p in files])

def load_image_data(modality):
    """Load image data by scanning data/<modality>/images/<difficulty> directories."""
    image_data = []
    for difficulty in DIFFICULTIES:
        images_dir = os.path.join(DATA_ROOT, modality, 'images', difficulty)
        filenames = list_image_files(images_dir)
        for filename in filenames:
            image_data.append({
                'filename': filename,
                'modality': modality,
                'difficulty': difficulty
            })
    return image_data

def load_ehr_text(filename, modality, difficulty):
    """Load report text for a given image filename in a modality and difficulty."""
    base, _ = os.path.splitext(filename)
    # Support both .txt and .ehr.txt just in case
    candidate_names = [f"{base}.txt", f"{base}.ehr.txt", f"{base}.report.txt"]
    reports_dir = os.path.join(DATA_ROOT, modality, 'reports', difficulty)
    for name in candidate_names:
        ehr_path = os.path.join(reports_dir, name)
        if os.path.exists(ehr_path):
            with open(ehr_path, 'r') as f:
                return f.read().strip()
    return "Report not found"

def get_doctor_file_path(doctor_id, modality):
    """Get the file path for a doctor's labels for a specific modality"""
    modality_dir = os.path.join(LABELS_PATH, modality)
    os.makedirs(modality_dir, exist_ok=True)
    return os.path.join(modality_dir, f"doctor_{doctor_id}.json")

def load_doctor_labels(doctor_id, modality):
    """Load existing labels for a doctor and modality"""
    file_path = get_doctor_file_path(doctor_id, modality)
    if os.path.exists(file_path):
        with open(file_path, 'r') as f:
            return json.load(f)
    return {}

def save_doctor_labels(doctor_id, modality, labels):
    """Save labels for a doctor and modality"""
    file_path = get_doctor_file_path(doctor_id, modality)
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
        image_path = os.path.join(DATA_ROOT, image_data['modality'], 'images', image_data.get('difficulty', ''), image_data['filename'])
        
        if os.path.exists(image_path):
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
    
    # Ensure data directories exist
    ensure_data_directories_exist()

    # Modality selection
    modality = st.sidebar.selectbox("Select Modality", MODALITIES, index=0)

    # Load data for selected modality
    image_data_list = load_image_data(modality)
    doctor_labels = load_doctor_labels(doctor_id, modality)
    
    # Doctor info sidebar
    # Labels are already scoped per modality file
    doctor_labels_current = doctor_labels

    st.sidebar.markdown(f"""
    <div class="doctor-info">
        <h4>👨‍⚕️ Doctor Information</h4>
        <p><strong>ID:</strong> {doctor_hash}</p>
        <p><strong>Modality:</strong> {modality}</p>
        <p><strong>Images Labeled (this modality):</strong> {len(doctor_labels_current)}</p>
        <p><strong>Total Images (this modality):</strong> {len(image_data_list)}</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Progress tracking
    progress = len(doctor_labels_current) / len(image_data_list) if image_data_list else 0
    st.sidebar.markdown("### 📈 Progress")
    st.sidebar.progress(progress)
    st.sidebar.write(f"{len(doctor_labels_current)} / {len(image_data_list)} images labeled ({progress:.1%})")
    
    # Find next unlabeled image
    def make_label_key(difficulty, filename):
        return f"{difficulty}/{filename}"

    unlabeled_images = [img for img in image_data_list if make_label_key(img['difficulty'], img['filename']) not in doctor_labels]
    
    if not unlabeled_images:
        st.success(f"🎉 Congratulations! You have labeled all images for {modality}.")
        st.markdown(f"### 📊 Your Labeling Summary — {modality}")
        
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
        
        # Always show previous labels management when all images are labeled
        st.markdown("---")
        show_previous_labels(doctor_labels, doctor_id, modality)
        return
    
    # Display current image
    current_image = unlabeled_images[0]
    ehr_text = load_ehr_text(current_image['filename'], modality, current_image['difficulty'])
    
    st.markdown("### Current Image")
    
    # Display image and EHR
    display_image_and_ehr(current_image, ehr_text)
    
    # Difficulty rating interface
    st.markdown("### 🎯 Difficulty Rating")
    st.markdown("**How difficult is it to detect that this image is a deepfake?**")
    
    col1, col2, col3 = st.columns(3)
    
    
    with col1:
        if st.button("🟢 Easy", use_container_width=True): 
            save_label(doctor_id, modality, make_label_key(current_image['difficulty'], current_image['filename']), "easy", current_image, ehr_text)
            st.rerun()
    
    with col2:
        if st.button("🟡 Medium", use_container_width=True):
            save_label(doctor_id, modality, make_label_key(current_image['difficulty'], current_image['filename']), "medium", current_image, ehr_text)
            st.rerun()
    
    with col3:
        if st.button("🔴 Hard", use_container_width=True):
            save_label(doctor_id, modality, make_label_key(current_image['difficulty'], current_image['filename']), "hard", current_image, ehr_text)
            st.rerun()
    
    # Additional options
    st.markdown("### 📝 Additional Options")
    
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("⏭️ Skip This Image", use_container_width=True):
            save_label(doctor_id, modality, make_label_key(current_image['difficulty'], current_image['filename']), "skipped", current_image, ehr_text)
            st.rerun()
    
    with col2:
        if st.button("🔄 View Previous Labels", use_container_width=True):
            show_previous_labels(doctor_labels, doctor_id, modality)

def save_label(doctor_id, modality, label_key, difficulty, image_data, ehr_text):
    """Save a label for the current image"""
    doctor_labels = load_doctor_labels(doctor_id, modality)
    
    label_data = {
        'doctor_difficulty': difficulty,
        'timestamp': datetime.datetime.now().isoformat(),
        'modality': image_data.get('modality'),
        'difficulty': image_data.get('difficulty'),
        'filename': image_data.get('filename'),
        'ehr_text': ehr_text
    }
    
    doctor_labels[label_key] = label_data
    save_doctor_labels(doctor_id, modality, doctor_labels)
    
    st.success(f"✅ Label saved: {difficulty.replace('_', ' ').title()}")

def delete_label(doctor_id, modality, label_key):
    """Delete a label for a specific image"""
    doctor_labels = load_doctor_labels(doctor_id, modality)
    if label_key in doctor_labels:
        del doctor_labels[label_key]
        save_doctor_labels(doctor_id, modality, doctor_labels)
        st.success(f"✅ Label deleted for {label_key}")
        return True
    return False

def show_previous_labels(doctor_labels, doctor_id, modality):
    """Show previous labels in an expandable section with embedded editing UI"""
    if not doctor_labels:
        st.info("No previous labels found.")
        return
    
    st.markdown("### 📋 Previous Labels")
    st.markdown(f"**Modality:** {modality} | **Total Labels:** {len(doctor_labels)}")
    
    for label_key, label_data in list(doctor_labels.items())[-20:]:  # Show last 20
        with st.expander(f"{label_key} - {label_data['doctor_difficulty'].replace('_', ' ').title()}"):
            # Show label information
            st.write(f"**Current Rating:** {label_data['doctor_difficulty'].replace('_', ' ').title()}")
            st.write(f"**Timestamp:** {label_data['timestamp']}")
            st.write(f"**Difficulty:** {label_data.get('difficulty', 'N/A')}")
            st.write(f"**File:** {label_data.get('filename', 'N/A')}")
            
            # Reconstruct image data for display
            difficulty, filename = label_key.split('/', 1)
            image_data = {
                'filename': filename,
                'modality': modality,
                'difficulty': difficulty
            }
            
            # Load the report text
            ehr_text = load_ehr_text(filename, modality, difficulty)
            
            # Display image and report
            display_image_and_ehr(image_data, ehr_text)
            
            # Embedded editing UI
            st.markdown("### 🎯 Change Rating")
            st.markdown("**How difficult is it to detect that this image is a deepfake?**")
            
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                if st.button("🟢 Easy", key=f"edit_easy_{label_key}"):
                    update_label_rating(doctor_id, modality, label_key, "easy")
                    st.rerun()
            
            with col2:
                if st.button("🟡 Medium", key=f"edit_medium_{label_key}"):
                    update_label_rating(doctor_id, modality, label_key, "medium")
                    st.rerun()
            
            with col3:
                if st.button("🔴 Hard", key=f"edit_hard_{label_key}"):
                    update_label_rating(doctor_id, modality, label_key, "hard")
                    st.rerun()
            
            with col4:
                if st.button("⏭️ Skip", key=f"edit_skip_{label_key}"):
                    update_label_rating(doctor_id, modality, label_key, "skipped")
                    st.rerun()

def update_label_rating(doctor_id, modality, label_key, new_rating):
    """Update the rating for an existing label"""
    doctor_labels = load_doctor_labels(doctor_id, modality)
    if label_key in doctor_labels:
        doctor_labels[label_key]['doctor_difficulty'] = new_rating
        doctor_labels[label_key]['timestamp'] = datetime.datetime.now().isoformat()
        save_doctor_labels(doctor_id, modality, doctor_labels)
        st.success(f"✅ Label updated to: {new_rating.replace('_', ' ').title()}")

if __name__ == "__main__":
    main()

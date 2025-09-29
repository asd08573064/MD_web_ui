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
MODALITIES = ['CXR', 'MRI', 'CT', 'Pathology']
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

def display_image_and_ehr(image_data, ehr_text, editable=False, key=None):
    """Display the image and EHR text. If editable=True, show a text area and return the edited text."""
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.markdown("### 📸 Medical Image")
        image_path = os.path.join(DATA_ROOT, image_data['modality'], 'images', image_data.get('difficulty', ''), image_data['filename'])
        
        if os.path.exists(image_path):
            image = Image.open(image_path)
            st.image(image, width='stretch')
        else:
            st.error(f"Image not found: {image_data['filename']}")
    
    with col2:
        st.markdown("### 📋 EHR Information")
        if editable:
            st.caption("This report is editable by the doctor")
            edited = st.text_area(
                "EHR (Editable)",
                value=ehr_text or "",
                height=200,
                key=key if key else None
            )
            return edited
        else:
            st.markdown(f'<div class="ehr-text">{ehr_text}</div>', unsafe_allow_html=True)
            return ehr_text

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
    
    # Check if we should show previous labels
    if st.session_state.get('show_previous_labels', False):
        st.markdown("### 📋 Previous Labels")
        # Reload labels to ensure we have the latest data
        current_doctor_labels = load_doctor_labels(doctor_id, modality)
        show_previous_labels(current_doctor_labels, doctor_id, modality)
        
        # Add button to go back to labeling
        if st.button("← Back to Labeling", width='stretch'):
            st.session_state.show_previous_labels = False
            st.rerun()
        return
    
    # Find next unlabeled image
    def make_label_key(difficulty, filename):
        return f"{difficulty}/{filename}"

    unlabeled_images = [img for img in image_data_list if make_label_key(img['difficulty'], img['filename']) not in doctor_labels]
    
    if not unlabeled_images:
        st.success(f"🎉 Congratulations! You have labeled all images for {modality}.")
        st.markdown(f"### 📊 Your Labeling Summary — {modality}")
        
        # Show summary statistics
        if doctor_labels:
            confidence_counts = {}
            for filename, label_data in doctor_labels.items():
                confidence = label_data.get('doctor_confidence') or label_data.get('doctor_difficulty') or 'Unknown'
                confidence_counts[confidence] = confidence_counts.get(confidence, 0) + 1
            
            col1, col2, col3 = st.columns(3)
            for i, (confidence, count) in enumerate(confidence_counts.items()):
                with [col1, col2, col3][i % 3]:
                    st.metric(f"{str(confidence).replace('_', ' ').title()} Confidence", count)
        
        # Always show previous labels management when all images are labeled
        st.markdown("---")
        # Reload labels to ensure we have the latest data
        current_doctor_labels = load_doctor_labels(doctor_id, modality)
        show_previous_labels(current_doctor_labels, doctor_id, modality)
        return
    
    # Display current image
    current_image = unlabeled_images[0]
    ehr_text = load_ehr_text(current_image['filename'], modality, current_image['difficulty'])
    # Prefer edited EHR if already saved for this image
    current_label_key = make_label_key(current_image['difficulty'], current_image['filename'])
    existing_label = doctor_labels.get(current_label_key)
    if existing_label:
        saved_ehr_text = existing_label.get('ehr_text')
        if saved_ehr_text:
            ehr_text = saved_ehr_text
    
    st.markdown("### Current Image")
    
    # Display image and EHR (EHR editable)
    ehr_key = f"ehr_{current_image['filename']}_{current_image['difficulty']}"
    ehr_text = display_image_and_ehr(current_image, ehr_text, editable=True, key=ehr_key)
    
    # Confidence rating interface
    st.markdown("### 🎯 Deepfake Confidence Rating")
    st.markdown("**How confident are you that this image is AI-generated (deepfake)?**")
    st.caption("Guidance: 1) Very Low: almost certainly real; 2) Low: likely real; 3) Medium: unsure; 4) High: likely deepfake; 5) Very High: almost certainly deepfake. Use Drop only if this image is too synthetic/invalid to include in the study.")
    
    # Add reasoning text input with unique key per image
    reasoning_key = f"reasoning_{current_image['filename']}_{current_image['difficulty']}"
    reasoning = st.text_area(
        "💭 Reasoning (Optional):",
        placeholder="Explain your decision... What makes this image easy/medium/hard to detect as a deepfake?",
        height=100,
        key=reasoning_key
    )
    
    col1, col2, col3, col4, col5 = st.columns(5)
    
    
    with col1:
        if st.button("1️⃣ Very Low", width='stretch'): 
            save_label(doctor_id, modality, make_label_key(current_image['difficulty'], current_image['filename']), "very_low", current_image, ehr_text, reasoning)
            st.rerun()
    
    with col2:
        if st.button("2️⃣ Low", width='stretch'):
            save_label(doctor_id, modality, make_label_key(current_image['difficulty'], current_image['filename']), "low", current_image, ehr_text, reasoning)
            st.rerun()
    
    with col3:
        if st.button("3️⃣ Medium", width='stretch'):
            save_label(doctor_id, modality, make_label_key(current_image['difficulty'], current_image['filename']), "medium", current_image, ehr_text, reasoning)
            st.rerun()

    with col4:
        if st.button("4️⃣ High", width='stretch'):
            save_label(doctor_id, modality, make_label_key(current_image['difficulty'], current_image['filename']), "high", current_image, ehr_text, reasoning)
            st.rerun()

    with col5:
        if st.button("5️⃣ Very High", width='stretch'):
            save_label(doctor_id, modality, make_label_key(current_image['difficulty'], current_image['filename']), "very_high", current_image, ehr_text, reasoning)
            st.rerun()
    
    # Additional options
    st.markdown("### 📝 Additional Options")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("⏭️ Skip This Image", width='stretch'):
            save_label(doctor_id, modality, make_label_key(current_image['difficulty'], current_image['filename']), "skipped", current_image, ehr_text, reasoning)
            st.rerun()
    
    with col2:
        if st.button("🗑️ Drop (Too fake to include)", width='stretch'):
            save_label(doctor_id, modality, make_label_key(current_image['difficulty'], current_image['filename']), "dropped", current_image, ehr_text, reasoning)
            st.rerun()

    with col3:
        if st.button("🔄 View Previous Labels", width='stretch'):
            # Set session state to show previous labels
            st.session_state.show_previous_labels = True
            st.rerun()

def save_label(doctor_id, modality, label_key, difficulty, image_data, ehr_text, reasoning=""):
    """Save a label for the current image"""
    
    print(f"Saving label: {label_key}, {difficulty}, {image_data}, {ehr_text}, {reasoning}")
    doctor_labels = load_doctor_labels(doctor_id, modality)
    
    label_data = {
        'doctor_confidence': difficulty,
        'timestamp': datetime.datetime.now().isoformat(),
        'modality': image_data.get('modality'),
        'difficulty': image_data.get('difficulty'),
        'filename': image_data.get('filename'),
        'ehr_text': ehr_text,
        'reasoning': reasoning.strip() if reasoning else ""
    }
    
    doctor_labels[label_key] = label_data
    save_doctor_labels(doctor_id, modality, doctor_labels)
    
    st.success(f"✅ Saved: Confidence = {difficulty.replace('_', ' ').title()}")

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
    
    for i, (label_key, label_data) in enumerate(list(doctor_labels.items())[-20:], 1):  # Show last 20
        title_conf = (label_data.get('doctor_confidence') or label_data.get('doctor_difficulty') or 'unknown')
        with st.expander(f"Image {i} - {str(title_conf).replace('_', ' ').title()}"):
            # Show label information
            conf = label_data.get('doctor_confidence') or label_data.get('doctor_difficulty') or 'unknown'
            st.write(f"**Current Confidence:** {str(conf).replace('_', ' ').title()}")
            st.write(f"**Timestamp:** {label_data['timestamp']}")
            
            # Show reasoning if available
            reasoning = label_data.get('reasoning', '')
            if reasoning:
                st.write(f"**Reasoning:** {reasoning}")
            
            # Reconstruct image data for display
            difficulty, filename = label_key.split('/', 1)
            image_data = {
                'filename': filename,
                'modality': modality,
                'difficulty': difficulty
            }
            
            # Load the report text and prefer edited EHR from JSON if present
            ehr_text = load_ehr_text(filename, modality, difficulty)
            saved = doctor_labels.get(label_key)
            if saved and saved.get('ehr_text'):
                ehr_text = saved.get('ehr_text')
            
            # Display image and report
            # Display image and EHR (EHR editable in edit view)
            ehr_edit_key = f"ehr_edit_{label_key}"
            ehr_text = display_image_and_ehr(image_data, ehr_text, editable=True, key=ehr_edit_key)
            
            # Embedded editing UI
            st.markdown("### 🎯 Change Confidence")
            st.markdown("**How confident are you that this image is AI-generated (deepfake)?**")
            st.caption("Guidance: 1) Very Low: almost certainly real; 2) Low: likely real; 3) Medium: unsure; 4) High: likely deepfake; 5) Very High: almost certainly deepfake. Use Drop only if this image is too synthetic/invalid to include in the study.")
            
            # Add reasoning text input for editing
            edit_reasoning = st.text_area(
                "💭 Update Reasoning (Optional):",
                value=reasoning,
                placeholder="Explain your decision... What makes this image easy/medium/hard to detect as a deepfake?",
                height=80,
                key=f"edit_reasoning_{label_key}"
            )
            
            # Save EHR without changing the current confidence
            current_conf = label_data.get('doctor_confidence') or label_data.get('doctor_difficulty') or 'medium'
            if st.button("💾 Save EHR Only", key=f"save_ehr_only_{label_key}"):
                save_label(doctor_id, modality, label_key, current_conf, image_data, ehr_text, edit_reasoning)
                st.rerun()
            
            col1, col2, col3, col4, col5, col6 = st.columns(6)
            
            with col1:
                if st.button("1️⃣ Very Low", key=f"edit_vlow_{label_key}"):
                    save_label(doctor_id, modality, label_key, "very_low", image_data, ehr_text, edit_reasoning)
                    st.rerun()
            
            with col2:
                if st.button("2️⃣ Low", key=f"edit_low_{label_key}"):
                    save_label(doctor_id, modality, label_key, "low", image_data, ehr_text, edit_reasoning)
                    st.rerun()
            
            with col3:
                if st.button("3️⃣ Medium", key=f"edit_med_{label_key}"):
                    save_label(doctor_id, modality, label_key, "medium", image_data, ehr_text, edit_reasoning)
                    st.rerun()

            with col4:
                if st.button("4️⃣ High", key=f"edit_high_{label_key}"):
                    save_label(doctor_id, modality, label_key, "high", image_data, ehr_text, edit_reasoning)
                    st.rerun()

            with col5:
                if st.button("5️⃣ Very High", key=f"edit_vhigh_{label_key}"):
                    save_label(doctor_id, modality, label_key, "very_high", image_data, ehr_text, edit_reasoning)
                    st.rerun()

            with col6:
                if st.button("🗑️ Drop", key=f"edit_drop_{label_key}"):
                    save_label(doctor_id, modality, label_key, "dropped", image_data, ehr_text, edit_reasoning)
                    st.rerun()

if __name__ == "__main__":
    main()

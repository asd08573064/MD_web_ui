# Medical Deepfake Difficulty Labeling Application

A Streamlit web application for medical professionals to label the difficulty of detecting deepfake medical images.

## Features

- 🔐 **Whitelist Authentication**: Only pre-authorized doctor IDs can access the system
- 🖼️ **Image Display**: View medical images with corresponding EHR text
- 🎯 **Difficulty Rating**: 5-point scale from "Very Easy" to "Very Hard"
- 📊 **Progress Tracking**: Real-time progress monitoring
- 💾 **Individual Storage**: Each doctor's labels saved to separate JSON files
- 📈 **Statistics**: View labeling summary and previous labels
- 🛡️ **Security**: Doctor IDs are hashed for privacy

## Installation

### Option 1: Docker (Recommended)

1. **Prerequisites:**
   - Docker and Docker Compose installed
   - Data directories (`out_scm_tts` and `out_scm_tts_ehr`) in place

2. **Quick Start:**
```bash
# Run the application with Docker
./docker-run.sh
```

3. **Manual Docker Commands:**
```bash
# Build and run
docker-compose up --build -d

# View logs
docker-compose logs -f

# Stop application
docker-compose down
```

### Option 2: Local Python Installation

1. Install required dependencies:
```bash
pip install -r requirements.txt
```

2. Ensure your data structure is as follows:
```
project/
├── out_scm_tts/
│   ├── easy/
│   │   ├── *.png files
│   │   └── results_easy.csv
│   ├── medium/
│   │   ├── *.png files
│   │   └── results_medium.csv
│   └── hard/
│       ├── *.png files
│       └── results_hard.csv
├── out_scm_tts_ehr/
│   ├── easy/
│   │   └── *.ehr.txt files
│   ├── medium/
│   │   └── *.ehr.txt files
│   └── hard/
│       └── *.ehr.txt files
└── app.py
```

## Usage

### Docker Usage

1. **Start the application:**
```bash
./docker-run.sh
```

2. **Access the application:**
   - Open your browser to `http://localhost:8501`

3. **View doctor IDs:**
```bash
docker-compose exec medical-labeling-app python show_doctor_ids.py
```

### Local Python Usage

1. **Start the application:**
```bash
streamlit run app.py
```

2. **Access the application:**
   - Open your browser to `http://localhost:8501`

3. Enter your authorized Doctor ID in the sidebar (see Doctor IDs section below)

4. Review each medical image and corresponding EHR text

5. Rate the difficulty of detecting if the image is a deepfake using the 5-point scale:
   - 🟢 Very Easy
   - 🟡 Easy
   - 🟠 Medium
   - 🔴 Hard
   - ⚫ Very Hard

6. Your labels are automatically saved to `doctor_labels/doctor_{your_id}.json`

## Authorized Doctor IDs

The system uses a whitelist of pre-authorized doctor IDs. To view the current list:

```bash
python show_doctor_ids.py
```

**Important:** Only these IDs can access the labeling system. Contact the administrator if you need access.

## Data Structure

### Input Data
- **Images**: PNG files in `out_scm_tts/{difficulty}/` folders
- **EHR Text**: Text files in `out_scm_tts_ehr/{difficulty}/` folders
- **Metadata**: CSV files with image properties and scores

### Output Data
Each doctor's labels are saved as JSON files with the following structure:
```json
{
  "filename.png": {
    "doctor_difficulty": "medium",
    "timestamp": "2024-01-01T12:00:00",
    "original_difficulty": "easy",
    "seed": 12345,
    "ehr_text": "AGE: 25\nSEX: Male\n...",
    "metadata": {
      "scm_realism": 0.595,
      "scm_artifact": 0.203,
      "scm_symmetry": 0.803,
      "scm_noise_cv": 1.000,
      "scm_vessel_decay": 0.165,
      "accepted": true,
      "objective": 0.167
    }
  }
}
```

## Security Features

- **Whitelist Authentication**: Only pre-authorized doctor IDs can access the system
- **Doctor ID Hashing**: IDs are hashed for privacy in the system
- **Individual Storage**: Each doctor's labels stored in separate JSON files
- **No Database**: File-based storage for simplicity
- **Access Control**: Invalid IDs are rejected with clear error messages

## Deployment

### AWS Deployment (Docker)

1. **Upload files to EC2 instance:**
   - Upload all project files to your EC2 instance
   - Ensure data directories (`out_scm_tts` and `out_scm_tts_ehr`) are included

2. **Deploy with Docker:**
```bash
# Run the AWS deployment script
./aws-deploy.sh
```

3. **Configure Security Group:**
   - Allow inbound traffic on port 8501
   - Restrict access to authorized IPs if needed

4. **Access the application:**
   - `http://YOUR_EC2_PUBLIC_IP:8501`

### Manual AWS Deployment

1. **Install Docker on EC2:**
```bash
sudo yum update -y
sudo yum install -y docker
sudo service docker start
sudo usermod -a -G docker ec2-user
```

2. **Install Docker Compose:**
```bash
sudo curl -L "https://github.com/docker/compose/releases/download/1.29.2/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose
```

3. **Deploy the application:**
```bash
docker-compose -f docker-compose.prod.yml up --build -d
```

### Local Deployment

The application can also be deployed locally using Docker or direct Python installation. The file-based storage system makes it easy to deploy without requiring a database setup.

## Troubleshooting

### General Issues
- **Images not loading**: Check that the `out_scm_tts` folder structure matches the expected format
- **EHR text not found**: Ensure `.ehr.txt` files exist in the `out_scm_tts_ehr` folders
- **Labels not saving**: Check write permissions in the `doctor_labels` directory

### Docker Issues
- **Container won't start**: Check logs with `docker-compose logs`
- **Port already in use**: Stop other services using port 8501 or change the port in docker-compose.yml
- **Permission denied**: Ensure Docker has proper permissions and data directories are accessible
- **Out of memory**: Increase Docker memory limits or use a larger EC2 instance

### AWS Deployment Issues
- **Can't access from browser**: Check EC2 security group allows port 8501
- **Container keeps restarting**: Check logs and ensure data directories are properly mounted
- **Performance issues**: Consider using a larger EC2 instance or optimizing Docker resources

## Support

For issues or questions, please contact the research team.

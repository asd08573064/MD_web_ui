#!/usr/bin/env python3
"""
Script to display the authorized doctor IDs for distribution to medical professionals.
"""

import json
import os

def show_doctor_ids():
    """Display the authorized doctor IDs"""
    whitelist_path = "doctor_whitelist.json"
    
    if not os.path.exists(whitelist_path):
        print("❌ Error: doctor_whitelist.json not found!")
        return
    
    with open(whitelist_path, 'r') as f:
        data = json.load(f)
    
    print("🏥 Medical Deepfake Labeling - Authorized Doctor IDs")
    print("=" * 60)
    print(f"Total authorized doctors: {data['total_doctors']}")
    print(f"Created: {data['created']}")
    print()
    print("📋 Doctor IDs to distribute:")
    print("-" * 30)
    
    for i, doctor_id in enumerate(data['whitelist'], 1):
        print(f"{i:2d}. {doctor_id}")
    
    print()
    print("🔐 Security Notes:")
    print("- These IDs are case-sensitive")
    print("- Each doctor should use their assigned ID only")
    print("- IDs are hashed for privacy in the system")
    print("- Contact administrator if access is needed")

if __name__ == "__main__":
    show_doctor_ids()

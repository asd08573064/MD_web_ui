#!/usr/bin/env python3
"""
Doctor Whitelist Generator for Medical Deepfake Labeling Application

This script generates a doctor_whitelist.json file with authorized doctor IDs
for the medical deepfake labeling system.

Usage:
    python generate_doctor_whitelist.py [options]

Options:
    --interactive    Interactive mode to manually enter doctor IDs
    --random N       Generate N random doctor IDs
    --from-file FILE Import doctor IDs from a text file (one per line)
    --from-csv FILE  Import doctor IDs from a CSV file
    --pattern PAT    Custom pattern for random IDs (default: "DOC{number}")
    --output FILE    Output file (default: doctor_whitelist.json)
    --help           Show this help message
"""

import json
import os
import sys
import argparse
import random
import string
import csv
from datetime import datetime
from pathlib import Path

class DoctorWhitelistGenerator:
    def __init__(self):
        self.whitelist = []
        self.created_time = datetime.now().isoformat()
    
    def add_doctor_id(self, doctor_id):
        """Add a doctor ID to the whitelist if it's not already present"""
        if doctor_id.strip() and doctor_id not in self.whitelist:
            self.whitelist.append(doctor_id.strip())
            return True
        return False
    
    def generate_random_id(self, pattern="DOC{number}", number=None):
        """Generate a random doctor ID based on pattern"""
        if number is None:
            number = random.randint(1000, 9999)
        
        # Replace placeholders in pattern
        id_str = pattern.replace("{number}", str(number))
        id_str = id_str.replace("{random}", ''.join(random.choices(string.ascii_uppercase + string.digits, k=4)))
        id_str = id_str.replace("{letter}", random.choice(string.ascii_uppercase))
        
        return id_str
    
    def generate_random_ids(self, count, pattern="DOC{number}"):
        """Generate multiple random doctor IDs"""
        generated = []
        attempts = 0
        max_attempts = count * 10  # Prevent infinite loops
        
        while len(generated) < count and attempts < max_attempts:
            attempts += 1
            new_id = self.generate_random_id(pattern)
            if new_id not in generated and new_id not in self.whitelist:
                generated.append(new_id)
        
        return generated
    
    def load_from_file(self, filename):
        """Load doctor IDs from a text file (one per line)"""
        try:
            with open(filename, 'r', encoding='utf-8') as f:
                lines = f.readlines()
            
            added_count = 0
            for line in lines:
                if self.add_doctor_id(line.strip()):
                    added_count += 1
            
            return added_count
        except FileNotFoundError:
            print(f"❌ Error: File '{filename}' not found!")
            return 0
        except Exception as e:
            print(f"❌ Error reading file '{filename}': {e}")
            return 0
    
    def load_from_csv(self, filename, column=0):
        """Load doctor IDs from a CSV file"""
        try:
            with open(filename, 'r', encoding='utf-8') as f:
                reader = csv.reader(f)
                rows = list(reader)
            
            added_count = 0
            for row in rows:
                if len(row) > column:
                    if self.add_doctor_id(row[column]):
                        added_count += 1
            
            return added_count
        except FileNotFoundError:
            print(f"❌ Error: File '{filename}' not found!")
            return 0
        except Exception as e:
            print(f"❌ Error reading CSV file '{filename}': {e}")
            return 0
    
    def interactive_mode(self):
        """Interactive mode to manually enter doctor IDs"""
        print("🏥 Interactive Doctor ID Entry Mode")
        print("=" * 40)
        print("Enter doctor IDs one at a time. Press Enter on empty line to finish.")
        print()
        
        while True:
            doctor_id = input("Enter Doctor ID (or press Enter to finish): ").strip()
            
            if not doctor_id:
                break
            
            if self.add_doctor_id(doctor_id):
                print(f"✅ Added: {doctor_id}")
            else:
                print(f"⚠️  Skipped (duplicate or empty): {doctor_id}")
        
        print(f"\n📋 Total doctor IDs entered: {len(self.whitelist)}")
    
    def save_whitelist(self, output_file="doctor_whitelist.json"):
        """Save the whitelist to a JSON file"""
        data = {
            "created": self.created_time,
            "total_doctors": len(self.whitelist),
            "whitelist": sorted(self.whitelist)  # Sort for consistency
        }
        
        try:
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            
            print(f"✅ Whitelist saved to: {output_file}")
            print(f"📊 Total doctors: {len(self.whitelist)}")
            return True
        except Exception as e:
            print(f"❌ Error saving whitelist: {e}")
            return False
    
    def display_whitelist(self):
        """Display the current whitelist"""
        if not self.whitelist:
            print("📋 No doctor IDs in whitelist")
            return
        
        print("🏥 Current Doctor Whitelist")
        print("=" * 30)
        for i, doctor_id in enumerate(sorted(self.whitelist), 1):
            print(f"{i:2d}. {doctor_id}")
        print(f"\nTotal: {len(self.whitelist)} doctors")

def main():
    parser = argparse.ArgumentParser(
        description="Generate doctor whitelist for Medical Deepfake Labeling Application",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Interactive mode
  python generate_doctor_whitelist.py --interactive
  
  # Generate 10 random IDs
  python generate_doctor_whitelist.py --random 10
  
  # Generate IDs with custom pattern
  python generate_doctor_whitelist.py --random 5 --pattern "MD{number}"
  
  # Import from text file
  python generate_doctor_whitelist.py --from-file doctors.txt
  
  # Import from CSV file
  python generate_doctor_whitelist.py --from-csv doctors.csv
  
  # Combine multiple sources
  python generate_doctor_whitelist.py --random 5 --from-file doctors.txt --output custom_whitelist.json
        """
    )
    
    parser.add_argument('--interactive', action='store_true',
                       help='Interactive mode to manually enter doctor IDs')
    parser.add_argument('--random', type=int, metavar='N',
                       help='Generate N random doctor IDs')
    parser.add_argument('--from-file', metavar='FILE',
                       help='Import doctor IDs from text file (one per line)')
    parser.add_argument('--from-csv', metavar='FILE',
                       help='Import doctor IDs from CSV file')
    parser.add_argument('--pattern', default='DOC{number}',
                       help='Pattern for random IDs (default: DOC{number})')
    parser.add_argument('--output', default='doctor_whitelist.json',
                       help='Output file (default: doctor_whitelist.json)')
    parser.add_argument('--show', action='store_true',
                       help='Display the generated whitelist')
    
    args = parser.parse_args()
    
    # If no arguments provided, show help
    if len(sys.argv) == 1:
        parser.print_help()
        return
    
    generator = DoctorWhitelistGenerator()
    
    # Process different input methods
    if args.interactive:
        generator.interactive_mode()
    
    if args.random:
        print(f"🎲 Generating {args.random} random doctor IDs with pattern: {args.pattern}")
        random_ids = generator.generate_random_ids(args.random, args.pattern)
        for doctor_id in random_ids:
            generator.add_doctor_id(doctor_id)
        print(f"✅ Generated {len(random_ids)} random IDs")
    
    if args.from_file:
        print(f"📁 Loading doctor IDs from file: {args.from_file}")
        added = generator.load_from_file(args.from_file)
        print(f"✅ Added {added} doctor IDs from file")
    
    if args.from_csv:
        print(f"📊 Loading doctor IDs from CSV: {args.from_csv}")
        added = generator.load_from_csv(args.from_csv)
        print(f"✅ Added {added} doctor IDs from CSV")
    
    # Save the whitelist
    if generator.whitelist:
        generator.save_whitelist(args.output)
        
        if args.show:
            print()
            generator.display_whitelist()
        
        print(f"\n🔐 Security Notes:")
        print(f"- Whitelist contains {len(generator.whitelist)} authorized doctor IDs")
        print(f"- IDs are case-sensitive")
        print(f"- Each doctor should use their assigned ID only")
        print(f"- IDs are hashed for privacy in the system")
        print(f"- File saved as: {args.output}")
        
        # Show how to use the whitelist
        print(f"\n📋 To view the whitelist later:")
        print(f"python show_doctor_ids.py")
        
    else:
        print("❌ No doctor IDs were added to the whitelist")
        print("Use --help to see available options")

if __name__ == "__main__":
    main()

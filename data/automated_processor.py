#!/usr/bin/env python3
"""
Automated GPS Scintillation Data Processor
This script runs every 15 minutes to:
1. Read GPS data files from local folder
2. Send them to the analysis API
3. Process the response and save as data.csv
4. Upload the result to GitHub
"""

import requests
import json
import csv
import pandas as pd
import base64
import os
import time
import schedule
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any

class AutomatedGPSProcessor:
    def __init__(self, config: Dict[str, Any]):
        """
        Initialize the automated processor
        
        Args:
            config: Configuration dictionary containing API endpoints, GitHub credentials, etc.
        """
        self.config = config
        self.data_folder = config['data_folder']
        self.api_url = config['api_url']
        self.github_token = config['github_token']
        self.github_owner = config['github_owner']
        self.github_repo = config['github_repo']
        
        # File paths
        self.lat_file = os.path.join(self.data_folder, "SN560_Lat_last15min.csv")
        self.lon_file = os.path.join(self.data_folder, "SN560_Lon_last15min.csv")
        self.s4c_file = os.path.join(self.data_folder, "SN560_S4C_last15min.csv")
        self.output_file = os.path.join(self.data_folder, "data.csv")
        
        # GitHub API setup
        self.github_headers = {
            'Accept': 'application/vnd.github+json',
            'Authorization': f'Bearer {self.github_token}',
            'X-GitHub-Api-Version': '2022-11-28'
        }
    
    def check_files_exist(self) -> bool:
        """Check if all required input files exist"""
        files_to_check = [self.lat_file, self.lon_file, self.s4c_file]
        
        for file_path in files_to_check:
            if not Path(file_path).exists():
                print(f"❌ Missing file: {file_path}")
                return False
                
        print("✅ All required files found")
        return True
    
    def send_to_analysis_api(self) -> Dict[str, Any]:
        """
        Send GPS data files to the analysis API
        
        Returns:
            API response as dictionary
        """
        print(f"📤 Sending files to analysis API: {self.api_url}")
        
        try:
            # Prepare files for multipart upload
            files = {
                's4c_file': ('SN560_S4C_last15min.csv', open(self.s4c_file, 'rb'), 'text/csv'),
                'lat_file': ('SN560_Lat_last15min.csv', open(self.lat_file, 'rb'), 'text/csv'),
                'lon_file': ('SN560_Lon_last15min.csv', open(self.lon_file, 'rb'), 'text/csv')
            }
            
            headers = {
                'accept': 'application/json'
            }
            
            # Make the POST request
            response = requests.post(self.api_url, headers=headers, files=files)
            
            # Close file handles
            for file_tuple in files.values():
                file_tuple[1].close()
            
            if response.status_code == 200:
                print("✅ Analysis API request successful")
                return response.json()
            else:
                print(f"❌ API request failed with status {response.status_code}")
                print(f"Response: {response.text}")
                return None
                
        except Exception as e:
            print(f"❌ Error calling analysis API: {e}")
            return None
    
    def extract_records_from_response(self, api_response: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Extract the records data from API response
        
        Args:
            api_response: The response from analysis API
            
        Returns:
            List of record dictionaries
        """
        try:
            records = api_response['transformed_data_result']['data']['records']
            print(f"✅ Extracted {len(records)} records from API response")
            return records
        except KeyError as e:
            print(f"❌ Error extracting records: Missing key {e}")
            return []
        except Exception as e:
            print(f"❌ Error extracting records: {e}")
            return []
    
    def save_as_csv(self, records: List[Dict[str, Any]]) -> bool:
        """
        Save records as CSV file
        
        Args:
            records: List of record dictionaries
            
        Returns:
            True if successful, False otherwise
        """
        if not records:
            print("❌ No records to save")
            return False
        
        try:
            # Convert to DataFrame for easier CSV handling
            df = pd.DataFrame(records)
            
            # Ensure columns are in the correct order
            column_order = ['Satellite', 'Time', 'S4C', 'Lat', 'Lon']
            df = df[column_order]
            
            # Save to CSV
            df.to_csv(self.output_file, index=False)
            print(f"✅ Saved {len(records)} records to {self.output_file}")
            return True
            
        except Exception as e:
            print(f"❌ Error saving CSV: {e}")
            return False
    
    def upload_to_github(self) -> bool:
        """
        Upload the data.csv file to GitHub
        
        Returns:
            True if successful, False otherwise
        """
        if not Path(self.output_file).exists():
            print(f"❌ Output file not found: {self.output_file}")
            return False
        
        try:
            # Read and encode file content
            with open(self.output_file, 'rb') as file:
                content = base64.b64encode(file.read()).decode('utf-8')
            
            # Check if file exists in repository
            repo_path = "data.csv"
            file_exists, current_sha = self.check_github_file_exists(repo_path)
            
            # Prepare API request
            url = f"https://api.github.com/repos/{self.github_owner}/{self.github_repo}/contents/{repo_path}"
            
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            data = {
                'message': f'Automated GPS scintillation data update - {timestamp}',
                'committer': {
                    'name': 'GPS Data Processor Bot',
                    'email': 'gps-processor@automated.com'
                },
                'content': content
            }
            
            # Add SHA if file exists (for updates)
            if file_exists:
                data['sha'] = current_sha
                print("📝 Updating existing file on GitHub...")
            else:
                print("📝 Creating new file on GitHub...")
            
            # Make API request
            response = requests.put(url, headers=self.github_headers, json=data)
            
            if response.status_code in [200, 201]:
                result = response.json()
                print(f"✅ Successfully uploaded to GitHub: {result['content']['html_url']}")
                return True
            else:
                print(f"❌ GitHub upload failed: {response.status_code}")
                print(f"Response: {response.text}")
                return False
                
        except Exception as e:
            print(f"❌ Error uploading to GitHub: {e}")
            return False
    
    def check_github_file_exists(self, file_path: str) -> tuple:
        """
        Check if file exists in GitHub repository
        
        Args:
            file_path: Path to file in repository
            
        Returns:
            tuple: (exists: bool, sha: str or None)
        """
        url = f"https://api.github.com/repos/{self.github_owner}/{self.github_repo}/contents/{file_path}"
        
        try:
            response = requests.get(url, headers=self.github_headers)
            if response.status_code == 200:
                return True, response.json()['sha']
            else:
                return False, None
        except Exception as e:
            print(f"Warning: Error checking GitHub file existence: {e}")
            return False, None
    
    def run_processing_cycle(self):
        """
        Run a complete processing cycle
        """
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        print(f"\n🚀 Starting GPS data processing cycle at {timestamp}")
        print("=" * 60)
        
        # Step 1: Check if files exist
        if not self.check_files_exist():
            print("❌ Processing cycle aborted: Missing required files")
            return False
        
        # Step 2: Send to analysis API
        api_response = self.send_to_analysis_api()
        if not api_response:
            print("❌ Processing cycle aborted: API call failed")
            return False
        
        # Step 3: Extract records from response
        records = self.extract_records_from_response(api_response)
        if not records:
            print("❌ Processing cycle aborted: No records extracted")
            return False
        
        # Step 4: Save as CSV
        if not self.save_as_csv(records):
            print("❌ Processing cycle aborted: Failed to save CSV")
            return False
        
        # Step 5: Upload to GitHub
        if not self.upload_to_github():
            print("❌ Processing cycle aborted: Failed to upload to GitHub")
            return False
        
        print("✅ Processing cycle completed successfully!")
        print("=" * 60)
        return True
    
    def start_scheduler(self):
        """
        Start the scheduled processing every 15 minutes
        """
        print("🕐 Starting automated GPS data processor...")
        print("📅 Schedule: Every 15 minutes")
        print("📁 Data folder:", self.data_folder)
        print("🌐 API endpoint:", self.api_url)
        print("📤 GitHub repo:", f"{self.github_owner}/{self.github_repo}")
        print("\nPress Ctrl+C to stop the scheduler\n")
        
        # Schedule the job every 15 minutes
        schedule.every(15).minutes.do(self.run_processing_cycle)
        
        # Run once immediately for testing
        print("🧪 Running initial test cycle...")
        self.run_processing_cycle()
        
        # Keep the scheduler running
        try:
            while True:
                schedule.run_pending()
                time.sleep(1)
        except KeyboardInterrupt:
            print("\n🛑 Scheduler stopped by user")


def main():
    """
    Main function to start the automated processor
    """
    # Configuration - UPDATE THESE VALUES
    config = {
        'data_folder': '/Users/user/Desktop/s4c-api-serives/data',
        'api_url': 'http://127.0.0.1:8000/analyze/',
        'github_token': 'xxxxxxxxx',
        'github_owner': 'Jaylaelike',
        'github_repo': 's4c-trajectory-project-app'
    }
    
    # Validate configuration
    if not config['github_token']:
        print("❌ Error: GitHub token not configured")
        return
    
    # Create and start processor
    processor = AutomatedGPSProcessor(config)
    processor.start_scheduler()


if __name__ == "__main__":
    main()


import requests
import base64
import os
import pandas as pd
from pathlib import Path
from datetime import datetime

class GitHubUploader:
    def __init__(self, token, owner, repo):
        """
        Initialize GitHub uploader
        
        Args:
            token (str): GitHub Personal Access Token
            owner (str): GitHub username or organization name
            repo (str): Repository name
        """
        self.token = token
        self.owner = owner
        self.repo = repo
        self.base_url = "https://api.github.com"
        self.headers = {
            'Authorization': f'Bearer {self.token}',
            'Accept': 'application/vnd.github+json'
        }
    
    def file_exists(self, file_path):
        """
        Check if file exists in repository and get its SHA
        
        Args:
            file_path (str): Path to file in repository
            
        Returns:
            tuple: (exists: bool, sha: str or None)
        """
        url = f"{self.base_url}/repos/{self.owner}/{self.repo}/contents/{file_path}"
        
        try:
            response = requests.get(url, headers=self.headers)
            if response.status_code == 200:
                return True, response.json()['sha']
            else:
                return False, None
        except Exception as e:
            print(f"Error checking file existence: {e}")
            return False, None
    
    def upload_csv(self, local_file_path, repo_file_path, commit_message=None):
        """
        Upload CSV file to GitHub repository
        
        Args:
            local_file_path (str): Path to local CSV file
            repo_file_path (str): Path where file should be stored in repo
            commit_message (str): Commit message (optional)
            
        Returns:
            dict: API response
        """
        # Validate local file exists
        if not Path(local_file_path).exists():
            raise FileNotFoundError(f"Local file not found: {local_file_path}")
        
        # Read and encode file content
        try:
            with open(local_file_path, 'rb') as file:
                content = base64.b64encode(file.read()).decode('utf-8')
        except Exception as e:
            raise Exception(f"Error reading file: {e}")
        
        # Set default commit message
        if not commit_message:
            file_name = Path(local_file_path).name
            commit_message = f"Upload {file_name}"
        
        # Check if file already exists
        file_exists, current_sha = self.file_exists(repo_file_path)
        
        # Prepare API request using GitHub API v2022-11-28 format
        url = f"{self.base_url}/repos/{self.owner}/{self.repo}/contents/{repo_file_path}"
        
        # Update headers to match the curl command format
        headers = {
            'Accept': 'application/vnd.github+json',
            'Authorization': f'Bearer {self.token}',
            'X-GitHub-Api-Version': '2022-11-28'
        }
        
        data = {
            'message': commit_message,
            'committer': {
                'name': 'CSV Uploader Bot',
                'email': 'uploader@example.com'
            },
            'content': content
        }
        
        # Add SHA if file exists (for updates)
        if file_exists:
            data['sha'] = current_sha
            print(f"File exists. Updating...")
        else:
            print(f"Creating new file...")
        
        # Make API request using PUT method (like curl -X PUT)
        try:
            response = requests.put(url, headers=headers, json=data)
            
            if response.status_code in [200, 201]:
                result = response.json()
                print(f"✅ Success! File uploaded to: {result['content']['html_url']}")
                return result
            else:
                print(f"❌ Error: {response.status_code}")
                print(f"Response: {response.text}")
                return None
                
        except Exception as e:
            print(f"❌ Request failed: {e}")
            return None
    
    def upload_multiple_csvs(self, file_mappings, base_commit_message="Upload CSV files"):
        """
        Upload multiple CSV files
        
        Args:
            file_mappings (dict): {local_path: repo_path} mappings
            base_commit_message (str): Base commit message
            
        Returns:
            list: Results for each upload
        """
        results = []
        
        for local_path, repo_path in file_mappings.items():
            print(f"\n📁 Uploading {local_path} → {repo_path}")
            
            file_name = Path(local_path).name
            commit_msg = f"{base_commit_message}: {file_name}"
            
            result = self.upload_csv(local_path, repo_path, commit_msg)
            results.append({
                'local_path': local_path,
                'repo_path': repo_path,
                'success': result is not None,
                'result': result
            })
        
        return results


def main():
    """
    Example usage of the GitHubUploader
    """
    
    # Configuration - REPLACE WITH YOUR VALUES
    GITHUB_TOKEN = 'xxxxxxxxxx'  # Set this environment variable
    OWNER = "Jaylaelike"  # Your GitHub username
    REPO = "s4c-trajectory-project-app"  # Your repository name
    
    # Validate token
    if not GITHUB_TOKEN:
        print("❌ Error: GITHUB_TOKEN environment variable not set")
        print("Set it with: export GITHUB_TOKEN=your_token_here")
        return
    
    # Initialize uploader
    uploader = GitHubUploader(GITHUB_TOKEN, OWNER, REPO)
    
    # Example 1: Upload single CSV file
    print("=== Single File Upload ===")
    try:
        result = uploader.upload_csv(
            local_file_path="data.csv",  # Local file path
            repo_file_path="data.csv",  # Path in repository
            commit_message="Add dataset for analysis"
        )
    except Exception as e:
        print(f"❌ Upload failed: {e}")
    
    # Example 2: Upload multiple CSV files including log_s4c_alert.csv
    print("\n=== Multiple Files Upload ===")
    file_mappings = {
        "data.csv": "data.csv",
        "log_s4c_alert.csv": "log_s4c_alert.csv"
    }
    
    results = uploader.upload_multiple_csvs(file_mappings)
    
    # Print summary
    print("\n=== Upload Summary ===")
    successful_uploads = [r for r in results if r['success']]
    print(f"✅ {len(successful_uploads)} files uploaded successfully")
    for result in results:
        status = "✅" if result['success'] else "❌"
        print(f"{status} {result['local_path']} → {result['repo_path']}")


if __name__ == "__main__":
    main()


# Alternative simple function for quick uploads
def filter_s4c_data(data_file="data.csv", alert_file="log_s4c_alert.csv"):
    """
    Filter data.csv for S4C >= 0.4 and create/update log_s4c_alert.csv
    with 60-day logic
    
    Args:
        data_file (str): Path to data CSV file
        alert_file (str): Path to alert CSV file
        
    Returns:
        bool: True if successful, False otherwise
    """
    try:
        # Check if data.csv exists
        if not os.path.exists(data_file):
            print(f"❌ {data_file} not found")
            return False
        
        # Read data.csv
        df = pd.read_csv(data_file)
        
        # Filter for S4C >= 0.4
        alert_df = df[df['S4C'] >= 0.4]
        
        if len(alert_df) == 0:
            print("No records with S4C >= 0.4 found")
            return True
        
        # Check if alert file exists and implement 60-day logic
        if os.path.exists(alert_file):
            # Read existing alert file
            existing_df = pd.read_csv(alert_file)
            
            if len(existing_df) > 0:
                # Check the date of the most recent record
                existing_df['Time'] = pd.to_datetime(existing_df['Time'])
                latest_record_date = existing_df['Time'].max()
                current_date = datetime.now()
                
                # Calculate days difference
                days_diff = (current_date - latest_record_date).days
                
                if days_diff <= 60:
                    # Less than or equal to 60 days, append new data
                    print(f"Latest record is {days_diff} days old. Appending new data.")
                    combined_df = pd.concat([existing_df, alert_df], ignore_index=True)
                    combined_df.to_csv(alert_file, index=False)
                else:
                    # More than 60 days, overwrite
                    print(f"Latest record is {days_diff} days old. Overwriting file.")
                    alert_df.to_csv(alert_file, index=False)
            else:
                # Empty file, just write new data
                alert_df.to_csv(alert_file, index=False)
        else:
            # File doesn't exist, create new
            alert_df.to_csv(alert_file, index=False)
        
        print(f"✅ Created/updated {alert_file} with {len(alert_df)} records (S4C >= 0.4)")
        return True
        
    except Exception as e:
        print(f"❌ Error filtering S4C data: {e}")
        return False


def quick_upload(token, owner, repo, local_file, repo_path, message=None):
    """
    Quick function to upload a single CSV file
    
    Args:
        token (str): GitHub token
        owner (str): Repository owner
        repo (str): Repository name
        local_file (str): Local file path
        repo_path (str): Repository file path
        message (str): Commit message
    """
    uploader = GitHubUploader(token, owner, repo)
    return uploader.upload_csv(local_file, repo_path, message)


# Example usage of quick function:
# quick_upload(
#     token=os.getenv('GITHUB_TOKEN'),
#     owner='your-username',
#     repo='your-repo',
#     local_file='data.csv',
#     repo_path='data/data.csv',
#     message='Upload CSV data'
# )
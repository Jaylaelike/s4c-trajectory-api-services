# GPS Scintillation Data Automation

This automation system processes GPS scintillation data every 15 minutes and uploads the results to GitHub.

## 📋 Task Checklist

- ✅ **Schedule auto run every 15 minutes** - Automated with Python `schedule` library
- ✅ **Get files from local folder** - Reads SN560_Lat_last15min.csv, SN560_Lon_last15min.csv, SN560_S4C_last15min.csv
- ✅ **POST to analysis API** - Sends curl request to http://127.0.0.1:8000/analyze/
- ✅ **Process response** - Extracts transformed_data_result.data.records
- ✅ **Save as data.csv** - Writes records to CSV with columns: Satellite, Time, S4C, Lat, Lon
- ✅ **Upload to GitHub** - Pushes data.csv to repository using GitHub API

## 🚀 Quick Start

1. **Install dependencies:**
   ```bash
   pip3 install -r requirements_automation.txt
   ```

2. **Start the API server** (in another terminal):
   ```bash
   cd /Users/user/Desktop/s4c-api-serives
   docker-compose up -d
   ```
   Or manually:
   ```bash
   cd backend && python main.py
   ```

3. **Run the automation:**
   ```bash
   ./run_automation.sh
   ```
   Or manually:
   ```bash
   python3 automated_processor.py
   ```

## 🧪 Testing

Test individual components before running the full automation:

```bash
python3 test_automation.py
```

This allows you to:
- Test API connection
- Test file processing
- Test GitHub upload
- Run a single processing cycle

## 📁 Files Overview

### Core Automation
- `automated_processor.py` - Main automation script
- `run_automation.sh` - Setup and run script
- `test_automation.py` - Testing utilities
- `requirements_automation.txt` - Python dependencies

### Input Files (Required)
- `SN560_Lat_last15min.csv` - Latitude data
- `SN560_Lon_last15min.csv` - Longitude data  
- `SN560_S4C_last15min.csv` - S4C scintillation data

### Output Files
- `data.csv` - Processed results in required format

## ⚙️ Configuration

Edit the `config` dictionary in `automated_processor.py`:

```python
config = {
    'data_folder': '/Users/user/Desktop/s4c-api-serives/data',
    'api_url': 'http://127.0.0.1:8000/analyze/',
    'github_token': 'your_github_token_here',
    'github_owner': 'your_username',
    'github_repo': 'your_repo_name'
}
```

## 🔄 Processing Flow

1. **File Check** - Verifies all 3 CSV files exist
2. **API Call** - Sends multipart POST request to analysis endpoint
3. **Response Processing** - Extracts records from API response
4. **CSV Generation** - Creates data.csv with processed results
5. **GitHub Upload** - Uploads data.csv to repository

## 📊 API Request Format

The automation sends this curl request:

```bash
curl --location 'http://127.0.0.1:8000/analyze/' \
--header 'accept: application/json' \
--form 's4c_file=@"SN560_S4C_last15min.csv"' \
--form 'lat_file=@"SN560_Lat_last15min.csv"' \
--form 'lon_file=@"SN560_Lon_last15min.csv"'
```

## 📈 Response Data Structure

The API returns:

```json
{
    "message": "Files processed successfully...",
    "analysis_complete": true,
    "transformed_data_result": {
        "status": "success",
        "data": {
            "records": [
                {
                    "Satellite": "G15",
                    "Time": "2025-06-11 09:32:10",
                    "S4C": 0.170506,
                    "Lat": 17.97266,
                    "Lon": 102.580338
                }
            ]
        }
    }
}
```

## 🔧 Troubleshooting

### Common Issues

1. **"Missing files" error**
   - Ensure all 3 CSV files exist in the data folder
   - Check file permissions

2. **"API call failed" error**
   - Verify the backend server is running
   - Check the API URL in configuration

3. **"GitHub upload failed" error**
   - Verify GitHub token has write permissions
   - Check repository name and owner

### Manual Testing

Run individual components:

```bash
# Test API connection only
python3 test_automation.py

# Run single cycle without scheduling
python3 -c "
from automated_processor import AutomatedGPSProcessor
config = {...}  # Your config
processor = AutomatedGPSProcessor(config)
processor.run_processing_cycle()
"
```

## 📅 Scheduling Options

### Current: Every 15 minutes
The script uses Python's `schedule` library and runs continuously.

### Alternative: Cron Job
Add to crontab for system-level scheduling:

```bash
# Edit crontab
crontab -e

# Add this line for every 15 minutes
*/15 * * * * /usr/bin/python3 /Users/user/Desktop/s4c-api-serives/data/automated_processor.py
```

### Alternative: macOS LaunchAgent
Create a plist file for macOS system scheduling.

## 🛡️ Security Notes

- GitHub token is stored in the script - consider using environment variables
- API endpoint is localhost - ensure proper network security
- File paths are absolute - adjust for different environments

## 📝 Logs

The automation provides detailed console output:
- ✅ Success indicators
- ❌ Error messages
- 📊 Processing statistics
- 🕐 Timestamps

Monitor the output to track processing status and identify issues.

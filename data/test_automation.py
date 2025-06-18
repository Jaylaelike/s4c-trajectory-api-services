#!/usr/bin/env python3
"""
Manual Test Script for GPS Data Processing
This script allows you to test individual components of the automation
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from automated_processor import AutomatedGPSProcessor

def test_api_connection():
    """Test if the analysis API is responding"""
    print("🧪 Testing API connection...")
    
    config = {
        'data_folder': '/Users/user/Desktop/s4c-api-serives/data',
        'api_url': 'http://127.0.0.1:8000/analyze/',
        'github_token': 'xxxxxxxxx',
        'github_owner': 'Jaylaelike',
        'github_repo': 's4c-trajectory-project-app'
    }
    
    processor = AutomatedGPSProcessor(config)
    
    # Test file existence
    print("\n1. Checking files...")
    files_exist = processor.check_files_exist()
    
    if not files_exist:
        print("❌ Files missing. Please ensure these files exist:")
        print("   - SN560_Lat_last15min.csv")
        print("   - SN560_Lon_last15min.csv") 
        print("   - SN560_S4C_last15min.csv")
        return False
    
    # Test API call
    print("\n2. Testing API call...")
    api_response = processor.send_to_analysis_api()
    
    if api_response:
        print("✅ API call successful!")
        
        # Test record extraction
        print("\n3. Testing record extraction...")
        records = processor.extract_records_from_response(api_response)
        
        if records:
            print(f"✅ Extracted {len(records)} records")
            print("Sample record:", records[0] if records else "None")
            
            # Test CSV saving
            print("\n4. Testing CSV save...")
            csv_saved = processor.save_as_csv(records)
            
            if csv_saved:
                print("✅ CSV saved successfully!")
                
                # Test GitHub upload
                print("\n5. Testing GitHub upload...")
                upload_success = processor.upload_to_github()
                
                if upload_success:
                    print("✅ GitHub upload successful!")
                    print("\n🎉 All tests passed!")
                    return True
                else:
                    print("❌ GitHub upload failed")
            else:
                print("❌ CSV save failed")
        else:
            print("❌ Record extraction failed")
    else:
        print("❌ API call failed")
    
    return False

def test_single_run():
    """Test a single processing cycle"""
    print("🧪 Testing single processing cycle...")
    
    config = {
        'data_folder': '/Users/user/Desktop/s4c-api-serives/data',
        'api_url': 'http://127.0.0.1:8000/analyze/',
        'github_token': 'xxxxxxxxx',
        'github_owner': 'Jaylaelike',
        'github_repo': 's4c-trajectory-project-app'
    }
    
    processor = AutomatedGPSProcessor(config)
    success = processor.run_processing_cycle()
    
    if success:
        print("\n🎉 Single processing cycle completed successfully!")
    else:
        print("\n❌ Processing cycle failed")
    
    return success

def main():
    print("🧪 GPS Data Processing Test Suite")
    print("=" * 40)
    
    while True:
        print("\nChoose a test:")
        print("1. Test API connection and components")
        print("2. Run single processing cycle")
        print("3. Exit")
        
        choice = input("\nEnter your choice (1-3): ").strip()
        
        if choice == "1":
            test_api_connection()
        elif choice == "2":
            test_single_run()
        elif choice == "3":
            print("👋 Goodbye!")
            break
        else:
            print("❌ Invalid choice. Please enter 1, 2, or 3.")

if __name__ == "__main__":
    main()

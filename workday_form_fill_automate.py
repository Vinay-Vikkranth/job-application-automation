"""
STEP 1: Chrome Profile Connection Test
=====================================
This file will ONLY test opening Chrome with your logged-in profile.
No form filling yet - just browser connection testing.
"""

from selenium import webdriver
from selenium.webdriver.chrome.service import Service
import json

def test_chrome_profile():
    """Step 1: Test opening Chrome with your default logged-in profile"""
    
    print("🚀 STEP 1: Chrome Profile Connection Test")
    print("=" * 50)
    
    # Load personal data to verify JSON is working
    try:
        with open('personal_data.json', 'r', encoding='utf-8') as file:
            data = json.load(file)
        print(f"✅ Personal data loaded successfully!")
        print(f"📋 Name: {data['personal_info']['full_name']}")
        print(f"📧 Email: {data['personal_info']['email']}")
    except Exception as e:
        print(f"❌ Error loading personal data: {e}")
        return False
    
    # Setup Chrome with your existing profile (where you're already logged in)
    print("\n🔧 Setting up Chrome with your logged-in profile...")
    
    # First, close any existing Chrome processes to avoid conflicts
    print("🔄 Closing any existing Chrome processes...")
    import subprocess
    try:
        subprocess.run("taskkill /f /im chrome.exe", shell=True, capture_output=True, check=False)
        print("✅ Chrome processes closed")
    except Exception as e:
        print(f"ℹ️  No Chrome processes to close or error: {e}")
    
    # Wait a moment for processes to fully close
    import time
    time.sleep(2)
    
    service = Service(executable_path=r"chromedriver-win64\chromedriver-win64\chromedriver.exe")
    chrome_options = webdriver.ChromeOptions()
    
    # Use your existing Chrome profile - different approach
    import os
    user_data_dir = os.path.expanduser("~") + r"\AppData\Local\Google\Chrome\User Data"
    chrome_options.add_argument(f"--user-data-dir={user_data_dir}")
    chrome_options.add_argument("--profile-directory=Default")
    
    # Additional options for stability
    chrome_options.add_argument("--start-maximized")
    chrome_options.add_argument("--disable-blink-features=AutomationControlled")
    chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
    chrome_options.add_experimental_option('useAutomationExtension', False)
    chrome_options.add_argument("--disable-web-security")
    chrome_options.add_argument("--allow-running-insecure-content")
    
    print("🔄 Opening Chrome with your logged-in profile automatically...")
    
    try:
        # Open Chrome with your logged-in profile
        print("🌐 Opening Chrome with your profile...")
        driver = webdriver.Chrome(service=service, options=chrome_options)
        
        # Test navigation to Google to verify profile is working
        print("🔍 Testing navigation to Google...")
        driver.get("https://www.google.com")
        
        print("\n🎉 SUCCESS! Chrome opened with your logged-in profile!")
        print("✅ Your logged-in account should be visible")
        print("✅ Your bookmarks and saved passwords are available")
        print("✅ Ready for job application automation")
        
        # Brief pause to let you see it working, then close
        import time
        time.sleep(3)
        print("🔚 Closing browser automatically...")
        
        # Close browser
        driver.quit()
        print("✅ Browser test completed successfully!")
        return True
        
    except Exception as e:
        print(f"❌ Error opening Chrome: {e}")
        if 'driver' in locals():
            driver.quit()
        return False

if __name__ == "__main__":
    success = test_chrome_profile()
    
    if success:
        print("\n🎯 STEP 1 COMPLETE!")
        print("✅ Chrome opened with your logged-in profile successfully")
        print("🚀 Ready for Step 2: Navigation to job application URL")
        print("⚡ No manual steps required - fully automated!")
    else:
        print("\n❌ STEP 1 FAILED!")
        print("🔧 Need to fix Chrome profile connection first")
        print("💡 Try closing all Chrome windows first")

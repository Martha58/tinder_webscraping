import requests
import os
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import re
import time

driver = webdriver.Edge()

url = 'https://tinder.com'
driver.get(url)

# Handle cookies pop-up
try:
    cookies = WebDriverWait(driver, 30).until(
        EC.element_to_be_clickable((By.XPATH, "//*[text()='I decline']"))
    )
    cookies.click()
except Exception as e:
    print(f"Cookies pop-up error: {e}")

# Click on the login button
try:
    login = WebDriverWait(driver, 30).until(
        EC.element_to_be_clickable((By.XPATH, "//*[text()='Log in']"))
    )
    login.click()
except Exception as e:
    print(f"Login button error: {e}")

# Click on the Facebook login button
try:
    facebook = WebDriverWait(driver, 30).until(
        EC.element_to_be_clickable((By.XPATH, "//*[text()='Log in with Facebook']"))
    )
    facebook.click()
except Exception as e:
    print(f"Facebook login button error: {e}") 

# Switch to the Facebook login window
try:
    WebDriverWait(driver, 30).until(lambda d: len(d.window_handles) > 1)
    original_window = driver.current_window_handle
    driver.switch_to.window(driver.window_handles[1])
except Exception as e:
    print(f"Window switch error: {e}")


try:
    # Wait for the email field to be present
    fb_email = WebDriverWait(driver, 30).until(
        EC.presence_of_element_located((By.ID, 'email'))
    )
    fb_email.send_keys('enter_your_email')

    # Wait for the password field to be present
    fb_password = WebDriverWait(driver, 30).until(
        EC.presence_of_element_located((By.ID, 'pass'))
    )
    fb_password.send_keys('enter_your_password')
    fb_password.send_keys(Keys.RETURN)
except Exception as e:
    print(f"Login error: {e}")

# Click on "Continue as [Name]" button
def click_continue_as_user():
    try:
        continue_button = WebDriverWait(driver, 30).until(
            EC.element_to_be_clickable((By.XPATH, "//*[text()='Continue as Mfon']"))
        )
        continue_button.click()
    except Exception as e:
        print(f"Continue as user button error: {e}")
        click_continue_as_user()

click_continue_as_user()

# Switch back to the original Tinder window
try:
    driver.switch_to.window(original_window)
except Exception as e:
    print(f"Switch back to original window error: {e}")

# Handle additional prompts (tidner allow location and notify me when theres a notification)
try:
    allow = WebDriverWait(driver, 30).until(
        EC.element_to_be_clickable((By.XPATH, "//*[text()='Allow']"))
    )
    allow.click()
    notify = WebDriverWait(driver, 30).until(
        EC.element_to_be_clickable((By.XPATH, "//*[text()='Notify me']"))
    )
    notify.click()
except Exception as e:
    print(f"Prompt error: {e}")

# Function to scrape profile details and images
def scrape_profile_details(profile_index):
    profile_data = {
        "username": "None",
        "age": "None",
        "essentials": "None",
        "basics": "None",
        "images": []
    }
    
    try:
        # Scrape username
        try:
            username_element = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.XPATH, "//span[contains(@class, 'Pend')]"))
            )
            profile_data["username"] = username_element.text
        except Exception as e:
            print(f"Username not found for profile {profile_index}: {e}")
        
        # Scrape age
        try:
            age_element = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.XPATH, "//span[contains(@class, 'Whs')]"))
            )
            profile_data["age"] = age_element.text
        except Exception as e:
            print(f"Age not found for profile {profile_index}: {e}")
        
        # Scrape essensials
        try:
            essentials_element = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.XPATH, "//div[contains(@class, 'P') and contains(@class, '24px') and contains(@class, 'W(100%)') and contains(@class, 'Bgc($c-ds-background-primary)') and contains(@class, 'Bdrs') and contains(@class, '12px')][2]"))
            )
            profile_data["zodiac_sign"] = essentials_element.text
        except Exception as e:
            print(f"Essebtials not found for profile {profile_index}: {e}")

        # Scrape  basic information
        try:
            basics_element = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.XPATH, "//div[contains(@class, 'P') and contains(@class, '24px') and contains(@class, 'W(100%)') and contains(@class, 'Bgc($c-ds-background-primary)') and contains(@class, 'Bdrs') and contains(@class, '12px')][3]"))
            )

            profile_data["location"] = basics_element.text
        except Exception as e:
            print(f"Basic not found for profile {profile_index}: {e}")

        # Scrape images
        for i in range(5):
            try:
                # Wait for the image to be present
                image = WebDriverWait(driver, 30).until(
                    EC.presence_of_element_located((By.XPATH, ".//div[contains(@class, 'slider__img Z')]"))
                )
                # Extract the style attribute
                style = image.get_attribute('style')

                # Extract the URL from the style attribute
                match = re.search(r'url\("(.+?)"\)', style)
                if match:
                    link = match.group(1)
                    profile_data["images"].append(link)
                    print(f"Profile {profile_index}, Image {i+1} URL: {link}")
                
                # Click the next button to go to the next image
                try:
                    next_button = WebDriverWait(driver, 30).until(
                        EC.element_to_be_clickable((By.XPATH, "//button[contains(@aria-label, 'Next Photo')]"))
                    )
                    next_button.click()
                    time.sleep(2)  # Wait for the next image to load
                except Exception as e:
                    print(f"Next photo button error on image {i+1} of profile {profile_index}: {e}")
                    break
                
            except Exception as e:
                print(f"Error scraping image {i+1} from profile {profile_index}: {e}")
                break
    
    except Exception as e:
        print(f"Error scraping profile details for profile {profile_index}: {e}")
    
    return profile_data

# Function to save profile data and images in a structured folder
def save_profile_data(profile_data, profile_index):
    base_folder = "profile_data"
    profile_folder = os.path.join(base_folder, f"profile_{profile_index}")
    
    # Create the profile folder if it doesn't exist
    os.makedirs(profile_folder, exist_ok=True)
    
    # Save profile details to a text file
    profile_txt_path = os.path.join(profile_folder, "profile.txt")
    with open(profile_txt_path, 'w') as file:
        file.write(f"Username: {profile_data['username']}\n")
        file.write(f"Age: {profile_data['age']}\n")
        file.write(f"Essensials: {profile_data['zodiac_sign']}\n")
        file.write(f"Basics: {profile_data['location']}\n")
    
    # Download and save images in the profile folder
    for i, image_url in enumerate(profile_data["images"], start=1):
        try:
            image_data = requests.get(image_url).content
            image_path = os.path.join(profile_folder, f"image_{i}.jpg")
            with open(image_path, 'wb') as img_file:
                img_file.write(image_data)
            print(f"Saved image {i} for profile {profile_index}")
        except Exception as e:
            print(f"Failed to save image {i} for profile {profile_index}: {e}")

# Main loop to scrape profiles
for profile_index in range(1, 100):
    try:
        # Open each profile
        open_profile_button = WebDriverWait(driver, 30).until(
            EC.presence_of_element_located((By.XPATH, '//button//span[text()="Open Profile"]'))
        )
        driver.execute_script("arguments[0].click();", open_profile_button)
        
        # Scrape and save profile data
        profile_data = scrape_profile_details(profile_index)
        save_profile_data(profile_data, profile_index)
        
        # Close the profile (click "Nope" or similar)
        cancel_button = WebDriverWait(driver, 30).until(
            EC.element_to_be_clickable((By.XPATH, "//button//span[text()='Nope']"))
        )
        driver.execute_script("arguments[0].click();", cancel_button)
        
        time.sleep(2)  # Wait before moving to the next profile
    except:
        break

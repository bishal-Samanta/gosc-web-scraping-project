
import json
import os
from datetime import time
from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException, ElementNotInteractableException, TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup


# Globals
company_data = []
temp_company_data = []
projects_data = []

year = "2023"
pre_file_name = "gsoc-temp-data-org-wise-"
file_name = pre_file_name + year


# Set up Selenium with ChromeDriver
driver = webdriver.Chrome()


def generate_json_from_array (data , filename) :
    # Create the 'data' folder if it doesn't exist
    if not os.path.exists("data-" + year):
        os.makedirs("data-" + year)

    # Define the path to the JSON file
    file_path = os.path.join("data-" + year, filename)

    # Open the JSON file in write mode and save the data
    with open(file_path, "w") as json_file:
        json.dump(data, json_file, indent=4)


def extract_data_from_project_page(project_url, org_name, official_gsoc_link, official_org_lin):

    driver.get(project_url)
    print("Running for project page ....")

    # Wait for elements to load on the organization's page
    WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CLASS_NAME, 'text--weight-medium')))

    # Now, you can use BeautifulSoup to extract data from the organization's page
    project_page_source = driver.page_source
    project_soup = BeautifulSoup(project_page_source, 'html.parser')

    project_technology_divs = project_soup.find_all('div', class_='h-list__item ng-star-inserted')

    global technology
    global topic

    for i in range(0, len(project_technology_divs), 2):
        technology_div = project_technology_divs[i]
        topic_div = project_technology_divs[i + 1]

        technology = technology_div.find('dd', class_='text--weight-medium').text.strip()
        topic = topic_div.find('dd', class_='text--weight-medium').text.strip()



    project_details = project_soup.find('div', class_='project-details-content').text.strip()

    projects_data.append({"org_name": org_name, "org_link": official_org_lin, "org_gsoc_link": official_gsoc_link,
                          "project_details_link": project_url, "technology": technology, "topics": topic,
                          "project_details": project_details})


def extract_data_from_org_page(orgUrl, organization_name, short_description):
    try:
        driver.get(orgUrl)

        # Wait for elements to load on the organization's page
        WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CLASS_NAME, 'tech__content')))
        WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CLASS_NAME, 'section__inner')))

        # Wait for the links to load dynamically
        WebDriverWait(driver, 10).until(
            EC.presence_of_all_elements_located((By.CSS_SELECTOR, 'a[href*="/programs/2023/projects/"]')))

        # Now, you can use BeautifulSoup to extract data from the organization's page
        org_page_source = driver.page_source
        org_soup = BeautifulSoup(org_page_source, 'html.parser')

        # print(org_soup)
        org_name = organization_name
        short_description = short_description
        org_technology = org_soup.find('div', class_='tech__content').text.strip()
        org_topics = org_soup.find('div', class_='topics__content').text.strip()
        official_org_link = org_soup.find('div', class_='link__wrapper').find('a', class_='link').get('href')
        official_gsoc_link = orgUrl

        company_data.append({"org_name": org_name, "org_description": short_description, "technology": org_technology,
                             "topics": org_topics, "official_link": official_org_link, "gsoc_link": official_gsoc_link})

      

        # Define the prefix you want to search for
        prefix = '/programs/2023/projects/'



        # Find all <a> tags with href containing the prefix and any ID
        matching_links = org_soup.find_all('a', href=lambda href: href and prefix in href)

        # Print the matching links
        for link in matching_links:
            project_url = 'https://summerofcode.withgoogle.com' + link.get('href')
            extract_data_from_project_page(project_url, org_name, official_gsoc_link, official_org_link)



    except NoSuchElementException:
        print(f"No data found on the organization's page: {orgUrl}")
        return None

    except TimeoutException:
        print(f"Timeout while waiting for elements on the organization's page: {orgUrl}")
        return None


def process_json_file():
    # Define the path to the JSON file
    file_path = os.path.join("data", file_name )

    try:
        # Open and read the JSON file
        with open(file_path, "r") as json_file:
            data = json.load(json_file)

        # Check if the data is a list of objects
        if isinstance(data, list):
            print("JSON Data extracted....")
            # Process each object in the list
            for obj in data:
                # You can perform your desired operations here
                extract_data_from_org_page(obj['org_gsoc_link'], obj['org_name'], obj['ord_description'])

            generate_json_from_array(projects_data , "project-data-" + year )
            generate_json_from_array( company_data , "company-data-" + year)

        else:
            print("The JSON file does not contain a list of objects.")

    except FileNotFoundError:
        print("The JSON file 'test.json' was not found in the 'data' folder.")
    except json.JSONDecodeError:
        print("Error decoding JSON data from the file.")


# Call the function to process the JSON file
process_json_file()

# Function to extract data from the current page
def extract_data_from_page(page_source):
    print("Running for first page")
    # Parse the page source with BeautifulSoup
    soup = BeautifulSoup(page_source, 'html.parser')

    # Extract all div elements with the specified class "card"
    card_divs = soup.find_all('div', class_='card')

    # Iterate through each card and extract information
    for card in card_divs:
        organization_name = card.find('div', class_='name').text.strip()
        short_description = card.find('div', class_='short-description').text.strip()
        organization_link = 'https://summerofcode.withgoogle.com/' + card.find('a', class_='content').get('href')

        temp_company_data.append(
            {"org_name": organization_name, "ord_description": short_description, "org_gsoc_link": organization_link})

    # All_tech_stacks_for_company
    for data in temp_company_data:
        extract_data_from_org_page(data['org_gsoc_link'], data['org_name'], data['ord_description'])


# Loop to navigate through pages and extract data
while True:
    try:
        # Scroll down to load more content
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")

        # Wait for the "Next page" button to be present
        next_page_button = WebDriverWait(driver, 30).until(
            EC.presence_of_element_located((By.XPATH, '//button[@aria-label="Next page"]')))

        # Check if the button has the "mat-button-disabled" class
        if "mat-button-disabled" in next_page_button.get_attribute("class"):
            print("The Next button is disabled...")
            break  # Exit the loop if the button is disabled

        # Extract data from the current page
        page_source = driver.page_source
        extract_data_from_page(page_source)

        print(next_page_button, "Button")

        # Find the SVG element using JavaScript
        svg_element = driver.execute_script('return document.querySelector("button[aria-label=\'Next page\'] svg")')

        print(svg_element)

        # Click the SVG element using JavaScript
        driver.execute_script(
            "arguments[0].dispatchEvent(new MouseEvent('click', {view: window, bubbles:true, cancelable: true}))",
            svg_element)

    except NoSuchElementException:
        print("No more pages or button not found")
        break  # Exit the loop if there are no more pages or the button is not found
    except ElementNotInteractableException:
        print("Button not interactable, waiting for a moment...")
        time.sleep(5)  # Add a delay and retry

print(company_data)
print(projects_data)
print(temp_company_data)
print(len(temp_company_data))

# Close the Selenium WebDriver
driver.quit()

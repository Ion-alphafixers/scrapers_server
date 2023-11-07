import datetime
from selenium import webdriver
import io
import zipfile
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import pandas as pd
import os
import time
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options


options = Options()
# options.add_argument("--headless")
options.add_argument("--disable-gpu")
options.add_argument("--no-sandbox")
options.add_argument("enable-automation")
options.add_argument("--disable-infobars")
options.add_argument("--disable-dev-shm-usage")



def click_login(driver):
    try:
        login_button = driver.find_element(By.ID,"ext-button-4")
        login_button.click()
        print("BUTTON CLICKED")
    except:
        print("Retrying")
        time.sleep(1)
        click_login(driver)


configs = {
    "AAFM": {
        "url": "https://allamericanfacilities.fexa.io/main/index#login",
        "email": "info@alphafixers.com",
        "password": "Fexa2020"},
    "DAVACO": {
        "url": "https://davaco.fexa.io/main/index#login",
        "email": "info@alphafixers.com ",
        "password": "Alphafix1!"
    }
}

def scrape_work_order(driver,wait_allowed,downloads_folder,facility_name):
    all_child_divs = []
    counter = 0
    dummy_wait = WebDriverWait(driver, wait_allowed).until(EC.presence_of_element_located((By.XPATH,
                                                                                           "/html/body/div[5]/div[2]/div/div[1]/div/div[2]/div/div[2]/div[2]/div/div[2]/div/div/div/div/div[1]/div[3]/div[2]/div[2]/div[10]")))
    headers = driver.find_element(By.XPATH,
                                  "/html/body/div[5]/div[2]/div/div[1]/div/div[2]/div/div[2]/div[2]/div/div[2]/div/div/div/div/div[1]/div[2]").text.split(
        "\n")[:-1]
    number_of_work_orders = int(driver.find_element(By.XPATH,
                                                    "/html/body/div[5]/div[2]/div/div[1]/div/div[2]/div/div[2]/div[2]/div/div[2]/div/div/div/div/div[1]/div[1]/div[1]/div[1]/div[1]/div[1]/div/div[1]/div/div/div/div/div[1]/div").text)
    print(number_of_work_orders)
    time.sleep(5)
    while True:
        if counter == number_of_work_orders: break
        for i in range(1, 30):
            try:
                if counter == number_of_work_orders: break
                curr_element = driver.find_element(By.XPATH,
                                                   f"/html/body/div[5]/div[2]/div/div[1]/div/div[2]/div/div[2]/div[2]/div/div[2]/div/div/div/div/div[1]/div[3]/div[2]/div[2]/div[{i}]")
                print(counter)
                all_child_divs.append(curr_element.text)
                driver.execute_script("arguments[0].scrollIntoView();", curr_element)
                counter += 1
            except:
                scroll_distance = 100
                driver.execute_script(f"window.scrollBy(0, {scroll_distance});")
                # dummy_wait = WebDriverWait(driver, wait_allowed).until(EC.presence_of_element_located((By.XPATH,
                #                                                                                        f"/html/body/div[5]/div[2]/div/div[1]/div/div[2]/div/div[2]/div[2]/div/div[2]/div/div/div/div/div[1]/div[3]/div[2]/div[2]/div[{i}]")))
                if counter == number_of_work_orders: break
                counter += 1
                print(counter)

                curr_element = driver.find_element(By.XPATH,
                                                   f"/html/body/div[5]/div[2]/div/div[1]/div/div[2]/div/div[2]/div[2]/div/div[2]/div/div/div/div/div[1]/div[3]/div[2]/div[2]/div[{i}]")
                print("ELEMENT")
                all_child_divs.append(curr_element.text)
                driver.execute_script("arguments[0].scrollIntoView();", curr_element)
    rows = []
    for row in all_child_divs:
        curr_row = row.split('\n')
        curr_div = []
        for col in curr_row:
            if col.startswith(" ") == True:
                curr_div.append("")
                curr_div.append(col.strip())
            else:
                curr_div.append(col.strip())
        rows.append(curr_div)
    df = pd.DataFrame([[col for col in (row[:13] if len(row) > 13 else row) if col != ""] for row in rows],
                      columns=headers if len(headers) == 13 else [' ID', 'Locations', 'Priority', 'Status', 'Class',
                                                                  'Trade', 'Total Vendor NTE', 'Assignment ID',
                                                                  'Upcoming Visits',
                                                                  'Completed Visits', 'Created By', 'Created Date',
                                                                  'Days'])
    timestamp = datetime.datetime.utcnow().strftime('%Y-%m-%d %H-%M-%S')  # Format the timestamp

    filename = os.path.join(downloads_folder, f'WorkOrders-{facility_name}-{timestamp}.csv')

    return df
def scrape_invoices(driver,wait_allowed,downloads_folder,facility_name):
    all_child_divs = []
    counter = 0
    dummy_wait = WebDriverWait(driver, wait_allowed).until(EC.presence_of_element_located((By.XPATH,
                                                                                           "/html/body/div[5]/div[2]/div/div[1]/div/div[2]/div/div[2]/div[4]/div/div[2]/div[1]/div/div/div/div[1]/div[3]/div[2]/div[2]/div[10]")))
    headers = driver.find_element(By.XPATH,
                                  "/html/body/div[5]/div[2]/div/div[1]/div/div[2]/div/div[2]/div[4]/div/div[2]/div/div/div/div/div[1]/div[2]/div").text.split(
        "\n")[:-1]
    if len(headers)!=18:
        headers = [' ID', 'Work Order ID', 'Billing Company Name', 'Location', 'Reference Number', 'City', 'State', 'GL Code', 'Status', 'Assignment Status', 'Workorder Status', 'Transaction Date', 'Due Date',"Approved Date", "Total","Balance Due","Pending Approval","Discount Total"]
    number_of_invoices = int(driver.find_element(By.XPATH,
                                                 "/html/body/div[5]/div[2]/div/div[1]/div/div[2]/div/div[2]/div[4]/div/div[2]/div/div/div/div/div[1]/div[1]/div[1]/div[1]/div[1]/div[1]/div/div[1]/div/div/div/div/div[1]/div").text)
    print(number_of_invoices)
    while True:
        if counter == number_of_invoices: break
        for i in range(1, 30):
            if counter == number_of_invoices: break
            counter += 1
            print(counter)

            curr_element = driver.find_element(By.XPATH,
                                               f"/html/body/div[5]/div[2]/div/div[1]/div/div[2]/div/div[2]/div[4]/div/div[2]/div/div/div/div/div[1]/div[3]/div[2]/div[2]/div[{i}]")
            all_child_divs.append(curr_element.text)
            driver.execute_script("arguments[0].scrollIntoView();", curr_element)

    rows = []
    for row in all_child_divs:
        curr_row = row.split('\n')
        curr_div = []
        for col in curr_row:
            if col.startswith(" ") == True:
                curr_div.append("")
                curr_div.append(col.strip())
            else:
                curr_div.append(col.strip())
        rows.append(curr_div)
    df = pd.DataFrame(rows, columns=headers)
    timestamp = datetime.datetime.utcnow().strftime('%Y-%m-%d %H-%M-%S')  # Format the timestamp

    filename = os.path.join(downloads_folder, f'Invoices-{facility_name}-{timestamp}.csv')

    return df
def scrape_proposals(driver,wait_allowed,downloads_folder,facility_name):
    all_child_divs = []
    counter = 0
    dummy_wait = WebDriverWait(driver, wait_allowed).until(EC.presence_of_element_located((By.XPATH,
                                                                                           "/html/body/div[5]/div[2]/div/div[1]/div/div[2]/div/div[2]/div[8]/div/div[2]/div/div/div/div/div[1]/div[3]/div[2]/div[2]/div[10]")))
    headers = driver.find_element(By.XPATH,
                                  "/html/body/div[5]/div[2]/div/div[1]/div/div[2]/div/div[2]/div[8]/div/div[2]/div/div/div/div/div[1]/div[2]").text.split(
        "\n")[:-1]
    number_of_invoices = int(driver.find_element(By.XPATH,
                                                 "/html/body/div[5]/div[2]/div/div[1]/div/div[2]/div/div[2]/div[8]/div/div[2]/div/div/div/div/div[1]/div[1]/div[1]/div[1]/div[1]/div[1]/div/div[1]/div/div/div/div/div[1]/div").text)
    print(number_of_invoices)
    while True:
        if counter == number_of_invoices: break
        for i in range(1, 30):
            if counter == number_of_invoices: break
            counter += 1
            print(counter)
            curr_element = driver.find_element(By.XPATH,
                                               f"/html/body/div[5]/div[2]/div/div[1]/div/div[2]/div/div[2]/div[8]/div/div[2]/div/div/div/div/div[1]/div[3]/div[2]/div[2]/div[{i}]")
            all_child_divs.append(curr_element.text)
            driver.execute_script("arguments[0].scrollIntoView();", curr_element)
    rows = []
    for row in all_child_divs:
        curr_row = row.split('\n')
        curr_div = []
        for col in curr_row:

            if len(col.split("  ")) > 1:
                for element in col.split("  "):
                    curr_div.append(element.strip())
            elif col.startswith(" ") == True:
                curr_div.append("")
                curr_div.append(col.strip())
            else:
                curr_div.append(col.strip())
        rows.append(curr_div)
    if len(headers) != 17:
        headers = [' ID', 'Work Order ID', 'Billing Company Name', 'Location', 'Proposal Number', 'City', 'State', 'Status', 'Assignment Status', 'Workorder Status', 'Transaction Date', 'Due Date', 'Approved Date',"Total","Balance Due","Pending Approval",""]
    df = pd.DataFrame(rows, columns=headers)
    return df
def get_side_bar_options(driver):
    side_bar_options = driver.find_elements(By.ID, "ext-element-112")
    div_elements = []

    # Loop through each 'side_bar_options' element
    for side_bar_option in side_bar_options:
        # Find all the div elements within the current 'side_bar_option' element using XPath
        divs_within_option = side_bar_option.find_elements(By.XPATH, ".//div")

        # Add the found div elements to the list
        div_elements.extend(divs_within_option)
    return div_elements
def convert_scraping_results_to_zip(results) -> zipfile.ZipFile:
    zip_buffer = io.BytesIO()

    with zipfile.ZipFile(zip_buffer, mode='w', compression=zipfile.ZIP_DEFLATED) as zip_f:
            for fm, data in results.items():
                for report_type_name, report_type_data in data.items():
                    zip_path = os.path.join(r"", f"{fm}_{report_type_name}.csv")
                    zip_f.writestr(zip_path, pd.DataFrame(report_type_data).to_csv(index=False))

    return zip_buffer


def scraper():
    driver = webdriver.Chrome(options=options)
    try:
        home_directory = os.path.expanduser("~")
        downloads_folder = os.path.join(home_directory, "Downloads")
        wait_allowed = 500
        data_to_return = {}
        for facility_name, facility_info in configs.items():
            driver.get(facility_info['url'])

            email_element = WebDriverWait(driver, 500).until(EC.presence_of_element_located((By.ID, 'ext-element-16')))
            email_element.click()
            email_element.send_keys(facility_info['email'])

            password_element = driver.find_element(By.ID, "ext-element-29")
            password_element.click()
            password_element.send_keys(facility_info['password'])

            click_login(driver)

            time.sleep(10)
            data_to_return[facility_name] = {}
            print(f"{facility_name}//work_orders")
            driver.get(facility_info['url'].split("#")[0] + "#workorders")
            data_to_return[facility_name]['work_orders'] = scrape_work_order(driver, wait_allowed, downloads_folder,
                                                                             facility_name)
            print(f"{facility_name}//invoices")
            driver.get(facility_info['url'].split("#")[0] + "#invoices")
            data_to_return[facility_name]['invoices'] = scrape_invoices(driver, wait_allowed, downloads_folder,
                                                                        facility_name)
            print(f"{facility_name}//proposals")
            driver.get(facility_info['url'].split("#")[0] + "#subcontractorquotes")
            data_to_return[facility_name]['proposals'] = scrape_proposals(driver, wait_allowed, downloads_folder,
                                                                          facility_name)
        zipped_data = convert_scraping_results_to_zip(data_to_return)
        return zipped_data
    finally:
        driver.quit()  # Make sure to quit the WebDriver to release resources


import time


driver = webdriver.Chrome(options=options)
driver.get(url='https://www.google.com')
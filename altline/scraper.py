import io
import os
import zipfile

import pandas as pd
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium import webdriver
import time

chrome_options = webdriver.ChromeOptions()
chrome_options.add_argument("--window-size=1850x1000")
chrome_options.add_argument("--headless")
chrome_options.add_argument("--disable-gpu")
chrome_options.add_argument("--no-sandbox")
chrome_options.add_argument("enable-automation")
chrome_options.add_argument("--disable-infobars")
chrome_options.add_argument("--disable-dev-shm-usage")
chrome_options.add_argument("--user-agent")

very_long_wait = 25
long_wait = 8
medium_wait = 5
short_wait = 2
def convert_scraping_results_to_zip(results) -> zipfile.ZipFile:
    zip_buffer = io.BytesIO()

    with zipfile.ZipFile(zip_buffer, mode='w', compression=zipfile.ZIP_DEFLATED) as zip_f:
            for fm, data in results.items():
                for report_type_name, report_type_data in data.items():
                    zip_path = os.path.join(r"", f"{fm}_{report_type_name}.csv")
                    zip_f.writestr(zip_path, pd.DataFrame(report_type_data).to_csv(index=False))

    return zip_buffer
def scraper():

    # This maximizes the browser window
    driver = webdriver.Chrome(options=chrome_options)
    driver.set_window_size(1850, 1000)
    wait = WebDriverWait(driver, 5000)

    print(1)
    driver.get('https://sobanco.profitstars.com/MicrosoftIdentity/Account/SignIn')
    print("Navigated to sign in screen")
    driver.implicitly_wait(30)

    emailInput = driver.find_element(By.ID, "email")
    emailInput.send_keys('Bernard@alphafixers.com')
    passwordInput = driver.find_element(By.ID, "password")
    passwordInput.send_keys('Alpha12#')
    driver.execute_script("document.getElementById('next').click()")
    print(f"Authenticated! Waiting for {very_long_wait} seconds")
    time.sleep(very_long_wait)
    payments_section = driver.find_element(By.XPATH,"/html/body/app/div[1]/div[2]/nav/div/a[10]").click()
    print("Payments")
    # Input.click()
    time.sleep(medium_wait)

    searchInput = driver.find_element(By.XPATH,
                                      "/html/body/app/div[2]/div[3]/div[3]/div/div/div/form/div[6]/div/div[1]/button")
    searchInput.click()

    time.sleep(short_wait)

    df = pd.DataFrame()
    set_disabled = False
    while True:
        table = driver.find_element(By.ID, "pmtList")
        rows = table.find_elements(By.TAG_NAME, ("tr"))
        all_rows = []
        for index, row in enumerate(rows):
            print(index)
            if index == 5:
                set_disabled = True
                break
            columns = row.find_elements(By.TAG_NAME, "td")
            driver.execute_script("arguments[0].scrollIntoView();", row)
            if len(columns) >= 3:
                for i in range(4):

                    print(f"Column {i + 1}: {columns[i + 1].text}")

                debtor = columns[1].text
                posted_date = columns[2].text
                check_date = columns[3].text
                check_number = columns[4].text
                time.sleep(medium_wait)
                driver.find_element(By.XPATH,
                                    f'/html/body/app/div[2]/div[3]/div[6]/div[1]/div[2]/section/div/div/table/tbody/tr[{index - 1}]/td[5]/button').click()
                while True:

                    time.sleep(medium_wait)
                    sub_table = driver.find_element(By.ID, "pmtDetails")
                    sub_rows = sub_table.find_elements(By.TAG_NAME, ("tr"))
                    for row in sub_rows[2:]:
                        sub_row = [debtor, posted_date, check_date, check_number]
                        columns = row.find_elements(By.TAG_NAME, "td")
                        if len(columns) >= 3:
                            for i in range(len(columns) - 1):
                                sub_row.append(columns[i + 1].text)
                            all_rows.append(sub_row)
                    nextBtn = driver.find_element(By.LINK_TEXT, "Next")
                    if "disabled" in nextBtn.get_attribute("class"):
                        break
                    nextBtn.click()
                time.sleep(medium_wait)
                backArrow = driver.find_element(By.XPATH,
                                                "/html/body/app/div[2]/div[3]/div[5]/div/header/div/div/button")
                backArrow.click()
        sub_headers = []
        sub_df = pd.DataFrame(data=all_rows,
                              columns=['Debtor', 'Posted Date', 'Check Date', 'Check Number' , 'INV#', 'PO#', 'INV DATE', 'AMOUNT', 'BALANCE', 'PAYMENT', 'ESCROW', 'FEE DAYS',
                       'FEE EARNED',"Explanation Code","Description"])
        df = pd.concat([df, sub_df])
        time.sleep(long_wait)
        nextBtn = driver.find_element(By.LINK_TEXT, "Next")
        if "disabled" in nextBtn.get_attribute("class"):
            break
        if set_disabled == True:
            break
        nextBtn.click()
    time.sleep(medium_wait)
    Input = wait.until(EC.presence_of_element_located((By.LINK_TEXT, "Invoices")))
    Input.click()

    time.sleep(long_wait)

    searchInput = driver.find_element(By.XPATH,
                                      "/html/body/app/div[2]/div[3]/div[3]/div/div/div/form/div[10]/div/div[1]/button")
    searchInput.click()
    time.sleep(medium_wait)
    print("Invoices")
    df1 = pd.DataFrame()
    while True:

        table = driver.find_element(By.ID, "invList")

        rows = table.find_elements(By.TAG_NAME, ("tr"))
        all_rows = []
        for index, row in enumerate(rows):
            print(index)
            columns = row.find_elements(By.TAG_NAME, "td")
            driver.execute_script("arguments[0].scrollIntoView();", row)
            if len(columns) >= 3:
                for i in range(len(columns) - 1):
                    print(f"Column {i + 1}: {columns[i + 1].text}")
                inv = columns[1].text
                amount = columns[2].text
                inv_balance = columns[3].text
                debtor = columns[4].text
                inv_date = columns[7].text
                purchase_date = columns[8].text
                print(inv, amount, inv_balance, debtor, inv_date, purchase_date)
                time.sleep(medium_wait)
                driver.find_element(By.XPATH,
                                    f"/html/body/app/div[2]/div[3]/div[14]/div[2]/div/section/div/div[2]/table/tbody/tr[{index - 1}]/td[2]/button").click()
                time.sleep(long_wait)
                sub_row = [inv, amount, inv_balance, debtor, inv_date, purchase_date]
                fee = driver.find_element(By.XPATH,
                                          "/html/body/app/div[2]/div[3]/div[4]/div/div/div[1]/form/div[2]/div[1]/div[4]/div/span").text
                reserve_escrow = driver.find_element(By.XPATH,
                                                     "/html/body/app/div[2]/div[3]/div[4]/div/div/div[1]/form/div[2]/div[1]/div[6]/div/span").text
                days_due = driver.find_element(By.XPATH,
                                               "/html/body/app/div[2]/div[3]/div[4]/div/div/div[1]/form/div[2]/div[3]/div[2]/div/span").text
                sub_row.append(fee)
                sub_row.append(reserve_escrow)
                sub_row.append(days_due)
                all_rows.append(sub_row)
                time.sleep(short_wait)
                backArrow = driver.find_element(By.XPATH,
                                                "/html/body/app/div[2]/div[3]/div[4]/div/header/div/div/div/div[1]/button")
                backArrow.click()
        sub_df = pd.DataFrame(data=all_rows,
                              columns=['INV', 'AMOUNT', 'INV BALANCE', 'DEBTOR', "INV DATE", "PURCHASE DATE",
                                       "Payment Fee Earned", "Reserve Escrow", "Days Due"])
        df1 = pd.concat([df1, sub_df])

        time.sleep(long_wait)
        nextBtn = driver.find_element(By.LINK_TEXT, "Next")
        if "disabled" in nextBtn.get_attribute("class"):
            break
        nextBtn.click()
    data = {
        "Altline":
            {
                "payments":df,
                'invoices':df1
            }
    }
    zipped_data = convert_scraping_results_to_zip(data)
    return zipped_data

if __name__ == "__main__":
    scraper()
import os
import json
import csv
import pandas as pd

from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By

from io import StringIO


class Country(dict):
    def __init__(self, alpha2_code, short_name_lower_case, alpha3_code, numeric_code, subdivisions):
        dict.__init__(self, alpha2_code=alpha2_code, short_name_lower_case=short_name_lower_case, alpha3_code=alpha3_code, numeric_code=numeric_code, subdivisions=subdivisions)
        self.alpha2_code = alpha2_code
        self.short_name_lower_case = short_name_lower_case
        self.alpha3_code = alpha3_code
        self.numeric_code = numeric_code
        self.subdivisions = subdivisions

class Subdivision(dict):
    def __init__(self, category, code, name):
        dict.__init__(self, category=category, code=code, name=name)
        self.category = category
        self.code = code
        self.name = name

def getCountryHtml(country_code):
    # instance of Options class allows
    # us to configure Headless Chrome
    options = Options()
    
    # this parameter tells Chrome that
    # it should be run without UI (Headless)
    options.add_argument("--headless")

    driver = webdriver.Chrome(options=options)

    url = f"https://www.iso.org/obp/ui/#iso:code:3166:{country_code}"

    driver.get(url)
    
    WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, "subdivision")))

    return driver.page_source

def getSubdivisions(html):
    column1_text = "Subdivision category"
    column2_text = "3166-2 code"
    column3_text = "Subdivision name"
    column4_text = "Local variant"
    column5_text = "Language code"
    column6_text = "Romanization system"
    column7_text = "Parent subdivision"

    df = pd.read_html(StringIO(html), match=column2_text)[0]
    df.reset_index()

    subdivisions = []
    codes = []

    for index, row in df.iterrows():
        code = row[column2_text].replace("*", "")
        
        # Prevent duplicate entries of alpha2 code
        if code not in codes:
            subdivisions.append(Subdivision(category=row[column1_text], code=code, name=row[column3_text]))
        
        codes.append(code)

    return subdivisions

def getCountryCodes():
    file_path = "./just-codes.csv"
    country_codes = []

    with open(file_path, "r") as csv_file:
        reader = csv.reader(csv_file)

        for row in reader:
            country_codes.append(row[0])

    return country_codes

def getCountries():
    country_codes = getCountryCodes()
    countries = []

    alpha2_code_field_name = "Alpha-2 code"
    short_name_lower_case_field_name = "Short name lower case"
    alpha3_code_field_name = "Alpha-3 code"
    numeric_code_field_name = "Numeric code"

    for country_code in country_codes:
        html = getCountryHtml(country_code)

        soup = BeautifulSoup(html, features="lxml")
        core_views = soup.find_all("div", {"class": "core-view-line"})

        alpha2_code = ""
        short_name_lower_case = ""
        alpha3_code = ""
        numeric_code = 0

        for core_view in core_views:
            fieldName = core_view.find("div", {"class": "core-view-field-name"}).contents[0]
            
            if fieldName == alpha2_code_field_name:
                alpha2_code = core_view.find("div", {"class": "core-view-field-value"}).contents[0]
            
            if fieldName == short_name_lower_case_field_name:
                short_name_lower_case = core_view.find("div", {"class": "core-view-field-value"}).contents[0]

            if fieldName == alpha3_code_field_name:
                alpha3_code = core_view.find("div", {"class": "core-view-field-value"}).contents[0]

            if fieldName == numeric_code_field_name:
                numeric_code = int(core_view.find("div", {"class": "core-view-field-value"}).contents[0])

        # Get country properties
        # Make list of subdivisions
        subdivisions = getSubdivisions(html)
        
        country = Country(alpha2_code=alpha2_code, alpha3_code=alpha3_code, numeric_code=numeric_code, short_name_lower_case=short_name_lower_case, subdivisions=subdivisions)
        countries.append(country)

        file = open("./json/"+short_name_lower_case+".json", "+w", encoding="utf-8")
        file.write(json.dumps(country, ensure_ascii=False, indent=4))
        file.close()

    return countries

jsonFolder = "./json"
if not os.path.exists(jsonFolder):
   # Create a new directory because it does not exist
   os.makedirs(jsonFolder)
   print("The new directory is created!")

countries = getCountries()
file = open("./json/all_countries.json", "+w", encoding="utf-8")
file.write(json.dumps(countries, ensure_ascii=False, indent=4))
file.close()

print(json.dumps(countries, ensure_ascii=False))
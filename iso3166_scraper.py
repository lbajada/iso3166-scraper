import os
import json

from selenium.webdriver.chrome.webdriver import WebDriver

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support.expected_conditions import presence_of_element_located
from selenium.webdriver.common.by import By


class Country(dict):
    def __init__(self, alpha2_code, short_name, short_name_lower_case, full_name, alpha3_code, numeric_code, remarks,
                 independent, territory_name, status, subdivision_categories, subdivisions, additional_information,
                 change_history):
        dict.__init__(self, alpha2_code=alpha2_code, short_name=short_name, short_name_lower_case=short_name_lower_case,
                      full_name=full_name, alpha3_code=alpha3_code, numeric_code=numeric_code, remarks=remarks,
                      independent=independent, territory_name=territory_name, status=status,
                      subdivision_categories=subdivision_categories, subdivisions=subdivisions,
                      additional_information=additional_information, change_history=change_history)
        self.alpha2_code = alpha2_code
        self.short_name = short_name
        self.short_name_lower_case = short_name_lower_case
        self.full_name = full_name
        self.alpha3_code = alpha3_code
        self.numeric_code = numeric_code
        self.remarks = remarks
        self.independent = independent
        self.territory_name = territory_name
        self.status = status
        self.subdivision_categories = subdivision_categories
        self.subdivisions = subdivisions
        self.additional_information = additional_information
        self.change_history = change_history


class AdditionalInformation(dict):
    def __init__(self, administrative_language_alpha2, administrative_language_alpha3, local_short_name):
        dict.__init__(self, administrative_language_alpha2=administrative_language_alpha2,
                      administrative_language_alpha3=administrative_language_alpha3,
                      local_short_name=local_short_name)
        self.administrative_language_alpha2 = administrative_language_alpha2
        self.administrative_language_alpha3 = administrative_language_alpha3
        self.local_short_name = local_short_name


class Subdivision(dict):
    def __init__(self, category, code3166_2, name, local_variant, language_code, romanization_system,
                 parent_subdivision):
        dict.__init__(self, category=category, code3166_2=code3166_2, name=name, local_variant=local_variant,
                      language_code=language_code, romanization_system=romanization_system,
                      parent_subdivision=parent_subdivision)
        self.category = category
        self.code3166_2 = code3166_2
        self.name = name
        self.local_variant = local_variant
        self.language_code = language_code
        self.romanization_system = romanization_system
        self.parent_subdivision = parent_subdivision


class SubdivisionCategory(dict):
    def __init__(self, category_count: int, category_locales: list[str]):
        dict.__init__(self, category_count=category_count, category_locales=category_locales)
        self.category_count = category_count
        self.category_locales = category_locales


class ChangeHistory(dict):
    def __init__(self, date: str, short_description_en, short_description_fr):
        dict.__init__(self, date=date, short_description_en=short_description_en,
                      short_description_fr=short_description_fr)
        self.date = date
        self.short_description_en = short_description_en
        self.short_description_fr = short_description_fr


def get_chrome_driver() -> WebDriver:
    # instance of Options class allows
    # us to configure Headless Chrome
    options = Options()

    # this parameter tells Chrome that
    # it should be run without UI (Headless)
    options.add_argument("--headless")
    options.add_argument('--disable-gpu')
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')

    return webdriver.Chrome(options=options)


def get_country_urls() -> list[str]:
    driver.get("https://www.iso.org/obp/ui/#iso:pub:PUB500001:en")
    driver.refresh()

    (WebDriverWait(driver, 10).until(presence_of_element_located((By.CLASS_NAME, "grs-grid"))))

    urls = []

    for code in driver.find_element(By.CLASS_NAME, "grs-grid").find_elements(By.CSS_SELECTOR, "a"):
        urls.append(code.get_attribute("href"))

    return urls


def get_additional_information() -> list[AdditionalInformation]:
    al_alpha2_position = al_alpha3_position = local_short_name_position = None

    additional_information_table_headers = (driver.find_element(By.ID, "country-additional-info")
                                            .find_element(By.CSS_SELECTOR, "thead")
                                            .find_elements(By.CSS_SELECTOR, "th"))

    i = 0
    for header in additional_information_table_headers:
        match header.text:
            case "Administrative language(s) alpha-2":
                al_alpha2_position = i
            case "Administrative language(s) alpha-3":
                al_alpha3_position = i
            case "Local short name":
                local_short_name_position = i
        i += 1

    additional_information_table = (driver.find_element(By.ID, "country-additional-info")
                                    .find_element(By.CSS_SELECTOR, "tbody")
                                    .find_elements(By.CSS_SELECTOR, "tr"))

    additional_information = []

    for row in additional_information_table:
        data = row.find_elements(By.CSS_SELECTOR, "td")
        additional_information.append(
            AdditionalInformation(administrative_language_alpha2=data[al_alpha2_position].text,
                                  administrative_language_alpha3=data[al_alpha3_position].text,
                                  local_short_name=data[local_short_name_position].text))

    return additional_information


def get_subdivision_categories() -> list[SubdivisionCategory]:
    subdivision_categories: list[SubdivisionCategory] = []

    subdivision_categories_html = driver.find_elements(By.CSS_SELECTOR, "p")
    for category_html in subdivision_categories_html:
        if category_html.find_elements(By.CLASS_NAME, "category-count"):
            category_count = int(category_html.find_element(By.CLASS_NAME, "category-count").text)

            category_locales: list[str] = []
            for category_locale_html in category_html.find_elements(By.CLASS_NAME, "category-locales"):
                category_locales.append(category_locale_html.text)

            subdivision_categories.append(SubdivisionCategory(category_count=category_count,
                                                              category_locales=category_locales))

    return subdivision_categories


def get_change_history() -> list[ChangeHistory]:
    change_history: list[ChangeHistory] = []

    date_position = short_description_en_position = short_description_fr_position = None

    change_history_div = None

    for element in (driver.find_element(By.CLASS_NAME, "code-view-container").find_elements(By.CSS_SELECTOR, "div")):
        if element.find_elements(By.CSS_SELECTOR, "h3"):
            if element.find_element(By.CSS_SELECTOR, "h3").text == "Change history of country code":
                change_history_div = element
                break

    if change_history_div is not None:
        change_history_table_headers = (change_history_div.find_element(By.CSS_SELECTOR, "thead")
                                        .find_elements(By.CSS_SELECTOR, "th"))

        i = 0
        for header in change_history_table_headers:
            match header.text:
                case "Effective date of change":
                    date_position = i
                case "Short description of change (en)":
                    short_description_en_position = i
                case "Short description of change (fr)":
                    short_description_fr_position = i
            i += 1

        change_history_table = (change_history_div.find_element(By.CSS_SELECTOR, "tbody")
                                .find_elements(By.CSS_SELECTOR, "tr"))

        for row in change_history_table:
            data = row.find_elements(By.CSS_SELECTOR, "td")
            change_history.append(
                ChangeHistory(date=data[date_position].text,
                              short_description_en=data[short_description_en_position].text,
                              short_description_fr=data[short_description_fr_position].text))

    return change_history


def get_subdivisions() -> list[Subdivision]:
    category_position = code_position = name_position = local_variant_position = language_code_position = \
        romanization_system_position = parent_subdivision_position = None

    subdivisions_table_headers = (driver.find_element(By.ID, "subdivision")
                                  .find_element(By.CSS_SELECTOR, "thead")
                                  .find_elements(By.CSS_SELECTOR, "th"))

    i = 0
    for header in subdivisions_table_headers:
        match header.text:
            case "Subdivision category":
                category_position = i
            case "3166-2 code":
                code_position = i
            case "Subdivision name":
                name_position = i
            case "Local variant":
                local_variant_position = i
            case "Language code":
                language_code_position = i
            case "Romanization system":
                romanization_system_position = i
            case "Parent subdivision":
                parent_subdivision_position = i
        i += 1

    subdivisions_table = (driver.find_element(By.ID, "subdivision")
                          .find_element(By.CSS_SELECTOR, "tbody")
                          .find_elements(By.CSS_SELECTOR, "tr"))

    subdivisions = []

    for row in subdivisions_table:
        data = row.find_elements(By.CSS_SELECTOR, "td")
        subdivisions.append(Subdivision(category=data[category_position].text,
                                        code3166_2=data[code_position].text.replace("*", ""),
                                        name=data[name_position].text, local_variant=data[local_variant_position].text,
                                        language_code=data[language_code_position].text,
                                        romanization_system=data[romanization_system_position].text,
                                        parent_subdivision=data[parent_subdivision_position].text))

    return subdivisions


def get_countries() -> list[Country]:
    country_urls = get_country_urls()
    countries = []

    for country_url in country_urls:
        driver.get(country_url)
        driver.refresh()

        (WebDriverWait(driver, 20).until(presence_of_element_located((By.ID, "subdivision"))))

        core_view_lines = (driver.find_element(By.CLASS_NAME, "core-view-summary")
                           .find_elements(By.CLASS_NAME, "core-view-line"))

        alpha2_code = short_name = short_name_lower_case = full_name = alpha3_code = numeric_code = remarks = \
            independent = territory_name = status = None

        for core_view in core_view_lines:
            field_name = core_view.find_element(By.CLASS_NAME, "core-view-field-name").text

            if core_view.find_elements(By.CLASS_NAME, "core-view-field-value"):
                field_value = core_view.find_element(By.CLASS_NAME, "core-view-field-value").text

                if field_value is not None and field_value != "":
                    field_value.replace("*", "")
                    match field_name:
                        case "Alpha-2 code":
                            alpha2_code = field_value
                        case "Short name":
                            short_name = field_value
                        case "Short name lower case":
                            short_name_lower_case = field_value
                        case "Full name":
                            full_name = field_value
                        case "Alpha-3 code":
                            alpha3_code = field_value
                        case "Numeric code":
                            numeric_code = int(field_value)
                        case "Remarks":
                            remarks = field_value
                        case "Independent":
                            independent = field_value
                        case "Territory name":
                            territory_name = field_value
                        case "Status":
                            status = field_value

        country = Country(alpha2_code=alpha2_code, short_name=short_name, short_name_lower_case=short_name_lower_case,
                          full_name=full_name, alpha3_code=alpha3_code, numeric_code=numeric_code, remarks=remarks,
                          independent=independent, territory_name=territory_name, status=status,
                          subdivision_categories=get_subdivision_categories(), subdivisions=get_subdivisions(),
                          additional_information=get_additional_information(), change_history=get_change_history())
        countries.append(country)

        with open("/json/countries/" + alpha2_code + ".json", "w+", encoding="utf-8") as country_file:
            country_file.write(json.dumps(country, ensure_ascii=False, indent=4).replace('""', "null")
                            .replace("code3166_2", "3166-2_code"))
            country_file.close()

    return countries


driver = get_chrome_driver()

JSON_FOLDER = "/json"
os.makedirs(JSON_FOLDER, exist_ok=True)
os.makedirs(JSON_FOLDER + "/countries", exist_ok=True)

with open(JSON_FOLDER + "/all_countries.json", "w+", encoding="utf-8") as all_countries_file:
    all_countries_file.write(json.dumps(get_countries(), ensure_ascii=False, indent=4).replace('""', "null")
                         .replace("code3166_2", "3166-2_code"))
    all_countries_file.close()

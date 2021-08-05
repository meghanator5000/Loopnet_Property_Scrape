import json
#from queue import Empty
#import multiprocessing as mp
# import sys
# import os
# import glob
#import time
import datetime
#from bs4.element import PageElement
import pandas as pd
import numpy as np
#import requests
#from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.common.exceptions import (NoSuchElementException,StaleElementReferenceException,TimeoutException)
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
import re
from pandas import DataFrame

#generate details json
DETAILS_JSON_FILE = "details.json"
DESC_JSON_FILE = "descriptions.json"

# load links_list json dictionary
with open('states.json') as json_file:
    states_list = json.load(json_file)

def new_driver():
    driver = webdriver.Chrome(executable_path=r"/Users/meghanmokate/Desktop/dated date/chromedriver 3")
    driver.maximize_window()  # maximize so all elements are clickable
    return driver

def next_page(driver):
    no_next = 0
    try:
        next_button = driver.find_element_by_xpath('/html/body/form/div[2]/div[4]/div[1]/div[3]/div[27]/a[2]')
        next_button.click()
    except:
        no_next += 1

def get_attribute(driver, states_index): 
    details = []
    link = states_list[states_index]["Link"] 
    for row in driver.find_elements_by_class_name('listingAttributes'):
        link = link,
        row_data = row.find_elements_by_tag_name('tr') 
        misc = ''
        building_size = ''
        sub_type = ''
        prop_type = ''
        status = ''
        price = ''
        try:
            misc = row_data[5].text
        except:
            misc = ''
        try:
            building_size = row_data[4].text
        except:
            building_size = ''
        try:
            sub_type = row_data[3].text
        except:
            sub_type = ''
        try:
            prop_type = row_data[2].text
        except:
            prop_type = ''
        try:
            status = row_data[0].text
        except:
            status = ''
        try:
            price = row_data[1].text
        except:
            price = ''
        detail = {
                   # "Link": link,
                    "Status": status, 
                    "Price": price,
                    "Property Type": prop_type,
                    "Sub-Type": sub_type,
                    "Building Size": building_size,
                    "Misc": misc
        }
        details.append(detail) # might need to change to extend?
    return details

def get_descriptions(driver): 
    descriptions = []
    for name in driver.find_elements_by_class_name('listingDescription'):
        name_data = name.find_elements_by_tag_name('a') 
        city_data = name.find_elements_by_tag_name('b') 
        description = {
                    "Link": name_data[0].get_attribute('href'),
                    "Address": name_data[0].get_attribute('title'),
                    "City": city_data[0].text
        }
        descriptions.append(description)
    return descriptions

# execute functions on webpage
if __name__ == "__main__":
    details = [] 
    descriptions = []
    driver = new_driver()
    for i in range(2):
    #for i in range(len(states_list)): # this is running 50 times yikes 
        driver.get(states_list[i]['Link'])
    
        catch = 0
        pages = 2
        for i in range(len(states_list)):
            try:
                next_button = driver.find_element_by_xpath('/html/body/form/div[2]/div[4]/div[1]/div[3]/div[27]/a[2]') #.get_attribute('href')
                next_button.click()
                pages = pages + 1
                print(pages)
            except:
                catch += 1
            
            if catch >= 1:
                driver.get(states_list[i]['Link']) 
                for i in range(pages):
                # overwrite to result file using the 'w' flag
                    details_json_file = open(DETAILS_JSON_FILE, 'w')
                    json.dump(details, details_json_file, indent=4)   
                    details_json_file.close()   

                    descriptions_json_file = open(DESC_JSON_FILE, 'w')
                    json.dump(descriptions, descriptions_json_file, indent=4)    
                    descriptions_json_file.close()
        
                    details.extend(get_attribute(driver, i))
                    descriptions.extend(get_descriptions(driver))

                    next_page(driver)
    
        try:
            with open(DETAILS_JSON_FILE) as details_json_file:
                details = json.load(details_json_file)
                if details is None or len(details) == 0:
                    raise FileNotFoundError
        except (FileNotFoundError, json.decoder.JSONDecodeError):
            print(f"no {DETAILS_JSON_FILE}...scraping website for new data")

        with open(DETAILS_JSON_FILE, 'w') as details_json_file:
            json.dump(details, details_json_file, indent=4)
    
        try:     
            with open(DESC_JSON_FILE) as descriptions_json_file:
                descriptions = json.load(descriptions_json_file)
                if descriptions is None or len(descriptions) == 0:
                    raise FileNotFoundError
        except (FileNotFoundError, json.decoder.JSONDecodeError):
            print(f"no {DESC_JSON_FILE}...scraping website for new data")

        with open(DESC_JSON_FILE, 'w') as descriptions_json_file:
            json.dump(descriptions, descriptions_json_file, indent=4)
         
    with open(DETAILS_JSON_FILE, 'w') as details_json_file:
        json.dump(details, details_json_file, indent=4)

    print("all details processes done")

# create dataframe and output to file

attribute = pd.read_json (r'/Users/meghanmokate/Desktop/loop_net_scrape/details.json')
attribute_df = pd.DataFrame(attribute)

descriptions_read = pd.read_json (r'/Users/meghanmokate/Desktop/loop_net_scrape/descriptions.json')
descriptions_df = pd.DataFrame(descriptions_read)

properties = pd.concat([attribute_df, descriptions_df],axis=1)

# Clean up dataframe
properties['Sub-Type'] = properties['Sub-Type'].astype(str)
properties['Misc'] = properties['Misc'].astype(str)
properties['Map_1'] = np.where(properties.Misc.str.contains('Building Class'), 'Building Class',
                   np.where(properties.Misc.str.contains('Space'), 'Spaces',
                   np.where(properties.Misc.str.contains('Building Size: '), 'Building Size',
                   np.where(properties.Misc.str.contains('Cap Rate'), 'Cap Rate',
                   np.where(properties.Misc.str.contains('Lot Size'), 'Lot Size',
                   np.where(properties.Misc.str.contains('Year Built'), 'Year Built', ''))))))

properties['Map_2'] = np.where(properties["Sub-Type"].str.contains('Building Class'), 'Building Class',
                   np.where(properties["Sub-Type"].str.contains('Space'), 'Spaces',
                   np.where(properties["Sub-Type"].str.contains('Building Size: '), 'Building Size',
                   np.where(properties["Sub-Type"].str.contains('Cap Rate'), 'Cap Rate',
                   np.where(properties["Sub-Type"].str.contains('Lot Size'), 'Lot Size',
                   np.where(properties["Sub-Type"].str.contains('Year Built'), 'Year Built', ''))))))

properties['Map_3'] = np.where(properties["Building Size"].str.contains('Building Class'), 'Building Class',
                   np.where(properties["Building Size"].str.contains('Space'), 'Spaces',
                   np.where(properties["Building Size"].str.contains('Building Size: '), 'Building Size',
                   np.where(properties["Building Size"].str.contains('Cap Rate'), 'Cap Rate',
                   np.where(properties["Building Size"].str.contains('Lot Size'), 'Lot Size',
                   np.where(properties["Building Size"].str.contains('Year Built'), 'Year Built', ''))))))                   

properties["Building Class"] = np.where(properties["Map_1"].str.contains("Building Class"), properties["Misc"], 
                            np.where(properties["Map_2"].str.contains("Building Class"), properties["Sub-Type"],
                            np.where(properties["Map_3"].str.contains("Building Class"), properties["Building Size"], '')))

properties["Space"] = np.where(properties["Map_1"].str.contains("Space"), properties["Misc"], 
                            np.where(properties["Map_2"].str.contains("Space"), properties["Sub-Type"],
                            np.where(properties["Map_3"].str.contains("Space"), properties["Building Size"], '')))

properties["Cap Rate"] = np.where(properties["Map_1"].str.contains("Cap Rate"), properties["Misc"], 
                            np.where(properties["Map_2"].str.contains("Cap Rate"), properties["Sub-Type"],
                            np.where(properties["Map_3"].str.contains("Cap Rate"), properties["Building Size"], '')))

properties["Lot Size"] = np.where(properties["Map_1"].str.contains("Lot Size"), properties["Misc"], 
                            np.where(properties["Map_2"].str.contains("Lot Size"), properties["Sub-Type"],
                            np.where(properties["Map_3"].str.contains("Lot Size"), properties["Building Size"], '')))


properties["Year Built"] = np.where(properties["Map_1"].str.contains("Year Built"), properties["Misc"], 
                            np.where(properties["Map_2"].str.contains("Year Built"), properties["Sub-Type"],
                            np.where(properties["Map_3"].str.contains("Year Built"), properties["Building Size"], '')))

properties["BS1"] = np.where(properties["Map_1"].str.contains("Building Size"), properties["Misc"], 
                            np.where(properties["Map_2"].str.contains("Building Size"), properties["Sub-Type"],
                            np.where(properties["Map_3"].str.contains("Building Size"), properties["Building Size"], '')))

properties['Misc'] = properties['Misc'].str.replace('Building Class ', '')
properties['Misc'] = properties['Misc'].str.replace('Building Size: ', '')
properties['Misc'] = properties['Misc'].str.replace('Spaces: ', '')
properties['Misc'] = properties['Misc'].str.replace('Cap Rate: ', '')
properties['Misc'] = properties['Misc'].str.replace('Lot Size: ', '')
properties['Misc'] = properties['Misc'].str.replace('Year Built ', '')
properties['Price'] = properties['Price'].str.replace('Price: ', '')
properties['Status'] = properties['Status'].str.replace('Status: ', '')
properties['Property Type'] = properties['Property Type'].str.replace('Property Type: ', '')
properties['Sub-Type'] = properties['Sub-Type'].str.replace('Sub-Type: ', '')
properties['Sub-Type'] = properties['Sub-Type'].str.replace('Building Class ', '')
properties['Sub-Type'] = properties['Sub-Type'].str.replace('Building Size: ', '')
properties['Sub-Type'] = properties['Sub-Type'].str.replace('Spaces: ', '')
properties['Sub-Type'] = properties['Sub-Type'].str.replace('Cap Rate: ', '')
properties['Sub-Type'] = properties['Sub-Type'].str.replace('Lot Size: ', '')
properties['Sub-Type'] = properties['Sub-Type'].str.replace('Year Built ', '')
properties['Building Size'] = properties['Building Size'].str.replace('Building Size: ', '')
properties['Building Size'] = properties['Building Size'].str.replace('Building Class ', '')
properties['Building Size'] = properties['Building Size'].str.replace('Spaces: ', '')
properties['Building Size'] = properties['Building Size'].str.replace('Cap Rate: ', '')
properties['Building Size'] = properties['Building Size'].str.replace('Lot Size: ', '')
properties['Building Size'] = properties['Misc'].str.replace('Year Built ', '')
properties['BS1'] = properties['BS1'].str.replace('Building Size: ', '')
properties["Year Built"] = properties["Year Built"].str.replace('Year Built ', '')
properties['Lot Size'] = properties['Lot Size'].str.replace('Lot Size: ', '')
properties['Building Class'] = properties['Building Class'].str.replace('Building Class ', '')
properties['Cap Rate'] = properties['Cap Rate'].str.replace('Cap Rate: ', '')
properties['Lot Size'] = properties['Lot Size'].str.replace('Lot Size: ', '')
properties["Sub-Type"] = np.where(properties["Sub-Type"].str.contains(" SF"), '', properties["Sub-Type"])                             

properties = properties.drop_duplicates()
properties = properties[['Status', 'Address', 'City', 'Price', 'Property Type', 'Sub-Type', 'BS1', 'Link', "Year Built", 'Lot Size', 'Building Class', 'Cap Rate']]
properties = properties.rename(columns = {"BS1": "Building Size"})

current_date = datetime.datetime.now()
date = str(current_date.month)+'.'+str(current_date.day)+'.'+str(current_date.year)

print(properties)
properties.to_csv(str('properties_' + date + '.csv'))

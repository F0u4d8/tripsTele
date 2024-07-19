#from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait , Select
from selenium.webdriver.support import expected_conditions as EC
from utils import get_sites_for_departure_and_destination , get_code_for_departure ,get_code_for_destination ,get_country_for_site_and_destination,tuiCheck,airToursChck,get_country_for_destination,deturChck ,sunwebCheck
import re
from datetime import datetime, timedelta
from urllib.parse import urlencode, urlparse, parse_qs, urlunparse ,quote_plus
import calendar
from seleniumwire import webdriver
import requests
import json
import time
import random




def calculate_return_date(departure_date, duration):
    duration = int(duration)
    # Parse the departure date
    departure_date_obj = datetime.strptime(departure_date, "%Y-%m-%d")
    
    # Calculate the return date by adding the duration
    return_date_obj = departure_date_obj + timedelta(days=duration)
    
    # Format the return date back to string
    return_date = return_date_obj.strftime("%Y-%m-%d")
    
    return return_date


def transfer_date_format(date_str):
    # Parse the date from the original format
    date_obj = datetime.strptime(date_str, '%Y-%m-%d')
    # Format the date to the new format
    new_date_str = date_obj.strftime('%d/%m/%Y')
    return new_date_str

def transfer_date_formatToDMY(date_str):
    # Parse the date from the original format
    date_obj = datetime.strptime(date_str, '%Y-%m-%d')
    # Format the date to the new format
    new_date_str = date_obj.strftime('%d-%m-%Y')
    return new_date_str


def transfer_date_formatToYMD(date_str :str) -> str:
    # Parse the date from the original format
    try:
      date_obj = datetime.strptime(date_str, '%Y-%m-%d')
      # Format the date to the new format
      new_date_str = date_obj.strftime('%Y%m%d')
      return new_date_str
    except:
        return



def load_proxies(file_path):
    with open(file_path, 'r') as file:
        proxies = [line.strip() for line in file if line.strip()]
    return proxies

# Load proxies from the file
proxies = load_proxies('proxies.txt')

# Function to get a random proxy
def get_random_proxy():
    return random.choice(proxies)


""" 
def scrape_norwegianholidays(departure, destination, date, duration, rooms):
   options = webdriver.ChromeOptions()
   #options.add_argument('--headless')  # Run in headless mode for performance

   prefs = {"profile.default_content_setting_values.notifications" : 2}
   options.add_experimental_option("prefs",prefs)
   options.add_argument("--start-maximized")
   driver = webdriver.Chrome(options=options)
 
    # Define the URL of the page
   return_date = calculate_return_date(date, duration)
   code= get_code_for_destination(destination ,'norwegianholidays')
   base_url = 'https://www.norwegianholidays.com/se/sok?'
   params = {
        'origins': departure,
        'destinations':code ,
        'from': date,
        'to': return_date,
        'flexibleDates': 'false' ,
        'rooms': ','.join([f"{room['adults']}-{room['children']}" for room in rooms])
    }
    
   url = base_url + '&'.join([f"{key}={value}" for key, value in params.items()])  
   driver.get(url)
   wait = WebDriverWait(driver, 10)
   try:
    container = wait.until(EC.presence_of_element_located((By.XPATH, "//div[@class='kkjyus-1 bSieNJ']")))
    deals = container.find_elements(By.XPATH, ".//a")
    if deals:
            first_deal=deals[0]
            deal_url=first_deal.get_attribute('href')
            # Extracting deal details
            
            deal_location = first_deal.find_element(By.XPATH, ".//p[contains(@class, 'sc-18jw3pj-3 gnKdCZ')]").text.strip()
            deal_name = first_deal.find_element(By.XPATH,"//h2[@class='sc-18jw3pj-1 ckZoBz']" ).text.strip()
            deal_price = first_deal.find_element(By.XPATH, ".//div[contains(@class, 'sc-18jw3pj-7 amqaE')]").text.strip()
            flight_deal = first_deal.find_element(By.XPATH, ".//div[contains(@class, 'ou6yye-0 enkNlW')]").text.strip()
            deal_details = first_deal.find_element(By.XPATH, ".//div[contains(@class, 'sc-1eebeid-0 kDpway')]").text.strip()
           
           
            deal_price_match = re.search(r'PER PERSON, INKLUSIVE FLYG\s*([\d\s]+)kr', deal_price)
            if deal_price_match:
     # Extract the matched group and remove any non-digit characters (e.g., spaces)
             deal_price_str = deal_price_match.group(1).replace('\u2009', '').replace(',', '').strip()
             try:
                 deal_price_str = deal_price_str.replace(' ', '')
                 deal_price_float = float(deal_price_str)
                 deal_price_float = float(f"{deal_price_float / 1000:.3f}") 
                 deal_price_formatted = f"{deal_price_str} kr per person "
             except ValueError:
        # Handle the case where conversion to float fails
                  deal_price_formatted = "N/A"
                  deal_price_float = None

           
            # Constructing the deal object
            deal_object = {
                "deal_name": deal_name,
                "deal_price": deal_price_formatted,
                "deal_location": deal_location,
                "flight_deal": flight_deal,
                "deal_details": deal_details,
               
                "floatPrice":deal_price_float,"url":deal_url
                
            }
            driver.quit()
            return deal_object
   except: 
            driver.quit()
            return 
"""        
def scrape_solresor(departure, destination, date,till, duration, rooms):

   proxy = get_random_proxy()
   proxies_dict = {
        'http': proxy,
        'https': proxy,
    }


   app_rooms = []
   for room in rooms:
     api_room = {
        "Adults":int(room["adults"]) ,
        "Children":int(room["children"]),
        "ChildAges": [4] * room["children"]  # Set age 4 for each child
    }
     app_rooms.append(api_room)
   url = "https://www.solresor.se/api/rolfsapi/v2/web/zz/charter/packages/offers/search"
   code= get_code_for_destination(destination ,'solresor')

   headers = {
    "Content-Type": "application/json"}

   body = {
    "rooms": app_rooms,
    "rating": [],
    "tripadvisor": 1,
    "tags": [],
    "charterTags": [],
    "sort": "price",
    "stopOver": {
        "max": 2
    },
    "departureDate": {
        "min": date,
        "max": till
    },
    "tripLength": {
        "min":int(duration) ,
        "max": int(duration)  + 1
    },
    "airport": departure,
    "destinations": [
int(code)
    ],
    "mode": "dateCalendar"
}

   response = requests.post(url, headers=headers, data=json.dumps(body),proxies=proxies_dict)
   try:
       data=response.json()
       deal=data[0]
       print(deal)
       deal_object = {
                "deal_name": deal["hotel"],
                "deal_price": "full price" + str(deal["priceSek"])  + "kr and " + str(deal["pricepp"])  + "kr per person" ,
                "deal_location": deal["destination_country"] + "-" + deal["destination_city"],
                "flight_deal": deal["arrival_date"] + "-" + deal["return_date"],
                "deal_details": deal["highlighted_facilities"] +"\n"+ deal["facilities_text"]+"\n"+ deal["nearby_facilities"],
           
                "floatPrice":float(deal["pricepp"] / 1000)  
                ,"url":deal["url"]
                
            }
       return deal_object
       
   except: 
            return 
       







"""
def scrape_solresor(departure, destination, date, duration, rooms):
   options = webdriver.ChromeOptions()
   #options.add_argument('--headless')  # Run in headless mode for performance

   prefs = {"profile.default_content_setting_values.notifications" : 2}
   options.add_experimental_option("prefs",prefs)
   options.add_argument("--start-maximized")
   driver = webdriver.Chrome(options=options)

# Define the URL of the page
   base_url = 'https://www.solresor.se/sok-packages?'
   params = {
        'airport': departure,
        'date': date,
        'duration': duration,
        'destinations': destination
    }
    
   for i, room in enumerate(rooms):
        params[f'Adults_{i}'] = room['adults']
        params[f'Children_{i}'] = room['children']
    
   url = base_url + '&'.join([f"{key}={value}" for key, value in params.items()])  
   driver.get(url)
   wait = WebDriverWait(driver, 10)
   try:
    deals = wait.until(EC.presence_of_all_elements_located((By.XPATH, "//div[@data-v-889f8517 and @class='booking__hotel-item' ]")))
    if deals:
            first_deal = deals[0]

            # Extracting deal details
            deal_location = first_deal.find_element(By.XPATH, ".//div[contains(@class, 'd-block')]").text.strip()
            deal_name = first_deal.find_element(By.XPATH, ".//div[contains(@class, 'text-capitalize d-inline px-0 h5 d-inline font-weight-semibold mb-0 pr-3')]").text.strip()
            deal_price = first_deal.find_element(By.XPATH, ".//div[contains(@class, 'd-flex flex-column align-items-center secondary-font')]").text.strip()
            flight_deal = first_deal.find_element(By.XPATH, ".//button[contains(@class, 'btn btn-link text-dark-gray font-weight-normal p-0 text-left text-decoration-underline')]").text.strip()
            deal_details = first_deal.find_element(By.XPATH, ".//div[contains(@class, 'text-truncate text-sm-truncate-0')]").text.strip()
            deal_image_url=None
            try:
              imageDiv=first_deal.find_element(By.XPATH, ".//div[contains(@class, 'aspect-ratio__content z-1 position-relative')]")
              image_element = imageDiv.find_element(By.CLASS_NAME, "responsive-image__thumbnail")
              deal_image_url = image_element.get_attribute('src')
            
            except:
                deal_image_url:None

            
            deal_price_match = re.search(r'fr\.\s*([\d\s,]+):-\s*per person', deal_price)
            if deal_price_match:
                deal_price_str = deal_price_match.group(1).replace('\u2009', '').replace(',', '').strip()
                try:
                 deal_price_float = float(deal_price_str)
                 deal_price_float = float(f"{deal_price_float / 1000:.3f}") 

                 deal_price_formatted = f"{deal_price_str} kr per person "
                except ValueError:
        # Handle the case where conversion to float fails
                  deal_price_formatted = "N/A"
                  deal_price_float = None

           
            # Constructing the deal object
            deal_object = {
                "deal_name": deal_name,
                "deal_price": deal_price_formatted,
                "deal_location": deal_location,
                "flight_deal": flight_deal,
                "deal_details": deal_details,
                "deal_image_url": deal_image_url,
                "floatPrice":deal_price_float,"url":url
                
            }
            driver.quit()
            return deal_object

   except: 
            driver.quit()
            return 
        
    """    
        

def scrape_norwegianholidays(departure, destination, date, duration, rooms):
   proxy = get_random_proxy()
   proxies_dict = {
        'http': proxy,
        'https': proxy,
    }

   app_rooms = []
   for room in rooms:
     api_room = {
        "numberOfAdults":int(room["adults"]) ,
        "numberOfChildren":int(room["children"]),
        "childrenAges": [4] * room["children"]  # Set age 4 for each child
    }
     app_rooms.append(api_room)
   url = "https://bkkbbi8sf9.execute-api.eu-west-1.amazonaws.com/prod/search?frontDomain=www.norwegianholidays.com&countryCode=se"
   code= get_code_for_destination(destination ,'norwegianholidays')
   return_date = calculate_return_date(date, duration)
   

   headers = {
    "Content-Type": "application/json"}
   body = {
   "origins":[departure],"destinations":[code],"dates":{"from":date,"to":return_date,"flexibleDates":False},"roomConfigurations":app_rooms,"affiliateId":"tripx"
}
   response = requests.post(url, headers=headers, data=json.dumps(body),proxies=proxies_dict)
   
   try:
       data=response.json()
       hotel=data["hotels"][0]
       result=data["results"][0]

       deal_object = {
                "deal_name": hotel["name"],
                "deal_price":  str(result["price"])  + "kr per person" ,
                "deal_location": hotel["location"]["country"] + "-" + hotel["location"]["city"] + "-" + hotel["location"]["destination"],
                "flight_deal": result["flightInfo"]["leaveDepartureTime"] + "-" + result["flightInfo"]["leaveAirportFromCode"],
                "deal_details":hotel["shortDescription"],
           
                "floatPrice":float(result["price"] / 1000)  
                ,"url":"https://www.norwegianholidays.com/se/c/" + hotel["hotelSlug"]
                
            }
       return deal_object
       
   except: 
            return 
       
 
def scrape_mixxtravel(departure, destination, date, duration, rooms ,):

    
   options = webdriver.ChromeOptions()
   #options.add_argument('--headless')  # Run in headless mode for performance

   prefs = {"profile.default_content_setting_values.notifications" : 2}
   options.add_argument("--disable-gpu")
   options.add_argument("--disable-extensions")
   options.add_argument("--disable-dev-shm-usage")
   options.add_argument("--no-sandbox")

# Disable loading images
   options.add_argument("--blink-settings=imagesEnabled=false")
   options.add_experimental_option("prefs",prefs)

   options.add_argument("--start-maximized")
   driver = webdriver.Chrome(options=options )

   code= get_code_for_destination(destination ,'mixxtravel')
   departureList=[{'Köpenhamn':'CPH'} ,{'Göteborg':'GOT'} , {'Norrköping':'NRK'} ,{'Stockholm-Arlanda':'ARN'} ]
   def get_departure_name(code, departure_list):
    for departure in departure_list:
        for name, departure_code in departure.items():
            
            if departure_code == code:
                return name
    return None
# Define the URL of the page
   base_url = 'https://www.mixxtravel.se/Packages?'
   params = {
        'Departure': departure,
        'Arrival':code ,
        'DName':get_departure_name(departure, departureList) ,
        'CheckIn': transfer_date_format(date),
        'Night': duration,
        'Adult': rooms[0]['adults'] , 'Child': rooms[0]['children'] , 
    }
    
   if rooms[0]['children'] > 0:
    params['ChildAge1'] = 12
    
   url = base_url + '&'.join([f"{key}={value}" for key, value in params.items()])  
   driver.get(url)
   wait = WebDriverWait(driver, 10)
   
   time.sleep(5)   
   try:
     xpath = "//div[@class='ssBt']"
     text_content = "Prisökning"
     button = wait.until(EC.element_to_be_clickable((By.XPATH, f"{xpath}[contains(text(), '{text_content}')]")))
     button.click()   
     time.sleep(10)
     deals = wait.until(EC.presence_of_all_elements_located((By.XPATH, "//div[@class='wideHotelBox wideHotelBoxOrg']")))
     if deals:
            first_deal = deals[1]

            # Extracting deal details
            deal_location = first_deal.find_element(By.XPATH, ".//div[contains(@class, 'wcLocation')]").text.strip()
            deal_name = first_deal.find_element(By.XPATH, ".//div[contains(@class, 'wcTitle')]").text.strip()
            
            deal_price = first_deal.find_element(By.XPATH, ".//div[contains(@class, 'wcMainPrice')]").text.strip()
            flight_deal = ''
            deal_details = first_deal.find_element(By.XPATH, ".//div[contains(@class, 'wcDesc')]").text.strip()
            deal_image_url=None
  
            deal_price_match = re.search(r'([\d\s.,]+):-', deal_price)
            if deal_price_match:
                deal_price_str = deal_price_match.group(1).replace('\u2009', '').replace(',', '').strip()
                try:
                 deal_price_float = float(deal_price_str)
                 deal_price_formatted = f"{deal_price_float:.2f} kn 14 per person"
                except ValueError:
        # Handle the case where conversion to float fails
                  deal_price_formatted = "N/A"
                  deal_price_float = None
                
           
            # Constructing the deal object
            deal_object = {
                "deal_name": deal_name,
                "deal_price": deal_price_formatted,
                "deal_location": deal_location,
                "flight_deal": flight_deal,
                "deal_details": deal_details,
                "deal_image_url": deal_image_url,
                "floatPrice":deal_price_float ,"url":url
                
            }
            driver.quit()
            return deal_object

   except: 
            driver.quit()
            return 


def scrape_ving(departure, destination, date, duration, rooms):
    
   proxy = get_random_proxy()
   proxies_dict = {
        'http': proxy,
        'https': proxy,
    }    
   print(proxies_dict)
   code= get_code_for_destination(destination ,'ving')
   country=get_country_for_site_and_destination('ving',destination)
   country = get_code_for_destination(country,'ving')
    

   base_url = "https://independentweb.nltg.com/api/proxy"
   rooms_str ='|' + '|'.join([','.join(['42'] * room['adults'] + ['6'] * room['children']) for room in rooms])

   query_params = {
    "departureAirportId": departure,
    "resortId": code,
    "areaId": '0',
    "departureDate": date,
    "returnDate": calculate_return_date(date, duration),
    "duration": -1,
    "userId": "Z01",
    "siteId": 1
}

# Use urlencode for the inner query string
   inner_query_string = '&'.join([f"{key}={quote_plus(str(value))}" for key, value in query_params.items()])
    
    # Encode the entire inner URL correctly
   encoded_inner_url = quote_plus(f"//bwoty-independentwebapi-prd.azurewebsites.net/api/package/hotels?{inner_query_string}")

    # Construct the final URL
   url = f"{base_url}?url={encoded_inner_url}%26rooms%3D{rooms_str}"




   print(url)
   response = requests.get(url,proxies=proxies_dict)
   
   try:
       data=response.json()
       result= data["result"]
       data=result["hotels"]
       deal = min(data, key=lambda x: x['priceInfo']['totalPrice'])
       deal_object = {
                "deal_name": deal["name"],
                "deal_price": "full price" + str(deal['priceInfo']['totalPrice'])  + "kr and " + str(deal['priceInfo']['twoAdultsPricePerPerson'])  + "kr per adult" ,
                "deal_location": deal['geographical']['district']['name'] ,
                "flight_deal": "",
                "deal_details": deal["introText"] ,
           
                "floatPrice":float(deal['priceInfo']['twoAdultsPricePerPerson'] / 1000)  
                ,"url":"https://www.ving.se/"+ deal["url"]
                
            }
       print(deal_object)
       return deal_object
       
   except: 
            return 
 

        
"""        
def scrape_ving(departure, destination, date, duration, rooms):
   options = webdriver.ChromeOptions()
   options.add_argument('--headless')  # Run in headless mode for performance

   prefs = {"profile.default_content_setting_values.notifications" : 2}
   options.add_experimental_option("prefs",prefs)
   driver = webdriver.Chrome(options=options)

   code= get_code_for_destination(destination ,'ving')
   country=get_country_for_site_and_destination('ving',destination)
   country = get_code_for_destination(country,'ving')

# Define the URL of the page
   base_url = 'https://www.ving.se/boka-paketresa?'
   params = {
        'QueryDepID': departure,
        'QueryCtryID':country,
        'QueryAreaID':'0',
        'QueryResID':code ,
        'QueryDepDate':transfer_date_formatToYMD(date),
        'QueryRetDate':transfer_date_formatToYMD(calculate_return_date(date , duration)),
        'CategoryId':'3',        
        'QueryRoomAges': '|'.join([','.join(['42'] * room['adults'] + ['4'] * room['children']) for room in rooms])
    }
    
  
    
   url = base_url + '&'.join([f"{key}={value}" for key, value in params.items()])  
   driver.get(url)
   wait = WebDriverWait(driver, 10)
   try:
    xpath = "//button[@class='idun-consent-modal__button style__Button-sc-mgj152-0 iNhXwa']"
    text_content = "Godkänn alla"
    button = wait.until(EC.element_to_be_clickable((By.XPATH, f"{xpath}[contains(text(), '{text_content}')]")))
    button.click()   
    time.sleep(5)
   
    deals = wait.until(EC.presence_of_all_elements_located((By.XPATH, "//div[@class='iw-hotel-list-item']")))
    if deals:
            first_deal = deals[0]
            # Extracting deal details
            deal_location = first_deal.find_element(By.XPATH, ".//div[contains(@class, 'hotelHitContentHeader__HotelHitContentSubTitleContainer-sc-7xzxtm-4 iYFxON')]").text.strip()
            deal_name = first_deal.find_element(By.XPATH, ".//h3[contains(@class, 'hotelHitContentHeader__HotelHitContentTitle-sc-7xzxtm-3 buLUCp')]").text.strip()
            url=first_deal.find_element(By.XPATH, ".//a[contains(@class, 'hotelHitLink__HotelHitLink-sc-1cfcrr-0 jrUHqW')]").get_attribute('href')
            try:
             deal_price = first_deal.find_element(By.XPATH, ".//div[contains(@class, 'hotelHitContentPrice__PricePerPerson-sc-1okdkzl-13 dIWpoS')]").text.strip()
            except:
                 deal_price = first_deal.find_element(By.XPATH, ".//div[contains(@class, 'hotelHitContentPrice__CurrentPrice-sc-1okdkzl-11 jNNwFR')]").text.strip()

            flight_deal = ''
            deal_details = first_deal.find_element(By.XPATH, ".//ul[contains(@class, 'hotelHitContentBody__UspList-sc-kdxujw-6 ehMULO')]").text.strip()
            deal_image_url=None
  
            deal_price_match = re.search(r'([\d\s.,]+):-/person', deal_price)
            if deal_price_match:
                deal_price_str = deal_price_match.group(1).replace('\u2009', '').replace(',', '').strip()
                try:
                 deal_price_float = float(deal_price_str)
                 deal_price_formatted = f"{deal_price_float:.2f} kn per person"
                except ValueError:
        # Handle the case where conversion to float fails
                  deal_price_formatted = "N/A"
                  deal_price_float = None
                
           
            # Constructing the deal object
            deal_object = {
                "deal_name": deal_name,
                "deal_price": deal_price_formatted,
                "deal_location": deal_location,
                "flight_deal": flight_deal,
                "deal_details": deal_details,
                "deal_image_url": deal_image_url,
                "floatPrice":deal_price_float ,"url":url
                
            }
            driver.quit()
            return deal_object

   except: 
            driver.quit()
            return 
 """       
             

def scrape_ving2(departure, destination, date, duration, rooms,type):
    
   options = webdriver.ChromeOptions()
   options.add_argument('--headless')  # Run in headless mode for performance
   options.add_argument("--start-maximized")
   proxy = get_random_proxy()
   seleniumwire_options = {
    "proxy": {
        "http": proxy,
        "https": proxy
    },
}

   prefs = {"profile.default_content_setting_values.notifications" : 2}
   options.add_argument("--disable-gpu")
   options.add_argument("--disable-extensions")
   options.add_argument("--disable-dev-shm-usage")
   options.add_argument("--no-sandbox")

# Disable loading images
   options.add_argument("--blink-settings=imagesEnabled=false")
   options.add_experimental_option("prefs",prefs)
   driver = webdriver.Chrome(options=options ,seleniumwire_options=seleniumwire_options)

   code= get_code_for_destination(destination ,'ving')
   country=get_country_for_site_and_destination('ving',destination)
   country = get_code_for_destination(country,'ving')

# Define the URL of the page
   base_url = 'https://www.ving.se/boka-resa?'
   if type=="month":
       params = {
           'QueryDepMonths':date,
       }
   else:
      params = {
        'QueryDepDate': transfer_date_formatToYMD(date),}

   params = {
        'QueryDepID': departure,
        'QueryCtryID':country,
        'QueryAreaID':'0',
        'QueryResID':code ,
        'QueryDur':duration,
        'CategoryId':'2',        
        'QueryRoomAges': '|'.join([','.join(['42'] * room['adults'] + ['4'] * room['children']) for room in rooms])
    }
    
   
    
   url = base_url + '&'.join([f"{key}={value}" for key, value in params.items()])  
   driver.get(url)
   wait = WebDriverWait(driver, 10)
   try:
    xpath = "//button[@class='idun-consent-modal__button style__Button-sc-mgj152-0 iNhXwa']"
    text_content = "Godkänn alla"
    button = wait.until(EC.element_to_be_clickable((By.XPATH, f"{xpath}[contains(text(), '{text_content}')]")))
    button.click()   
    time.sleep(5)
    xpath = "//button[@class='tcne-cf-sort-buttons__item']"
    button = wait.until(EC.element_to_be_clickable((By.XPATH, f"{xpath}")))
    button.click()    
    time.sleep(2)

    deals = wait.until(EC.presence_of_all_elements_located((By.XPATH, "//div[@class='tcne-cf-hotel']")))
    if deals:
            first_deal = deals[0]
            # Extracting deal details
            deal_location = first_deal.find_element(By.XPATH, ".//div[contains(@class, 'hotelHitContentHeader__HotelHitContentSubTitleContainer-sc-7xzxtm-5 jAVFkj')]").text.strip()
            deal_name = first_deal.find_element(By.XPATH, ".//h3[contains(@class, 'hotelHitContentHeader__HotelHitContentTitle-sc-7xzxtm-4 fAfpcp')]").text.strip()
            url=first_deal.find_element(By.XPATH, ".//a[contains(@class, 'hotelHitContentHeader__HotelHitCoverAnchor-sc-7xzxtm-3 eVcirb')]").get_attribute('href')
            try:
             deal_price = first_deal.find_element(By.XPATH, ".//div[contains(@class, 'hotelHitContentPrice__PricePerPerson-sc-1okdkzl-14 jBUlBl')]").text.strip()
            except:
             deal_price = first_deal.find_element(By.XPATH, ".//div[contains(@class, 'hotelHitContentPrice__CurrentPrice-sc-1okdkzl-12 kKzlAT')]").text.strip()

            flight_deal = ''
            deal_details = first_deal.find_element(By.XPATH, ".//ul[contains(@class, 'hotelHitContentBody__UspList-sc-kdxujw-5 eaNIss')]").text.strip()
            deal_image_url=None
  
            deal_price_match = re.search(r'([\d\s.,]+):-/person', deal_price)
            if deal_price_match:
                deal_price_str = deal_price_match.group(1).replace('\u2009', '').replace(',', '').strip()
                try:
                 deal_price_float = float(deal_price_str)
                 deal_price_formatted = f"{deal_price_float:.2f} kn per person"
                except ValueError:
        # Handle the case where conversion to float fails
                  deal_price_formatted = "N/A"
                  deal_price_float = None
                
           
            # Constructing the deal object
            deal_object = {
                "deal_name": deal_name,
                "deal_price": deal_price_formatted,
                "deal_location": deal_location,
                "flight_deal": flight_deal,
                "deal_details": deal_details,
                "deal_image_url": deal_image_url,
                "floatPrice":deal_price_float ,"url":url
                
            }
            driver.quit()
            return deal_object
   except: 
            driver.quit()
            return 


 
def scrape_tui(departure, destination, date, days ,duration, rooms , type):
   options = webdriver.ChromeOptions()
   #options.add_argument('--headless')  # Run in headless mode for performance

   prefs = {"profile.default_content_setting_values.notifications" : 2}
   options.add_argument("--disable-gpu")
   options.add_argument("--disable-extensions")
   options.add_argument("--disable-dev-shm-usage")
   options.add_argument("--no-sandbox")

# Disable loading images
   options.add_argument("--blink-settings=imagesEnabled=false")
   options.add_experimental_option("prefs",prefs)

   proxy = get_random_proxy()
   seleniumwire_options = {
    "proxy": {
        "http": proxy,
        "https": proxy
    },
}

   driver = webdriver.Chrome(options=options ,seleniumwire_options=seleniumwire_options)

   code= get_code_for_destination(destination ,'tui')
   def get_duration_code(days):
    if days == '7':
        return '7114'
    elif days == '14':
        return '1413'
    elif days == '21':
        return '211'
    elif days == '28':  # 4 weeks
        return '2918'
    else:
        return

   flexibility='false'
   monthSearc='false'
   flexibleDays='0'
   if type == "month":
    flexibility='true'
    monthSearc='false'
    flexibleDays='14' 
   elif type == "flexibility":
    flexibility='true'
    monthSearc='false'
    flexibleDays= days 
            
   
   # Define the URL of the page
# Define the URL of the page
   base_url = 'https://www.tui.se/se/hitta-din-resa'
   params = {
    'airports%5B%5D': departure,
    'units%5B%5D':tuiCheck(code),
    'when': transfer_date_formatToDMY(date),
    'until': '',
    'flexibility': flexibility,
    'monthSearch': monthSearc,
    'flexibleDays': flexibleDays,
    'flexibleMonths': '',
    'noOfAdults': sum(room['adults'] for room in rooms),
    'noOfChildren': sum(room['children'] for room in rooms),
    'childrenAge': '',
    'duration': get_duration_code(duration),
    'searchRequestType': 'ins',
    'searchType': 'search',
    'sp': 'true',
    'multiSelect': 'true',
    'isVilla': 'false',
    'reqType': '',
    'sortBy': 'totalPriceAsc',
    'nearByAirports': 'true'
}

# Construct the URL with parameters
   url = base_url + '?' + '&'.join([f'{key}={value}' for key, value in params.items()]) 
   driver.get(url)
   wait = WebDriverWait(driver, 10)
   try:
   
     xpath = "//button[@class='button raised blue']"
     text_content = "Godkänn"
     button = wait.until(EC.element_to_be_clickable((By.XPATH, f"{xpath}[contains(text(), '{text_content}')]")))
     button.click()   
     time.sleep(2)   
     deals = wait.until(EC.presence_of_all_elements_located((By.XPATH, "//section[@class=' ResultListItemV2__resultItem']")))
     if deals:
            first_deal = deals[0]
            # Extracting deal details
            deal_location = first_deal.find_element(By.XPATH, ".//div[contains(@class, 'ResultListItemV2__GeoLocation')]").text.strip()
            deal_name = first_deal.find_elements(By.XPATH, ".//div[contains(@class, 'ResultListItemV2__details')]")
            deal_name=deal_name[0].find_elements(By.TAG_NAME , "div")[0]
            deal_name =deal_name.find_element(By.TAG_NAME , "h5")
            url=deal_name.find_element(By.TAG_NAME , "a").get_attribute('href')
            deal_name=deal_name.text.strip()
            flight_deal = first_deal.find_element(By.XPATH, ".//span[contains(@class, 'ResultListItemV2__flightName')]").text.strip()
            deal_details = first_deal.find_element(By.XPATH, ".//div[contains(@class, 'ResultsListItem__accomFactsContainer')]").text.strip()
            deal_price = first_deal.find_element(By.XPATH, ".//div[contains(@class, 'Column__col ResultListItemV2__packagePrice ResultListItemV2__showPackage')]")
            

        
            deal_price =deal_price.text.split()[0] + deal_price.text.split()[1] 
        
            deal_price_match = re.search(r'([\d\s.,]+):-', deal_price)
            if deal_price_match:
                deal_price_str = deal_price_match.group(1).replace('\u2009', '').replace(',', '').strip()
                try:
                 deal_price_float = float(deal_price_str)
                 deal_price_float = float(f"{deal_price_float / 1000:.3f}") 
                 deal_price_float1=deal_price_float / sum(room['adults'] for room in rooms)
                 deal_price_formatted = f"{deal_price_float:.2f} kn "
                except ValueError:
        # Handle the case where conversion to float fails
                  deal_price_formatted = "N/A"
                  deal_price_float = None
                
           
            # Constructing the deal object
            deal_object = {
                "deal_name": deal_name,
                "deal_price": deal_price_formatted,
                "deal_location": deal_location,
                "flight_deal": flight_deal,
                "deal_details": deal_details,
                "deal_image_url": '',
                "floatPrice":deal_price_float1 ,"url":url
                
            }
            driver.quit()
            return deal_object
   except: 
            driver.quit()
            return 
        



def scrape_airtours(departure, destination, date,till ,duration, rooms):
    
   proxy = get_random_proxy()
   proxies_dict = {
        'http': proxy,
        'https': proxy,
    }
   city_code, region_code, country_code = airToursChck(destination)
   def get_duration_code(days):
    if int(days) < 7 :
      return '1-7'     
    elif int(days) < 9 :
        return '8-9'
    elif int(days) < 14 :
        return '10-14'
    elif int(days) < 15 :
        return '15-15'
    else:
        return '16-999'
    
   participants = []
   participants_distribution = []
    
   for room in rooms:
        room_participants = []
        for _ in range(room['adults']):
            room_participants.append("1994-03-20")  # Example birthdate for adults
        for _ in range(room['children']):
            room_participants.append("2014-03-20")  # Example birthdate for children
        participants.append(room_participants)
        participants_distribution.append(f"{len(room_participants)}")
        
   base_url = 'https://www.airtours.se/api/sitecore/SearchApi/GetSearchResponse?'
   parsed_url = urlparse(base_url)
   query_params = parse_qs(parsed_url.query)     
   query_params['contextitemid'] = "7a6c5943-fc84-4df8-9ef6-58e28362c71e" 
   query_params['isFirstUserRequest'] = "True"
   query_params['offset'] = 0
   query_params['sort'] = 'Price'
        # Flatten participants list into the query parameters
   for i, room_participants in enumerate(participants):
        for j, participant in enumerate(room_participants):
            query_params[f'Participants[{i}][{j}]'] = participant
   query_params['DepartureAirport[0]'] = departure            
   query_params['DepartureDate[0]'] = date
   query_params['DepartureDate[1]'] = till
   query_params['Destination[0]'] = str(city_code) 
   query_params['Duration[0]'] = get_duration_code(duration)
   query_params['TransportType[0]'] = 'Flight'
   query_params['ParticipantsDistribution'] = '|'.join(participants_distribution)     
   query_params['isFirstLoad'] = "True"
   
   
   new_query_string = urlencode(query_params, doseq=True)
 
    # Construct the new URL
   url = urlunparse(parsed_url._replace(query=new_query_string))               
        

   response = requests.get(url,proxies=proxies_dict)
   try:
       data=response.json()
       data=data["results"]
       deal=data[0]
       print(deal)
       deal_object = {
                "deal_name": deal["name"],
                "deal_price":  str(deal["price"]["averagePrice"])  + "kr per person" ,
                "deal_location": deal["countryName"] + "-" + deal["cityName"],
                "flight_deal": deal["departureDateDetail"] + "-" + deal["arrivalDateDetail"],
                "deal_details": ",".join(deal["usps"]),
           
                "floatPrice":float(deal["price"]["averagePrice"] / 1000)  
                ,"url":"https://www.airtours.se/"+ deal["urlWithFilters"]
                
            }
       return deal_object
       
   except: 
            return 

def scrape_sunweb(departure, destination, date,till, duration, rooms):
   proxy = get_random_proxy()
   proxies_dict = {
        'http': proxy,
        'https': proxy,
    }
   city_code, region_code, country_code = sunwebCheck(destination)
   def get_duration_code(days):
    if int(days) < 7 :
      return '1-7'     
    elif int(days) < 9 :
        return '8-9'
    elif int(days) < 14 :
        return '10-14'
    elif int(days) < 15 :
        return '15-15'
    else:
        return '16-999'
    
   participants = []
   participants_distribution = []
    
   for room in rooms:
        room_participants = []
        for _ in range(room['adults']):
            room_participants.append("1994-03-20")  # Example birthdate for adults
        for _ in range(room['children']):
            room_participants.append("2014-03-20")  # Example birthdate for children
        participants.append(room_participants)
        participants_distribution.append(f"{len(room_participants)}")
        
   base_url = 'https://www.sunweb.se/api/sitecore/SearchApi/GetSearchResponse?'
   parsed_url = urlparse(base_url)
   query_params = parse_qs(parsed_url.query)     
   query_params['contextitemid'] = "7a6c5943-fc84-4df8-9ef6-58e28362c71e" 
   query_params['isFirstUserRequest'] = "false"
   query_params['offset'] = 0
   query_params['sort'] = 'Price'
        # Flatten participants list into the query parameters
   for i, room_participants in enumerate(participants):
        for j, participant in enumerate(room_participants):
            query_params[f'Participants[{i}][{j}]'] = participant
   query_params['DepartureAirport[0]'] = departure            
   query_params['DepartureDate[0]'] = date
   query_params['DepartureDate[1]'] = till
   if country_code:
     query_params['Country[0]'] = str(country_code) 
   elif region_code:
    query_params['Region[0]'] = str(region_code)    
       
   query_params['Duration[0]'] = get_duration_code(duration)
   query_params['TransportType[0]'] = 'Flight'
   query_params['ParticipantsDistribution'] = '|'.join(participants_distribution)     
   query_params['isFirstLoad'] = "True"
   
   
   new_query_string = urlencode(query_params, doseq=True)
 
    # Construct the new URL
   url = urlunparse(parsed_url._replace(query=new_query_string))               
        

   response = requests.get(url,proxies=proxies_dict)
   try:
       data=response.json()
       data=data["results"]
       deal=data[0]
       deal_object = {
                "deal_name": deal["name"],
                "deal_price":  str(deal["price"]["averagePrice"])  + "kr per person" ,
                "deal_location": deal["countryName"] + "-" + deal["cityName"],
                "flight_deal": deal["departureDateDetail"] + "-" + deal["arrivalDateDetail"],
                "deal_details": ",".join(deal["usps"]),
           
                "floatPrice":float(deal["price"]["averagePrice"] / 1000)  
                ,"url":"https://www.airtours.se/"+ deal["urlWithFilters"]
                
            }
       return deal_object
       
   except: 
            return 



             
"""
def scrape_airtours(departure, destination, date,till ,duration, rooms):
   options = webdriver.ChromeOptions()
   options.add_argument('--headless')  # Run in headless mode for performance

   prefs = {"profile.default_content_setting_values.notifications" : 2}
   options.add_experimental_option("prefs",prefs)
   driver = webdriver.Chrome(options=options)

   city_code, region_code, country_code = airToursChck(destination)
   def get_duration_code(days):
    if int(days) < 7 :
      return '1-7'     
    elif int(days) < 9 :
        return '8-9'
    elif int(days) < 14 :
        return '10-14'
    elif int(days) < 15 :
        return '15-15'
    else:
        return '16-999'

   base_url = 'https://www.airtours.se/sokresultat?'


   parsed_url = urlparse(base_url)
   query_params = parse_qs(parsed_url.query)

    # Initialize parameters
   participants = []
   participants_distribution = []
    
   for room in rooms:
        room_participants = []
        for _ in range(room['adults']):
            room_participants.append("1994-03-20")  # Example birthdate for adults
        for _ in range(room['children']):
            room_participants.append("2014-03-20")  # Example birthdate for children
        participants.append(room_participants)
        participants_distribution.append(f"{len(room_participants)}")
    
    # Update query parameters
   query_params['DepartureAirport[0]'] = departure
   query_params['DepartureDate[0]'] = date
   query_params['DepartureDate[1]'] = till
   query_params['Country[0]'] = str(country_code)
   query_params['Region[0]'] = str(region_code)
   query_params['City[0]'] = str(city_code)
   query_params['Duration[0]'] = get_duration_code(duration)
   query_params['TransportType'] = 'Flight'
   query_params['sort'] = 'Price'
   query_params['ParticipantsDistribution'] = '|'.join(participants_distribution)
    
    # Flatten participants list into the query parameters
   for i, room_participants in enumerate(participants):
        for j, participant in enumerate(room_participants):
            query_params[f'Participants[{i}][{j}]'] = participant
    
    # Construct the new query string
   new_query_string = urlencode(query_params, doseq=True)
 
    # Construct the new URL
   url = urlunparse(parsed_url._replace(query=new_query_string))
   
   driver.get(url)
   wait = WebDriverWait(driver, 10)
   try:
    xpath = "//button[@class='CookieInfoButton CookieInfoButtonArrow']"
    text_content = "Acceptera cookies "
    button = wait.until(EC.element_to_be_clickable((By.XPATH, f"{xpath}[contains(text(), '{text_content}')]")))
    button.click()   
    time.sleep(5)  

    # Wait for options to be available
   
    
    # Select the option by value
    
    # Wait for the page to reload with sorted results
   
    deals = wait.until(EC.presence_of_all_elements_located((By.XPATH, """""" //div[@class='c-search-result
  
  
  
  
  ']""" """)))

    if deals:
            first_deal = deals[0]
            # Extracting deal details
            deal_location = first_deal.find_element(By.XPATH,""" """.//ol[contains(@class, 'c-breadcrumbs
  c-breadcrumbs--unclickable
  c-search-result__breadcrumbs')]""" """).text.strip()

            deal_name = first_deal.find_element(By.TAG_NAME, "h2").text.strip()

            url=first_deal.find_element(By.TAG_NAME , "a").get_attribute('href')
            
            flight_deal = first_deal.find_element(By.XPATH, ".//div[contains(@class, 'c-search-result__footer-top')]").text.strip()
            deal_details = first_deal.find_element(By.XPATH, ".//ul[contains(@class, 'c-bullet-list o-list-bare c-search-result__usps')]").text.strip()
            deal_price = first_deal.find_element(By.XPATH, ".//div[contains(@class, 'c-price__number m-price m-price--large')]").text.strip()

        
            deal_price_match = re.search(r'([\d\s.,]+):-', deal_price)

            if deal_price_match:
                deal_price_str = deal_price_match.group(1).replace('\u2009', '').replace(',', '').strip()
                try:
                 deal_price_float = float(deal_price_str)
                 deal_price_float = float(f"{deal_price_float / 1000:.3f}") 

                 deal_price_formatted = f"{deal_price_str} kr per person "
                except ValueError:
        # Handle the case where conversion to float fails
                  deal_price_formatted = "N/A"
                  deal_price_float = None
                
           
            # Constructing the deal object
            deal_object = {
                "deal_name": deal_name,
                "deal_price": deal_price_formatted,
                "deal_location": deal_location,
                "flight_deal": flight_deal,
                "deal_details": deal_details,
                "deal_image_url": '',
                "floatPrice":deal_price_float ,"url":url
                
            }
            driver.quit()
            return deal_object
   except: 
            driver.quit()
            return 
        
"""  
"""
def scrape_sunweb(departure, destination, date,till, duration, rooms):
   options = webdriver.ChromeOptions()
   options.add_argument('--headless')  # Run in headless mode for performance

   prefs = {"profile.default_content_setting_values.notifications" : 2}
   options.add_experimental_option("prefs",prefs)
   driver = webdriver.Chrome(options=options)

   city_code, region_code, country_code = airToursChck(destination)
   def get_duration_code(days):
    if int(days) < 7 :
      return '1-7'     
    elif int(days) < 9 :
        return '8-9'
    elif int(days) < 14 :
        return '10-14'
    elif int(days) < 15 :
        return '15-15'
    else:
        return '16-999'

   base_url = 'https://www.sunweb.se/solresor/sog?'


   parsed_url = urlparse(base_url)
   query_params = parse_qs(parsed_url.query)

    # Initialize parameters
   participants = []
   participants_distribution = []
    
   for room in rooms:
        room_participants = []
        for _ in range(room['adults']):
            room_participants.append("1994-03-20")  # Example birthdate for adults
        for _ in range(room['children']):
            room_participants.append("2014-03-20")  # Example birthdate for children
        participants.append(room_participants)
        participants_distribution.append(f"{len(room_participants)}")
    
    # Update query parameters
   query_params['DepartureAirport[0]'] = departure
   query_params['DepartureDate[0]'] = date
   query_params['DepartureDate[1]'] = till
   query_params['Country[0]'] = str(country_code)
   query_params['Region[0]'] = str(region_code)
   query_params['Duration[0]'] = get_duration_code(duration)
   query_params['TransportType'] = 'Flight'
   query_params['sort'] = 'Price'
   query_params['ParticipantsDistribution'] = '|'.join(participants_distribution)
    
    # Flatten participants list into the query parameters
   for i, room_participants in enumerate(participants):
        for j, participant in enumerate(room_participants):
            query_params[f'Participants[{i}][{j}]'] = participant
    
    # Construct the new query string
   new_query_string = urlencode(query_params, doseq=True)
 
    # Construct the new URL
   url = urlunparse(parsed_url._replace(query=new_query_string))
   
   driver.get(url)
   wait = WebDriverWait(driver, 10)
   try:
       
    xpath = "//button[@class='CookieInfoButton CookieInfoButtonArrow']"
    text_content = "Acceptera cookies "
    button = wait.until(EC.element_to_be_clickable((By.XPATH, f"{xpath}[contains(text(), '{text_content}')]")))
    button.click()   
    time.sleep(5)  
    deals = wait.until(EC.presence_of_all_elements_located((By.XPATH, """ """//div[@class='c-search-result
  
  
  
  
  ']""" """)))

    if deals:
            first_deal = deals[0]
            # Extracting deal details
            deal_location = first_deal.find_element(By.XPATH,""" """.//ol[contains(@class, 'c-breadcrumbs
  c-breadcrumbs--unclickable
  c-search-result__breadcrumbs')]""" """).text.strip()

            deal_name = first_deal.find_element(By.TAG_NAME, "h2").text.strip()

            url=first_deal.find_element(By.TAG_NAME , "a").get_attribute('href')
            
            flight_deal = first_deal.find_element(By.XPATH, ".//div[contains(@class, 'c-search-result__footer-top')]").text.strip()
            deal_details = first_deal.find_element(By.XPATH, ".//ul[contains(@class, 'c-bullet-list o-list-bare c-search-result__usps')]").text.strip()
            deal_price = first_deal.find_element(By.XPATH, ".//div[contains(@class, 'c-price__number m-price m-price--large')]").text.strip()

        
            deal_price_match = re.search(r'([\d\s.,]+):-', deal_price)

            if deal_price_match:
                deal_price_str = deal_price_match.group(1).replace('\u2009', '').replace(',', '').strip()
                try:
                 deal_price_float = float(deal_price_str)
                 deal_price_float = float(f"{deal_price_float / 1000:.3f}") 

                 deal_price_formatted = f"{deal_price_str} kr per person "
                except ValueError:
        # Handle the case where conversion to float fails
                  deal_price_formatted = "N/A"
                  deal_price_float = None
                
           
            # Constructing the deal object
            deal_object = {
                "deal_name": deal_name,
                "deal_price": deal_price_formatted,
                "deal_location": deal_location,
                "flight_deal": flight_deal,
                "deal_details": deal_details,
                "deal_image_url": '',
                "floatPrice":deal_price_float ,"url":url
                
            }
            driver.quit()
            return deal_object

   except: 
            driver.quit()
            return 
        
 
"""



def scrape_apollo(departure, destination, date, duration, rooms):
    
   proxy = get_random_proxy()
 
   seleniumwire_options = {
    "proxy": {
        "http": proxy,
        "https": proxy
    },
}

   paxAges_list = []
   paxConfig_list = []
    
   for room in rooms:
        adults = room['adults']
        children = room['children']
        
        # Assuming all adults are 18 and all children are 6 for simplicity
        paxAges_list.extend(['18'] * adults)
        paxAges_list.extend(['6'] * children)
        
        paxConfig_list.append(f"{adults},{children}")
    
   paxAges = ",".join(paxAges_list)
   paxConfig = ";".join(paxConfig_list)
   base_url = 'https://www.apollo.se/booking-guide/core/list?'


   parsed_url = urlparse(base_url)
   query_params = parse_qs(parsed_url.query)


    
    # Update query parameters
   query_params['departureAirportCode'] = departure
   query_params['bookingEngineCountryCode'] = get_code_for_destination(get_country_for_destination(destination) ,'apollo')
   query_params['bookingEngineDestinationCode'] = get_code_for_destination(destination ,'apollo')
   query_params['orderBy'] = 'Price'
   query_params['paxAges'] = paxAges
   query_params['searchProductCategoryCodes'] ="FlightAndHotel&searchProductCategoryCodes=Cruise"
   query_params['departureDate'] = date
   query_params['duration'] = duration
   query_params['searchType'] = 'Cached'
   if len(rooms) > 1:
    query_params['paxConfig'] = paxConfig

    
    # Construct the new query string
   new_query_string = urlencode(query_params, doseq=True)
 
    # Construct the new URL
   url = urlunparse(parsed_url._replace(query=new_query_string))

      
     
   def scrapeAp(url): 
     options = webdriver.ChromeOptions()
   #options.add_argument('--headless')  # Run in headless mode for performance

     prefs = {"profile.default_content_setting_values.notifications" : 2}
     options.add_argument("--disable-gpu")
     options.add_argument("--disable-extensions")
     options.add_argument("--disable-dev-shm-usage")
     options.add_argument("--no-sandbox")

# Disable loading images
     options.add_argument("--blink-settings=imagesEnabled=false")
     options.add_experimental_option("prefs",prefs)
     options.add_argument("--start-maximized")
     driver = webdriver.Chrome(options=options ,seleniumwire_options=seleniumwire_options,)
      
             
     driver.get(url)
     wait = WebDriverWait(driver, 10)
     time.sleep(1)  
     try: 
      deals = wait.until(EC.presence_of_all_elements_located((By.XPATH, "//div[@class='information-section']")))

      if deals:
            first_deal = deals[0]
            # Extracting deal details
            try:
              deal_location = first_deal.find_element(By.XPATH, ".//span[contains(@class, 'accommodation-location-text align-items-center')]").text.strip()
            except:     
              deal_location = first_deal.find_element(By.XPATH, ".//span[contains(@class, 'accommodation-location-text align-items-center')]").text.strip()

            deal_name = first_deal.find_element(By.XPATH, ".//div[contains(@class, 'accommodation-heading-component active')]").text.strip()
            flight_deal = first_deal.find_element(By.XPATH, ".//span[contains(@class, 'flight-information')]").text.strip()
            try: 
              deal_details = first_deal.find_element(By.XPATH, ".//div[contains(@class, 'accommodation-facts-component')]").text.strip()
            except:
              deal_details = first_deal.find_element(By.XPATH, ".//div[contains(@class, 'accommodation-item-information')]").text.strip()

            deal_price = first_deal.find_element(By.XPATH, ".//div[contains(@class, 'product-price')]").text.strip()
            deal_price_match = re.search(r'([\d\s.,]+):-', deal_price)
            
            if deal_price_match:
                deal_price_str = deal_price_match.group(1).replace('\u2009', '').replace(' ', '').strip()
                try:
                 deal_price_float = float(deal_price_str)
                 deal_price_float = float(f"{deal_price_float / 1000:.3f}") 
                 deal_price_float1=deal_price_float / sum(room['adults'] for room in rooms)
                 deal_price_formatted = f"{deal_price_float1} kr per person "
                except ValueError:
        # Handle the case where conversion to float fails
                  deal_price_formatted = "N/A"
                  deal_price_float = None
                
           
            # Constructing the deal object
            deal_object = {
                "deal_name": deal_name,
                "deal_price": deal_price_formatted,
                "deal_location": deal_location,
                "flight_deal": flight_deal,
                "deal_details": deal_details,
                "deal_image_url": '',
                "floatPrice":deal_price_float1 ,"url":url
                
            }
            driver.quit()
            return deal_object
     except: 
            driver.quit()
            return 
        
 
   deal= scrapeAp(url)
   if deal :
        return deal
   else:
      query_params['searchType'] = 'Uncached'
      new_query_string = urlencode(query_params, doseq=True)
      url = urlunparse(parsed_url._replace(query=new_query_string))
      deal=scrapeAp(url)
      return deal       
 
  
"""       
def scrape_detur(departure, destination, date, duration, rooms):
   options = webdriver.ChromeOptions()
   options.add_argument('--headless')  # Run in headless mode for performance

   prefs = {"profile.default_content_setting_values.notifications" : 2}
   options.add_experimental_option("prefs",prefs)
   #options.add_argument("--start-maximized")
   driver = webdriver.Chrome(options=options)

   def construct_rms(rooms):
    rms_list = []
    for room in rooms:
        adults = room['adults']
        num_children = room['children']
        if num_children > 0:
            children_str = '.'.join(['5'] * num_children)
        else:
            children_str = ''
        rms_list.append(f"{adults}.{num_children}.{children_str}")
    return '|'.join(rms_list)
    
   
   base_url = "https://detur.se/sv/find/flyg-hotell#&"


   parsed_url = urlparse(base_url)
   query_params = parse_qs(parsed_url.fragment)


    
    # Update query parameters
   query_params['cfr'] = departure
   query_params['ds'] = deturChck(departure ,destination)
  # query_params['d'] = get_code_for_destination(destination ,'apollo')
   query_params['df'] = date
   query_params['dt'] = date
   query_params['nf'] =duration
   query_params['nt'] = duration
   query_params['rms[]'] = construct_rms(rooms)
   query_params['cc[]'] = "0"


    
    # Construct the new query string
   new_fragment  = urlencode(query_params, doseq=True)
 
    # Construct the new URL
   url = urlunparse(parsed_url._replace(fragment=new_fragment))
   print(url)
   driver.get(url)
   wait = WebDriverWait(driver, 10)
   try:
    xpath = "//button[@class='ch2-btn ch2-allow-all-btn ch2-btn-primary ch2-btn-text-sm']"
    text_content = "Tillåt alla cookies"
    button = wait.until(EC.element_to_be_clickable((By.XPATH, f"{xpath}[contains(text(), '{text_content}')]"))) 
    button.click()   
    time.sleep(5)  
    deals = wait.until(EC.presence_of_all_elements_located((By.XPATH, "//div[@class='bg-light rounded overflow-hidden result async-package']")))

    if deals:
            first_deal = deals[0]
            # Extracting deal details
            deal_info = first_deal.find_element(By.XPATH, ".//div[contains(@class, 'col-md-5 p-3')]")
            
            url=deal_info.find_element(By.TAG_NAME , "a").get_attribute('href')
            
            deal_location = deal_info.find_element(By.XPATH, ".//div[contains(@class, 'font-weight-light')]").text.strip()
            deal_name = deal_info.find_element(By.TAG_NAME , "a").text.strip()
            flight_deal = deal_info.find_element(By.XPATH, ".//div[@class='mt-2']").text.strip()
            deal_details = first_deal.find_element(By.XPATH, ".//div[contains(@class, 'col-md-4 d-flex flex-wrap align-content-center p-3 mt-n4 mt-md-0')]").text.strip()
            deal_price = first_deal.find_element(By.XPATH, ".//div[contains(@class, 'w-100 text-center mb-3 mb-md-0')]").text.strip()
            deal_price_match = re.search(r'([\d\s.,]+)', deal_price)


            if deal_price_match:
                deal_price_str = deal_price_match.group(1).replace('\u2009', '').replace(' ', '').strip()
                try:
                 deal_price_float = float(deal_price_str)
                 deal_price_float = float(f"{deal_price_float / 1000:.3f}") 
                 deal_price_formatted = f"{deal_price_float} kr per person "
                except ValueError:
        # Handle the case where conversion to float fails
                  deal_price_formatted = "N/A"
                  deal_price_float = None
                
           
            # Constructing the deal object
            deal_object = {
                "deal_name": deal_name,
                "deal_price": deal_price_formatted,
                "deal_location": deal_location,
                "flight_deal": flight_deal,
                "deal_details": deal_details,
                "deal_image_url": '',
                "floatPrice":deal_price_float ,"url":url
                
            }
            driver.quit()
            return deal_object
   except: 
            driver.quit()
            return 
        
 """


def scrape_detur(departure, destination, date,till, duration, rooms):
   proxy = get_random_proxy()
   proxies_dict = {
        'http': proxy,
        'https': proxy,
    }
   
   base_url = 'https://aventura-se-online.goodwin-soft.com/api/public/package?'
   parsed_url = urlparse(base_url)
   query_params = parse_qs(parsed_url.query)     
   query_params['initial'] = "true"
   query_params['city_from_id'] = departure
   query_params['destination_id'] = deturChck(departure ,destination)
   query_params['date_from'] = date
   query_params['date_to'] = till   
   query_params['nights_from'] = duration
   query_params['nights_to'] = duration  
        # Flatten participants list into the query parameters
   for i, room_participants in enumerate(rooms):
    for key, value in room_participants.items():
        if key == 'children':
            key = 'kids'
        query_params[f'rooms[{i}][{key}]'] = value

   query_params['user_token'] = 'ut:ba435ee11a133d44b178e0db7f33f176'            
   query_params['current_request_key'] = '9HNia9aBB11721167205638'            

   new_query_string = urlencode(query_params, doseq=True)
   url = urlunparse(parsed_url._replace(query=new_query_string))               


   headers = {
        "Accept": "application/json",
        "Content-Type": "application/json",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3"
    }

   response = requests.get(url, headers=headers,proxies=proxies_dict)
   try:
       
    data=response.json()
    data=data["results"]
    first_key = next(iter(data))
    deal = data[first_key]
    deal_object = {
                "deal_name": deal["hotel_slug"],
                "deal_price":  str(deal["price"])  + "kr per person" ,
                "deal_location": deal["city_name"],
                "flight_deal": deal["date_from"] + "-" + deal["date_to"],
                "deal_details": deal["room_name"],
           
                "floatPrice":float(deal["price"] / 1000)  
                ,"url":"https://detur.se/sv/hotel/"+ deal["hotel_slug"]
                
            }
    return deal_object
   except:
       return
   
 
def scrape_tripx(departure, destination, date, duration, rooms):

   proxy = get_random_proxy()
   proxies_dict = {
        'http': proxy,
        'https': proxy,
    }

   app_rooms = []
   for room in rooms:
     api_room = {
        "numberOfAdults":int(room["adults"]) ,
        "numberOfChildren":int(room["children"]),
        "childrenAges": [4] * room["children"]  # Set age 4 for each child
    }
     app_rooms.append(api_room)
   url = "https://bkkbbi8sf9.execute-api.eu-west-1.amazonaws.com/prod/search?frontDomain=www.tripx.se&countryCode=se"
   code= get_code_for_destination(destination ,'tripx')
   return_date = calculate_return_date(date, duration)
   

   headers = {
    "Content-Type": "application/json"}
   body = {
   "origins":[departure],"destinations":[code],"dates":{"from":date,"to":return_date,"flexibleDates":False},"roomConfigurations":app_rooms,"affiliateId":"tripx"
}
   response = requests.post(url, headers=headers, data=json.dumps(body) ,proxies=proxies_dict)
   
   try:
       data=response.json()
       hotel=data["hotels"][0]
       result=data["results"][0]

       deal_object = {
                "deal_name": hotel["name"],
                "deal_price":  str(result["price"])  + "kr per person" ,
                "deal_location": hotel["location"]["country"] + "-" + hotel["location"]["city"] + "-" + hotel["location"]["destination"],
                "flight_deal": result["flightInfo"]["leaveDepartureTime"] + "-" + result["flightInfo"]["leaveAirportFromCode"],
                "deal_details":hotel["shortDescription"],
           
                "floatPrice":float(result["price"] / 1000)  
                ,"url":"https://www.norwegianholidays.com/se/c/" + hotel["hotelSlug"]
                
            }
       return deal_object
       
   except: 
            return  
        


def scrape_almena(departure, destination, date,till ,duration, rooms):
   proxy = get_random_proxy()
   proxies_dict = {
        'http': proxy,
        'https': proxy,
    }
    
   departureList=[{'ARL':'Arlanda'} ,{'BLL':'Billund'} , {'GOT':'Göteborg'} ,{'CPH':'Köpenhamn'} ]
   def get_departure_name(code, departure_list):
    for departure in departure_list:
        for name, departure_code in departure.items():
            
            if departure_code == code:
                return name
    return None
   
        
   base_url = 'https://www.almena.se/clientfiles/cm4/charterTourlistV5-ajax.asp?'
   parsed_url = urlparse(base_url)
   query_params = parse_qs(parsed_url.query)     
   query_params['type'] = "searchresult" 
   query_params['isFirstUserRequest'] = "True"
   query_params['offset'] = 0
   query_params['sort'] = 'Price'
        # Flatten participants list into the query parameters
   
   query_params['DepartureAirport[0]'] = departure            
   query_params['DepartureDate[0]'] = date
   query_params['DepartureDate[1]'] = till
   query_params['Destination[0]'] = destination
   query_params['Duration[0]'] = duration
   query_params['TransportType[0]'] = 'Flight'
  
   query_params['isFirstLoad'] = "True"
   
   
   new_query_string = urlencode(query_params, doseq=True)
 
    # Construct the new URL
   url = urlunparse(parsed_url._replace(query=new_query_string))               
        

   response = requests.get(url)
   try:
       data=response.json()
       data=data["results"]
       deal=data[0]
       print(deal)
       deal_object = {
                "deal_name": deal["name"],
                "deal_price":  str(deal["price"]["averagePrice"])  + "kr per person" ,
                "deal_location": deal["countryName"] + "-" + deal["cityName"],
                "flight_deal": deal["departureDateDetail"] + "-" + deal["arrivalDateDetail"],
                "deal_details": ",".join(deal["usps"]),
           
                "floatPrice":float(deal["price"]["averagePrice"] / 1000)  
                ,"url":"https://www.airtours.se/"+ deal["urlWithFilters"]
                
            }
       return deal_object
       
   except: 
            return 







def scrape_website(site, departure, destination, date, duration, rooms):
    
    if site == 'solresor':
       code =get_code_for_departure(departure,site)
       
       return [scrape_solresor(code, destination, date,date, duration, rooms)]
    elif site == 'norwegianholidays':
        code =get_code_for_departure(departure,site)
        
        return [scrape_norwegianholidays(code, destination, date, duration, rooms)]
    elif site == 'tripx':
        code =get_code_for_departure(departure,site)
        
        return [scrape_tripx(code, destination, date, duration, rooms)]    
    elif site == 'mixxtravel':
        code =get_code_for_departure(departure,site)
        
        return [scrape_mixxtravel(code, destination, date, duration, rooms)]    
    elif site == 'ving':
        code =get_code_for_departure(departure,site)
        deals= []
        deals.append(scrape_ving(code, destination, date, duration, rooms))
        deals.append(scrape_ving2(code, destination, date, duration, rooms , type="date"))
        return [get_cheapest_deal(deals)]

           
     
    elif site == 'tui':
        code =get_code_for_departure(departure,site)
        return [scrape_tui(code, destination, date, 0, duration, rooms , type="date")]  
    
    elif site == 'airtours':
        code =get_code_for_departure(departure,site)
        return [scrape_airtours(code, destination, date,date, duration, rooms)]
      
    elif site == 'sunweb':
        code =get_code_for_departure(departure,site)
        return [scrape_sunweb(code, destination, date, date,duration, rooms)]  
        
    elif site == 'apollo':
        code =get_code_for_departure(departure,site)
        return [scrape_apollo(code, destination, date, duration, rooms)]  
    elif site == 'detur':
        code =get_code_for_departure(departure,site)
        return [scrape_detur(code, destination, date,date, duration, rooms)]          
      

def get_all_deals(departure, destination, date, duration,rooms ):
    sites = get_sites_for_departure_and_destination(departure , destination)
    all_deals = []
    for site in sites:
        all_deals.extend(scrape_website(site, departure, destination, date, duration, rooms))
       
    return all_deals

def get_cheapest_deal(deals):
    # Fetch all deals
    
    
    # Ensure all_deals is a list
    if deals is None:
        return None
    all_deals = [deal for deal in deals if deal is not None]
    # Handle empty list case
    if not all_deals:
        return None

    # Find the cheapest deal
    cheapest_deal = min(all_deals, key=lambda x: x['floatPrice'])
    return cheapest_deal



def get_package_deal(departure, destination, date, duration , rooms):
    all_deals = get_all_deals(departure, destination, date, duration, rooms)
    cheapest_deal = get_cheapest_deal(all_deals)
    if not cheapest_deal:
        return None
  
    return {
        'price': cheapest_deal['deal_price'],'name':cheapest_deal['deal_name'],'location':cheapest_deal['deal_location'],'flight':cheapest_deal['flight_deal'],
        'details': cheapest_deal['deal_details'] ,'url': cheapest_deal['url'] , 'floatPrice':cheapest_deal['floatPrice']
    }





def get_package_deal_for_month(departure, destination, date, duration , rooms):
    all_deals = get_all_deals_for_month(departure, destination, date, duration, rooms)
    cheapest_deal = get_cheapest_deal(all_deals)
    if not cheapest_deal:
        return None
  
    return {
        'price': cheapest_deal['deal_price'],'name':cheapest_deal['deal_name'],'location':cheapest_deal['deal_location'],'flight':cheapest_deal['flight_deal'],
        'details': cheapest_deal['deal_details'] ,'url': cheapest_deal['url'] , 'floatPrice':cheapest_deal['floatPrice']
    }



def get_package_deal_for_flexible(departure, destination, date,days, duration , rooms):
    all_deals = get_all_deals_for_flexible(departure, destination, date,days, duration, rooms)
    cheapest_deal = get_cheapest_deal(all_deals)
    if not cheapest_deal:
        return None
  
    return {
        'price': cheapest_deal['deal_price'],'name':cheapest_deal['deal_name'],'location':cheapest_deal['deal_location'],'flight':cheapest_deal['flight_deal'],
        'details': cheapest_deal['deal_details'] ,'url': cheapest_deal['url'] , 'floatPrice':cheapest_deal['floatPrice']
    }





def get_all_deals_for_month(departure, destination, date, duration , rooms):
    sites = get_sites_for_departure_and_destination(departure , destination)
    all_deals = []
    for site in sites:
        all_deals.extend(scrape_website_month(site, departure, destination, date, duration, rooms))
       
    return all_deals
    
    
    
    
def get_all_deals_for_flexible(departure, destination, date,days, duration , rooms):
    sites = get_sites_for_departure_and_destination(departure , destination)
    print(sites)
    all_deals = []
    days=int(days)
    for site in sites:
        all_deals.extend(scrape_website_flexible(site, departure, destination, date,days, duration, rooms))
       
    return all_deals
    






def scrape_website_month(site, departure, destination, date, duration, rooms):
    parsed_date = datetime.strptime(date, "%Y-%m")
    month = parsed_date.month
    year = parsed_date.year
    _, num_days = calendar.monthrange(year, month)
    
    if site == 'solresor':
       code =get_code_for_departure(departure,site)
       
       deals=[]
       current_date = datetime(year, month, 1)
       date=current_date.strftime("%Y-%m-%d")
       current_date = datetime(year, month, num_days+1)
       till = current_date.strftime("%Y-%m-%d")
       deals.append(scrape_solresor(code, destination, date,till, duration, rooms))
           
       return [get_cheapest_deal(deals)]
   
   
    elif site == 'norwegianholidays':
        code =get_code_for_departure(departure,site)
        deals=[]
        for day in range(1, num_days + 1):
           current_date = datetime(year, month, day)
           date=current_date.strftime("%Y-%m-%d")
           deals.append(scrape_norwegianholidays(code, destination, date, duration, rooms))
           
        return [get_cheapest_deal(deals)]
    elif site == 'tripx':
        code =get_code_for_departure(departure,site)
        deals=[]
        for day in range(1, num_days + 1):
           current_date = datetime(year, month, day)
           date=current_date.strftime("%Y-%m-%d")
           deals.append(scrape_tripx(code, destination, date, duration, rooms))
           
        return [get_cheapest_deal(deals)]    
    elif site == 'mixxtravel':
        code =get_code_for_departure(departure,site)
        deals=[]
        for day in range(1, num_days + 1):
           current_date = datetime(year, month, day)
           date=current_date.strftime("%Y-%m-%d")
           deals.append(scrape_mixxtravel(code, destination, date, duration, rooms))
        return [get_cheapest_deal(deals)] 
    
    
    
    
    elif site == 'ving':
        code =get_code_for_departure(departure,site)
        deals= []
        for day in range(1, num_days + 1):
           current_date = datetime(year, month, day)
           date=current_date.strftime("%Y-%m-%d")
           deals.append(scrape_ving(code, destination, date, duration, rooms))
        deals.append(scrape_ving2(code, destination, parsed_date.strftime("%Y%m"), duration, rooms , type="month"))
        return [get_cheapest_deal(deals)]
    
         
     
    elif site == 'tui':
        code =get_code_for_departure(departure,site)
        deals=[]
        
        current_date = datetime(year, month, 15)
        date=current_date.strftime("%Y-%m-%d")
        deals.append(scrape_tui(code, destination, date ,num_days,duration, rooms ,type="month"))
        return [get_cheapest_deal(deals)]  


    
    elif site == 'airtours':
        code =get_code_for_departure(departure,site)
        deals=[]
        
        current_date = datetime(year, month, 1)
        date=current_date.strftime("%Y-%m-%d")
        current_date = datetime(year, month, num_days+1)
        till = current_date.strftime("%Y-%m-%d")
        deals.append(scrape_airtours(code, destination, date,till, duration, rooms))
        return [get_cheapest_deal(deals)]   
    
         
    elif site == 'sunweb':
        code =get_code_for_departure(departure,site)
        deals=[]
        
        current_date = datetime(year, month, 1)
        date=current_date.strftime("%Y-%m-%d")
        current_date = datetime(year, month, num_days+1)
        till = current_date.strftime("%Y-%m-%d")
        deals.append(scrape_sunweb(code, destination, date,till, duration, rooms))
        return [get_cheapest_deal(deals)]    

        
    elif site == 'apollo':
        code =get_code_for_departure(departure,site)
        deals=[]
        
        for day in range(1, num_days + 1):
           current_date = datetime(year, month, day)
           date=current_date.strftime("%Y-%m-%d")
           deals.append(scrape_apollo(code, destination, date, duration, rooms))
        return [get_cheapest_deal(deals)] 

    elif site == 'detur':
        code =get_code_for_departure(departure,site)
        deals=[]
        current_date = datetime(year, month, 1)
        date=current_date.strftime("%Y-%m-%d")
        current_date = datetime(year, month, num_days+1)
        till = current_date.strftime("%Y-%m-%d")
        deals.append(scrape_detur(code, destination, date, duration, rooms))
        return [get_cheapest_deal(deals)] 





def scrape_website_flexible(site, departure, destination, date,days, duration, rooms):
    parsed_date = datetime.strptime(date, "%Y-%m-%d")

    
    if site == 'solresor':
       code =get_code_for_departure(departure,site)
       
       deals=[]
     
       date=parsed_date - timedelta(days=int(days))
       till = parsed_date+ timedelta(days=int(days)) 
       deals.append(scrape_solresor(code, destination, date.strftime("%Y-%m-%d"),till.strftime("%Y-%m-%d"), duration, rooms))           
       return [get_cheapest_deal(deals)]
   
   
   
    elif site == 'norwegianholidays':
        code =get_code_for_departure(departure,site)
        deals=[]
        for day in range(- days, days + 1):
           date = parsed_date + timedelta(days=day)
           deals.append(scrape_norwegianholidays(code, destination, date.strftime("%Y-%m-%d"), duration, rooms))         
        return [get_cheapest_deal(deals)]
    elif site == 'tripx':
        code =get_code_for_departure(departure,site)
        deals=[]
        for day in range(- days, days + 1):
           date = parsed_date + timedelta(days=day)
           deals.append(scrape_tripx(code, destination, date.strftime("%Y-%m-%d"), duration, rooms))         
        return [get_cheapest_deal(deals)]  
    
    elif site == 'mixxtravel':
        code =get_code_for_departure(departure,site)
        deals=[]
        for day in range(- days, days + 1):
           date = parsed_date + timedelta(days=day)
           deals.append(scrape_mixxtravel(code, destination, date.strftime("%Y-%m-%d"), duration, rooms))
        return [get_cheapest_deal(deals)] 
          

    elif site == 'ving':
        code =get_code_for_departure(departure,site)
        deals= []
        for day in range(- days, days + 1):
           date = parsed_date + timedelta(days=day)
           deals.append(scrape_ving(code, destination,  date.strftime("%Y-%m-%d"), duration, rooms))
           deals.append(scrape_ving2(code, destination,  date.strftime("%Y-%m-%d"), duration, rooms , type="date"))
        return [get_cheapest_deal(deals)]
     
    elif site == 'tui':
        code =get_code_for_departure(departure,site)
        deals=[]
        
        deals.append(scrape_tui(code, destination, date,days, duration, rooms ,type="flexible"))
        return [get_cheapest_deal(deals)]  


    
    elif site == 'airtours':
        code =get_code_for_departure(departure,site)
        deals=[]    
        date=parsed_date - timedelta(days=int(days))
        till = parsed_date+ timedelta(days=int(days)) 
        deals.append(scrape_airtours(code, destination, date.strftime("%Y-%m-%d"),till.strftime("%Y-%m-%d"), duration, rooms))
        return [get_cheapest_deal(deals)]   
    
         
    elif site == 'sunweb':
        code =get_code_for_departure(departure,site)
        deals=[]
        
        date=parsed_date - timedelta(days=int(days))
        till = parsed_date+ timedelta(days=int(days)) 
        deals.append(scrape_sunweb(code, destination, date.strftime("%Y-%m-%d"),till.strftime("%Y-%m-%d"), duration, rooms))
        return [get_cheapest_deal(deals)]    

        
    elif site == 'apollo':
        code =get_code_for_departure(departure,site)
        deals=[]
        
        for day in range(- days, days + 1):
           date = parsed_date + timedelta(days=day)
           deals.append(scrape_apollo(code, destination, date.strftime("%Y-%m-%d"), duration, rooms))
        return [get_cheapest_deal(deals)] 

    elif site == 'detur':
        code =get_code_for_departure(departure,site)
        deals=[]
        
        date=parsed_date - timedelta(days=int(days))
        till = parsed_date+ timedelta(days=int(days)) 
        deals.append(scrape_detur(code, destination, date.strftime("%Y-%m-%d"), till.strftime("%Y-%m-%d"), duration, rooms))
        return [get_cheapest_deal(deals)] 







#print(get_package_deal('Kiruna', 'München', '2024-07-24', '14',[{'adults':2 , 'children':0}]))
print(scrape_website('mixxtravel','Göteborg','Antalya','2024-07-24','14',[{'adults':2 , 'children':0}])    )      

#scrape_website('ving','Stockholm','Clearwater Beach','2024-08-09','7',[{'adults':2 , 'children':0}])    

#print(scrape_website('mixxtravel','Köpenhamn','Antalya','2024-07-24','14',[{'adults':2 , 'children':0}])    )

#print(scrape_website('airtours','Göteborg','Alanya','2024-07-13','7',[{'adults':2 , 'children':0}]))     
#scrape_website('solresor','Göteborg','Alanya','2024-07-13','7',[{'adults':2 , 'children':0}])    

#scrape_website('detur','Köpenhamn','Rhodos Reguljär','2024-08-04','7',[{'adults':2 , 'children':0}])    

#get_package_deal_for_month('Köpenhamn','Rhodos Reguljär','2024-08','7',[{'adults':2 , 'children':0}])    

#print(scrape_website_month('detur','Köpenhamn','Rhodos Reguljär','2024-08','7',[{'adults':2 , 'children':0}]))

#print(scrape_website('tui','Stockholm','Samos','2024-08-18','7',[{'adults':2 , 'children':0}])    )

#print(scrape_website('apollo','Köpenhamn','Ayia Napa','2024-07-21','7',[{'adults':2 , 'children':0}])    )

#print(get_all_deals_for_flexible('Stockholm','Kap Verde','2024-09-20','8','7',[{'adults':2 , 'children':0}])    )



#print(scrape_website('ving','Stockholm','Ayia Napa','2024-07-19','7',[{'adults':2 , 'children':0}])    )


#scrape_solresor("CPH","Kos" ,'2024-07-12','7',[{'adults':2 , 'children':0}])
#print(scrape_solresor("CPH","Kos" ,'2024-07-12','7',[{'adults':2 , 'children':0}]))


#print(scrape_website('norwegianholidays','Stockholm','Hurghada','2024-10-30','7',[{'adults':2 , 'children':0}]))
#print(scrape_website('ving','Köpenhamn','Rom','2024-07-20','7',[{'adults':2 , 'children':1}])    )

#print(scrape_website('sunweb','Köpenhamn','Kreta','2024-07-18','7',[{'adults':2 , 'children':1}]) )


#print(scrape_website('tripx','Stockholm','Köpenhamn','2024-07-27','7',[{'adults':2 , 'children':0}]))

#print(get_package_deal_for_flexible("Stockholm", "Köpenhamn", "2024-09-20","4", "7" , [{'adults':2 , 'children':0}]))
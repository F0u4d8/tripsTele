import pandas as pd
from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from fuzzywuzzy import process
from messages import messages
import sqlite3



departures_df = pd.read_csv('departure.csv')
destinations_df = pd.read_csv('destinations.csv')
destinationsCode_df = pd.read_csv('destinationsCode.csv')


def suggest_closest_matches(user_input, choices):
    matches = process.extract(user_input, choices, limit=3)
    return matches

def get_destinations_for_departure(departure ,country):
    destinations = set()  # Use a set to store destinations
    filtered_df = destinations_df[(destinations_df['departure'] == departure) & (destinations_df['country'] == country)]
    
    for index, row in filtered_df.iterrows():
        if pd.notna(row['destinations']):
            destination_list = str(row['destinations']).split(',')
            for destination in destination_list:
                destinations.add(destination.strip())
    return list(destinations)

def getCountriesFotDepar(departure):
    return destinations_df[destinations_df['departure'] == departure]['country'].unique().tolist()



def create_duration_keyboard():
    durations = [7, 14, 21, 28]
    keyboard = [[InlineKeyboardButton(str(duration) + ' days', callback_data=str(duration))] for duration in durations]
    keyboard.append([InlineKeyboardButton("Type your own duration", callback_data='custom_duration')])
    return InlineKeyboardMarkup(keyboard)

"""
def create_room_selection_keyboard(adults, children,rooms):
    keyboard = [
        [InlineKeyboardButton("Adults: " + str(adults), callback_data='noop')],
        [InlineKeyboardButton("-", callback_data='decrease_adults'), InlineKeyboardButton("+", callback_data='increase_adults')],
        [InlineKeyboardButton("Children: " + str(children), callback_data='noop')],
        [InlineKeyboardButton("-", callback_data='decrease_children'), InlineKeyboardButton("+", callback_data='increase_children')],
        [InlineKeyboardButton("rooms: " + str(rooms), callback_data='noop')],
        [InlineKeyboardButton("-", callback_data='decrease_room'), InlineKeyboardButton("+", callback_data='increase_room')],
        [InlineKeyboardButton("Confirm", callback_data='confirm_room_selection')],
    ]
    return InlineKeyboardMarkup(keyboard)
"""




def get_sites_for_departure_and_destination(departure, destination):
    sites = []
    # Filter the destinations DataFrame based on the departure
    filtered_df = destinations_df[destinations_df['departure'] == departure]
    
    if not filtered_df.empty:
        for index, row in filtered_df.iterrows():
            # Split the destinations by both ', ' and ','
            destinations = row['destinations'].replace(', ', ',').split(',')
            
            # Check if the destination is in the list of destinations
            if destination in destinations:
                sites.append(row['site'])
    return sites


def get_code_for_departure(departure, site):
    # Filter the DataFrame based on both departure and site
    filtered_df = departures_df[(departures_df['departure'] == departure) & (departures_df['site'] == site)]
    
    # Extract the code
    if not filtered_df.empty:
        return filtered_df['code'].iloc[0]
    else:
        return None
    
    
    
    
def create_room_selection_keyboard(rooms , lang):
    keyboard = []
    for i, room in enumerate(rooms):
        keyboard.append([
            InlineKeyboardButton(text=messages[lang]['room'].format(num=i+1 ,adults=room['adults'] , Children=room['children']  )
                , callback_data=f'edit_room_{i}')
        ])
    keyboard.append([InlineKeyboardButton(text=messages[lang]['addR'], callback_data='add_room')])
    keyboard.append([InlineKeyboardButton(text=messages[lang]['Confirm'], callback_data='confirm_room_selection')])
    return InlineKeyboardMarkup(keyboard)

def create_individual_room_keyboard(room_index, room , lang):
    return InlineKeyboardMarkup([
        [InlineKeyboardButton(text=messages[lang]['IncreaseA'].format(adults=room['adults']), callback_data=f'increase_adults_{room_index}'),
         InlineKeyboardButton(text=messages[lang]['DecreaseA'].format(adults=room['adults']), callback_data=f'decrease_adults_{room_index}')],
        [InlineKeyboardButton(text=messages[lang]['IncreaseC'].format(Children=room['children']), callback_data=f'increase_children_{room_index}'),
         InlineKeyboardButton(text=messages[lang]['DecreaseC'].format(Children=room['children']), callback_data=f'decrease_children_{room_index}')],
        [InlineKeyboardButton(text=messages[lang]['back'], callback_data='back_to_room_selection')]
    ])    
    
    
    
def get_code_for_destination(destination, site):
    # Filter the DataFrame based on both departure and site
    filtered_df = destinationsCode_df[(destinationsCode_df['destination'] == destination) & (destinationsCode_df['site'] == site)]
    
    # Extract the code
    if not filtered_df.empty:
        return filtered_df['code'].iloc[0]
    else:
        return None


def get_country_for_destination( destination):
    # Read the CSV file into a DataFrame

    
    # Loop through each row to find the destination
    for index, row in destinations_df.iterrows():
        if pd.notna(row['destinations']) and destination in row['destinations']:
            return row['country']
    return None
        

def get_country_for_site_and_destination(site, destination):
    # Filter the destinations DataFrame based on the site and destination
    filtered_df = destinations_df[destinations_df['site'] == site ]
    
    if not filtered_df.empty:
        for index, row in filtered_df.iterrows():
            destinations = row['destinations'].split(',')
            if destination in destinations:
                return row['country']
    return None




def create_database():
    conn = sqlite3.connect('user_preferences.db')
    cursor = conn.cursor()

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS price_notifications (
            user_id INTEGER,
            departure TEXT,
            destination TEXT,
            date TEXT,
            duration INTEGER,
            price REAL,
            PRIMARY KEY (user_id, departure, destination, date, duration)
        )
    ''')
    conn.commit()
    conn.close()

create_database()



import json


def tuiCheck(id):
    with open('tui.json', 'r', encoding='utf-8') as file:
     data = json.load(file)
     for country in data:
         for resort in country['children']:
             if id == resort['id']:
                if resort['type'] == 'DESTINATION':
                     if resort ['children']:
                         for resss in resort ['children']:
                             if  id == resss['id']:
                                 if resss['type'] == 'RESORT':
                                      return id+'%3ARESORT'                             
                     return id+'%3ADESTINATION'
                else :
                  return id+'%3ARESORT'  
             
                 
                 
                 
def airToursChck(city):
    with open('airtours.json', 'r', encoding='utf-8') as file:
     data = json.load(file)
     city_code = None
     region_code = None
     country_code = None
    
     for item in data:
        if item['caption'].lower() == city.lower() and item['metadata'].startswith("Type:City"):
            city_code = item['value']
            parent_region_id = item['metadata'].split("ParentId:")[1].split(" ||")[0]
            
            # Find region
            for region in data:
                if region['value'] == parent_region_id and region['metadata'].startswith("Type:Region"):
                    region_code = region['value']
                    parent_country_id = region['metadata'].split("ParentId:")[1].split(" ||")[0]
                    
                    # Find country
                    for country in data:
                        if country['value'] == parent_country_id and country['metadata'].startswith("Type:Country"):
                            country_code = country['value']
                            break
                    break
            break

    return city_code, region_code, country_code
             

def sunwebCheck(city):
    with open('airtours.json', 'r', encoding='utf-8') as file:
     data = json.load(file)
     city_code = None
     region_code = None
     country_code = None
    
     for item in data:
        if item['caption'].lower() == city.lower() and item['metadata'].startswith("Type:City"):
            city_code = item['value']
            break
        elif  item['caption'].lower() == city.lower() and item['metadata'].startswith("Type:Region"):    
            region_code = item['value']
            break           
        elif item['caption'].lower() == city.lower() and item['metadata'].startswith("Type:Country"):
            country_code = item['value']
            break       


           

    return city_code, region_code, country_code

                                 
                                 
def deturChck(depar,city):
    with open('detur.json', 'r', encoding='utf-8') as file:
     data = json.load(file)
     for item in data:
        if item['departure_city'] == depar:         
            # Find region
            for cities in item['destinations']:
                if cities['destination'].lower() == city.lower():
                    return cities['code']
              
    
    return None     
    
    
def chunk_list(lst, n):
    """Helper function to divide a list into chunks of size n."""
    for i in range(0, len(lst), n):
        yield lst[i:i + n]
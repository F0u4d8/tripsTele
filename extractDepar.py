import json
import csv

# Load the JSON data
with open('data.json', 'r', encoding='utf-8') as file:
    data = json.load(file)

# Initialize the required variables
site = "apollo"
departure = "Växjö"
countries = {}
cities = {}

# Extract countries, regions, and cities
for entry in data:
    for country in entry['Countries']:
      countries[country['Code']] = {
            "name": country['Name'],

        }
      for areas in country['TravelAreas']:
        cities[areas['Code']] = {
            "name": areas['Name'],

        }
        try:
         if areas["TravelAreas"]:
          for are in areas["TravelAreas"]:
              cities[are['Code']] = {
            "name": are['Name']
        }
        except:
          continue
      
      
     
    

# Prepare the data for the CSV
csv_data = []
for country_id, country_info in countries.items():
    country_name = country_info["name"]
    csv_data.append([site, country_name, country_id])
for country_id, country_info in cities.items():
    country_name = country_info["name"]
    csv_data.append([site, country_name, country_id])

# Write to CSV
with open('output.csv', 'a', newline='', encoding='utf-8') as csvfile:
    csvwriter = csv.writer(csvfile)
    csvwriter.writerow(["site", "country", "cities"])
    csvwriter.writerows(csv_data)

print("CSV file has been written successfully.")

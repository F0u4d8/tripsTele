
import json
import csv

# Load the JSON data
file_path = 'data.json'
with open(file_path, 'r', encoding='utf-8') as file:
    data = json.load(file)



# Create a dictionary for mapping destination codes to countries and destinations
dest_map = {}
with open("dest.csv", mode='w', newline='', encoding='utf-8') as file:
 writer = csv.writer(file)
 writer.writerow(["site","dest","code"])
 for country in data["full"]:
    country_name = country["name"]
    for dest in country["destinations"]:
        writer.writerow(["tripx" ,dest["name"] ,dest["code"] ])
  
        


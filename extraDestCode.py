import json
import csv

# Read JSON data from a file
with open('data.json', 'r') as file:
    result = json.load(file)

# Specify the CSV file name
csv_file = "destinationsCode.csv"

# Open the CSV file for writing
with open(csv_file, mode='a', newline='') as file:
    writer = csv.writer(file)
    # Iterate through the result object to write the data rows
    for country in result:
        country_name = country["name"]
        country_id = country["itemId"]
        writer.writerow(["ving", country_name, country_id])
        
        for area_resort in country["areaResorts"]:
            if area_resort["isArea"]:
                writer.writerow(["ving", area_resort["name"], area_resort["itemId"]])
                for resort in area_resort["resorts"]:
                    writer.writerow(["ving", resort["name"], resort["itemId"]])
            else:
                writer.writerow(["ving", area_resort["name"], area_resort["itemId"]])

print(f"Data has been written to {csv_file}")

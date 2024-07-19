import json
import csv

# Load the JSON data
file_path = 'data.json'
with open(file_path, 'r', encoding='utf-8') as file:
    data = json.load(file)

# Initialize dictionaries to hold the hierarchical data



depar=['Göteborg-Landvetter','Jönköping','kalmar','Karlstad','Köpenhamn','Halmstad','Linköping','Luleå','Malmö','Norrköping','Skellefteå','Stockholm','Stockholm-Bromma','Stockholm-Nyköping Skavsta','Sundsvall','Umeå','Visby','Växjö','Åre/Östersund','Örebro']

# Function to convert JSON data to CSV
def json_to_csv(json_data, csv_filename):
    with open(csv_filename, mode='a', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        writer.writerow(["site", "destination", "code"])
        
        for country in json_data:
            
            if 'children' in country:
                for child in country['children']:
                    writer.writerow(["tui", child['name'], child['id']])

# Convert the JSON data to CSV
json_to_csv(data, 'dest.csv')

print("CSV file created successfully.")
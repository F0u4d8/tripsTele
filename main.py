import pandas as pd

def process_destinations(file_path):
    # Load the CSV file
    df = pd.read_csv(file_path)
    
    # Function to process each destination entry
    def process_entry(entry):
        # Remove spaces after commas
        entry = entry.replace(', ', ',')
        
        # Split by commas
        destinations = entry.split(',')
        
        # Add quotes if there's only one destination
        if len(destinations) == 1:
            return entry + ","
        
        return entry

    # Apply the processing function to the destinations column
    df['destinations'] = df['destinations'].apply(process_entry)
    
    return df

# Path to the CSV file
file_path = 'destinations.csv'

# Process the CSV file
processed_df = process_destinations(file_path)

# Write the processed DataFrame to a new CSV file
output_file_path = 'dest.csv'
processed_df.to_csv(output_file_path, index=False)

print(f"Processed CSV file saved to {output_file_path}")

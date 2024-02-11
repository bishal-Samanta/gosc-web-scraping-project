import json
import csv
import os


def json_to_csv(input_file, output_folder, output_filename):
    try:
        # Read the JSON file
        with open(input_file, 'r', encoding='utf-8') as json_file:
            data = json.load(json_file)

        # Create the output folder if it doesn't exist
        if not os.path.exists(output_folder):
            os.makedirs(output_folder)

        # Construct the output CSV file path
        output_csv_file = os.path.join(output_folder, output_filename)

        # Write the data to a CSV file
        with open(output_csv_file, 'w', newline='', encoding='utf-8') as csv_file:
            csv_writer = csv.writer(csv_file)

            # Write the header (assuming the JSON has a list of dictionaries with consistent keys)
            if data:
                header = data[0].keys()
                csv_writer.writerow(header)

                # Write the data rows
                for row in data:
                    csv_writer.writerow(row.values())

        return output_csv_file

    except Exception as e:
        return f"Error: {str(e)}"


# Example usage:
input_json_file = 'data-2023/project-data-2023.json'  
output_folder = 'sheets'  
output_filename = 'project-data-2023.csv' 

result = json_to_csv(input_json_file, output_folder, output_filename)
if result and not result.startswith("Error"):
    print(f"CSV file saved at: {result}")
else:
    print(result)

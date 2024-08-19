import pandas as pd
import json


csv_file = './bodmas_metadata.csv' 
df = pd.read_csv(csv_file)


df.drop(df.columns[1], axis=1, inplace=True)


json_file = '../malware_families_list.json' 
with open(json_file, 'r') as f:
    json_dict = json.load(f)
json_dict = {v: k for k, v in json_dict.items()}

def process_row(row):
    third_col_value = row.iloc[-1]
    if pd.isna(third_col_value):
        return None 
    else:
        return json_dict.get(third_col_value, None) 


df['third_column_processed'] = df.apply(process_row, axis=1)


df.dropna(subset=['third_column_processed'], inplace=True)


df.drop(df.columns[-2], axis=1, inplace=True)
df.rename(columns={'third_column_processed': df.columns[-2]}, inplace=True)

output_file = 'processed_file.csv' 
df.to_csv(output_file, index=False)

print(f"saved as {output_file}")

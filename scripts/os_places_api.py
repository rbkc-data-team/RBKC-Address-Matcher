from osdatahub import PlacesAPI, Extent,FeaturesAPI
from os import environ
import os
import geojson
import geopandas as gpd
import pandas as pd
import matplotlib.pyplot as plt
#%matplotlib inline
from dotenv import load_dotenv
import time

key = os.getenv("OS_KEY")
places = PlacesAPI(key) # No extent or product is given to PlacesAPI
crs = "EPSG:27700"

# define logic to bring in data

df['address'] = df['address_concat_r']+ " " + df['postcode_r']
address_list = df['address'].tolist()


# Define a list to hold the final results
matched_results = []

# Iterate through the first 20 addresses
for address in address_list[-50:]:

    if not isinstance(address, str) or (isinstance(address, float) and math.isnan(address)):
        # Skip or append None for this address, since it's invalid  
        matched_results.append({  
            'original_address': address,  
            'UPRN': None,  
            'ADDRESS': None,  
            'SUB_BUILDING_NAME': None,  
            'BUILDING_NUMBER': None,  
            'THOROUGHFARE_NAME': None,  
            'POST_TOWN': None,  
            'POSTCODE': None,  
            'MATCH': None,  
            'MATCH_DESCRIPTION': None  
        })  
        continue  # Skip API call and go to next address   
    # Call the OS Places API
    results = places.find(address, limit=6, logical_status_code=1, minmatch=0.7)
    
    # Create a GeoDataFrame from the features
    gdf = gpd.GeoDataFrame.from_features(
        results['features'],
        columns=["UPRN", "ADDRESS", 'SUB_BUILDING_NAME', 'BUILDING_NUMBER', 'THOROUGHFARE_NAME', 'POST_TOWN', 'POSTCODE', 'MATCH', 'MATCH_DESCRIPTION']
    )
    
    if not gdf.empty:
        # Select the row with the highest 'MATCH' score
        highest_match_row = gdf.loc[gdf['MATCH'].idxmax()]
        print("Match found, score is: ",highest_match_row['MATCH'])
        
        # Append a dictionary including the original address plus the highest match details
        matched_results.append({
            'original_address': address,  
            'UPRN': highest_match_row.get('UPRN'),  
            'ADDRESS': highest_match_row.get('ADDRESS'),  
            'SUB_BUILDING_NAME': highest_match_row.get('SUB_BUILDING_NAME'),  
            'BUILDING_NUMBER': highest_match_row.get('BUILDING_NUMBER'),  
            'THOROUGHFARE_NAME': highest_match_row.get('THOROUGHFARE_NAME'),  
            'POST_TOWN': highest_match_row.get('POST_TOWN'),  
            'POSTCODE': highest_match_row.get('POSTCODE'),  
            'MATCH': highest_match_row.get('MATCH'),  
            'MATCH_DESCRIPTION': highest_match_row.get('MATCH_DESCRIPTION')
        })
    else:
        # If no matches found, append with None for match fields
        print("No match found")
        matched_results.append({
            'original_address': address,
            'UPRN': None,
            'ADDRESS': None,
            'SUB_BUILDING_NAME': None,
            'BUILDING_NUMBER': None,
            'THOROUGHFARE_NAME': None,
            'POST_TOWN': None,
            'POSTCODE': None,
            'MATCH': None,
            'MATCH_DESCRIPTION': None
        })

    time.sleep(3)  # Wait 3 seconds before next API call 

# Convert list of dicts into a DataFrame
#print(matched_results)
matched_df = pd.DataFrame(matched_results)

matched_df.head()

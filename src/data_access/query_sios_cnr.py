import requests

MAPPING_ECV_VARIABLES = {'Pressure_average':['Pressure (surface)'],
                         'Wind_speed_average_at_33m':['Surface Wind Speed and direction'], 
                         'Wind_speed_average_at_10m':['Surface Wind Speed and direction'], 
                         'Wind_speed_average_at_5m':['Surface Wind Speed and direction'], 
                         'Wind_speed_average_at_2m':['Surface Wind Speed and direction'],
                         'Wind_direction_average_at_33m':['Surface Wind Speed and direction'], 
                         'Wind_direction_average_at_10m':['Surface Wind Speed and direction'], 
                         'Wind_direction_average_at_5m':['Surface Wind Speed and direction'], 
                         'Wind_direction_average_at_2m':['Surface Wind Speed and direction'],
                         'Temperature_average_at_33m':['Temperature (near surface)'], 
                         'Temperature_average_at_10m':['Temperature (near surface)'], 
                         'Temperature_average_at_5m':['Temperature (near surface)'], 
                         'Temperature_average_at_2m':['Temperature (near surface)'],
                         'Relative_humidity_average_at_33m':['Water Vapour (surface)'], 
                         'Relative_humidity_average_at_10m':['Water Vapour (surface)'], 
                         'Relative_humidity_average_at_5m':['Water Vapour (surface)'],
                         'Relative_humidity_average_at_2m':['Water Vapour (surface)'],
                         'Total_net_radiation_average_at_33m ':['Surface Radiation Budget'],
                         'GUV_O3':['Ozone'],
                         'Brewer_O3':['Ozone'],
                         'UV_RAD_O3':['Ozone'],
                         'M_124_O3':['Ozone']}

def get_iadc_datasets():
    datasets = []
    endpoint = 'https://data.iadc.cnr.it/erddap/search/advanced.json'
    query = endpoint + '?searchFor=ENVRI'
    response = requests.get(query, verify="sios_cnr_certificate_chain.pem")

    table = response.json()['table']
    index = table['columnNames'].index('Dataset ID') # Perché il JSON è formattato così
    for row in table['rows']:
      datasets.append(row[index])
    
    return(datasets)

def get_list_platforms():
  platforms = []
  
  datasets = get_iadc_datasets()
  for datasetID in datasets:
    query = f'https://data.iadc.cnr.it/erddap/info/{datasetID}/index.json'
    response = requests.get(query, verify="sios_cnr_certificate_chain.pem")

    table = response.json()['table']
    
    # Indexes for rows in json file
    variable_name = table['columnNames'].index('Variable Name') 
    attribute_name = table['columnNames'].index('Attribute Name') 
    value = table['columnNames'].index('Value') 

    # Dict variables
    short_name = None
    latitude = None
    longitude = None
    long_name = None
    platform_URI = None
    altitude = None

    for row in table['rows']:
      if row[variable_name] == 'NC_GLOBAL' and row[attribute_name] == 'ENVRI_platform_short_name':
        short_name = row[value]
        
      if row[variable_name] == 'NC_GLOBAL' and row[attribute_name] == 'ENVRI_platform_long_name':
        long_name = row[value]
      
      if row[variable_name] == 'NC_GLOBAL' and row[attribute_name] == 'geospatial_lat_max':
        latitude = row[value]
      
      if row[variable_name] == 'NC_GLOBAL' and row[attribute_name] == 'geospatial_lon_max':
        longitude = row[value]
      
      if row[variable_name] == 'NC_GLOBAL' and row[attribute_name] == 'ENVRI_platform_URI':
        platform_URI = row[value]

      platform = { 'short_name': short_name,
                  'latitude': latitude,
                  'longitude': longitude,
                  'long_name': long_name ,
                  'URI': platform_URI,
                  'ground_elevation': altitude }

    platforms.append(platform)

  return platforms

def get_list_variables():
  return MAPPING_ECV_VARIABLES

if __name__ == "__main__":
  print(get_list_platforms())

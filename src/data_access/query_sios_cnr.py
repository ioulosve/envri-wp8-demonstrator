import requests

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

if __name__ == "__main__":
  print(get_list_platforms())

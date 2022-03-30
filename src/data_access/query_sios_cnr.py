import requests


MAPPING_ECV_VARIABLES = {'air_pressure':['Pressure (surface)'],
                         'wind_speed':['Surface Wind Speed and direction'],
                         'wind_from_direction':['Surface Wind Speed and direction'], 
                         'air_temperature':['Temperature (near surface)'],
                         'relative_humidity':['Water Vapour (surface)'], 
                         'equivalent_thickness_at_stp_of_atmosphere_ozone_content':['Ozone']}

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
    metadata = get_metadata_from_dataset(datasetID)
    platform = { 'short_name': metadata['ENVRI_platform_short_name'],
                'latitude':  metadata['ENVRI_platform_long_name'],
                'longitude':  metadata['geospatial_lat_max'],
                'long_name':  metadata['geospatial_lon_max'],
                'URI':  metadata['ENVRI_platform_URI'],
                'ground_elevation':  None }

    platforms.append(platform)

  return platforms

def get_list_variables():
  return MAPPING_ECV_VARIABLES

def query_dataset(variables_list=[], temporal_extent=[None,None], spatial_extent=[None,None,None,None]):
  filtered_datasets = []
  reversed_var_map = get_reverse_var_map()
  endpoint = 'https://data.iadc.cnr.it/erddap/search/advanced.json'

  for var in variables_list:
    # extract ERDDAP variables
    ERDDAP_vars = reversed_var_map[var]
    for evar in ERDDAP_vars:
      query = endpoint + f'?searchFor=ENVRI&standard_name={evar}&minLon={spatial_extent[0]}&minLat={spatial_extent[1]}&maxLon={spatial_extent[2]}&maxLat={spatial_extent[3]}&minTime={temporal_extent[0]}&maxTime={temporal_extent[1]}'
      response = requests.get(query, verify="sios_cnr_certificate_chain.pem")

      table = response.json()['table']
      id = table['columnNames'].index('Dataset ID')
      tabledap = table['columnNames'].index('tabledap')
      for row in table['rows']:
        filtered_datasets.append({
          'title': row[id],
          'urls' : [{'url': row[tabledap] , 'type':'OPeNDAP URL'}, {'url': row[tabledap]+'.nc' , 'type':'NetCDF-3 Direct Download'}],
          'ecv_variables' : [var],
          'time_period': None,
          'platform_id': None
        })
        

# Reverse the ecv mapping, useful for queries on erddap
def get_reverse_var_map():
  ecv_reverse = {}
  for k,v in MAPPING_ECV_VARIABLES.items():
    keys = []
    for k1,v1 in MAPPING_ECV_VARIABLES.items():
      if v[0] == v1[0]:
        keys.append(k1)
        ecv_reverse[v[0]] = keys
  
  return ecv_reverse

def get_metadata_from_dataset(datasetID):
  query = f'https://data.iadc.cnr.it/erddap/info/{datasetID}/index.json'
  response = requests.get(query, verify="sios_cnr_certificate_chain.pem")

  table = response.json()['table']
    
  # Indexes for rows in json file
  variable_name = table['columnNames'].index('Variable Name') 
  attribute_name = table['columnNames'].index('Attribute Name') 
  value = table['columnNames'].index('Value')
  
  metadata = {}

  for row in table['rows']:
    if row[variable_name] == 'NC_GLOBAL':
      metadata[row[attribute_name]] = row[value]
    
  return metadata

if __name__ == "__main__":
  #print(get_list_platforms())
  #print(get_list_variables())
  #print(get_reverse_var_map())

  #print(get_metadata_from_dataset('cct_radiation_d2'))






  '''
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
'''
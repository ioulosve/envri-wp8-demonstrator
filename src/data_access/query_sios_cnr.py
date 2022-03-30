from urllib import request
import requests


MAPPING_ECV_VARIABLES = {'air_pressure':['Pressure (surface)'],
                         'wind_speed':['Surface Wind Speed and direction'],
                         'wind_from_direction':['Surface Wind Speed and direction'], 
                         'air_temperature':['Temperature (near surface)'],
                         'relative_humidity':['Water Vapour (surface)'], 
                         'equivalent_thickness_at_stp_of_atmosphere_ozone_content':['Ozone'],
                         'surface_net_downward_radiative_flux':['Surface Radiation Budget']}

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
  # This works but needs to be optimized
  datasets = []

  endpoint = 'https://data.iadc.cnr.it/erddap/search/advanced.json'
  query = endpoint + f'?searchFor=ENVRI&minLon={spatial_extent[0]}&minLat={spatial_extent[1]}&maxLon={spatial_extent[2]}&maxLat={spatial_extent[3]}&minTime={temporal_extent[0]}&maxTime={temporal_extent[1]}'
  response = requests.get(query, verify="sios_cnr_certificate_chain.pem")

  # No datasets for the query
  if response.status_code == 404:
    return datasets
    
  table = response.json()['table']
  id = table['columnNames'].index('Dataset ID')
  tabledap = table['columnNames'].index('tabledap')

  for row in table['rows']:
    metadata = get_metadata_from_dataset(row[id])
    standard_names = get_standard_names_from_dataset(row[id])

    ecvs = []
    for sn in standard_names:
      if sn in MAPPING_ECV_VARIABLES.keys():
        ecvs.extend(MAPPING_ECV_VARIABLES[sn])

    datasets.append({
      'title': metadata['title'],
      'urls' : [{'url': row[tabledap] , 'type':'opendap'}, {'url': row[tabledap]+'.nc' , 'type':'data_file'}],
      'ecv_variables' : list(dict.fromkeys(ecvs)),
      'time_period': [metadata['time_coverage_start'], metadata['time_coverage_end']],
      'platform_id': metadata['ENVRI_platform_short_name']
    })

  filtered_datasets = list(filter(lambda x : set(variables_list) & set(x['ecv_variables']), datasets))
  
  return filtered_datasets

### Utils ###        

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

def get_standard_names_from_dataset(datasetID):
  standard_names=[]
  query = f'https://data.iadc.cnr.it/erddap/info/{datasetID}/index.json'
  response = requests.get(query, verify="sios_cnr_certificate_chain.pem")

  table = response.json()['table']
    
  # Indexes for rows in json file
  attribute_name = table['columnNames'].index('Attribute Name') 
  value = table['columnNames'].index('Value')
  
  for row in table['rows']:
    if row[attribute_name] == 'standard_name':
      standard_names.append(row[value])
  
  # return list removing duplicates  
  return list(dict.fromkeys(standard_names))


if __name__ == "__main__":
  #print(get_list_platforms())
  #print(get_list_variables())
  #print(get_reverse_var_map())

  #print(get_metadata_from_dataset('cct_radiation_d2'))
  #print(get_standard_names_from_dataset('cct_radiation_d2'))
  print(query_dataset(['Pressure (surface)', 'Ozone'], ['2009-09-20T00:00:00Z','2021-09-20T00:00:00Z'], [-22, 37, 52, 88]))





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
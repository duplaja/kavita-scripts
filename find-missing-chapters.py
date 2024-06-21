import requests
import json
import argparse

########################################################
#
# Change These Settings, as desired.
#
########################################################

#Kavita ODPS url (requierd)

odps_url = 'https://example.com/api/opds/xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxc'

########################################################
#
# Stop changing here
#
########################################################

# Calculated from odps_url
base_url = odps_url.split('/api')[0]
api_key = odps_url.split('/opds/')[1]

def kauth():

  auth_url = base_url+'/api/Plugin/authenticate/?apiKey='+api_key+'&pluginName=Kavita_List'

  response = requests.post(auth_url)

  token = response.json()['token']

  return token

def myuserid(kavita_token):

  headers = {'Authorization': f'Bearer {kavita_token}'}

  myself_url = base_url+'/api/Users/myself'

  response = requests.get(myself_url, headers=headers)

  user_id = response.json()['id']

  return user_id

def librarySeriesInfo(library_id, kavita_token):

  headers = {
    'Authorization': f'Bearer {kavita_token}',
    'accept': "text/plain",
    'Content-Type': "application/json"
  }

  library_series_url = base_url+'/api/Series/all-v2/?PageNumber=1&PageSize=0'

  data = {
    "id": 0,
    "name": None,
    "statements": [
        {
            "comparison": 0,
            "field": 19,
            "value": str(library_id),
        }
    ],
    "combination": 0,
    "sortOptions": {
        "sortField": 1,
        "isAscending": True,
    },
    "limitTo": 0
  }

  response = requests.post(library_series_url, headers=headers, data=json.dumps(data))
  
  library_data = response.json()

  return library_data

def seriesVols(series_id, kavita_token):

  headers = {'Authorization': f'Bearer {kavita_token}'}

  series_vol_url = base_url+'/api/Series/volumes?seriesId='+str(+series_id)

  response = requests.get(series_vol_url, headers=headers)

  series_vols = response.json()

  return series_vols

def findMissingChapters(chapter_list):

  sorted_list = sorted(chapter_list, key=float)

  integers = [int(float(val)) for val in sorted_list if float(val).is_integer()]

  # Create the list of missing integers if there are at least two integers to form a range
  if integers:
    integers = sorted(set(integers))  # Sort and remove duplicates
    missing_integers = set(range(integers[0], integers[-1] + 1)) - set(integers)
  
  else:
    missing_integers = set()
  
  return missing_integers

def main():

  parser = argparse.ArgumentParser(description="Check Kavita Library for missing chapters")
  parser.add_argument("library_id", help="The Kavita Library ID to check")

  args = parser.parse_args()

  kavita_token = kauth()

  print('Missing Chapters: \n\n--------------------------\n')

  library_series = librarySeriesInfo(args.library_id, kavita_token)

  for series in library_series:

    series_id = series['id']
    series_name = series['name']

    series_vols = seriesVols(int(series_id),kavita_token)

    for volume in series_vols:

      chapters = volume['chapters']
      vol_chapter_numbers = []

      for chapter in chapters:

        chapter_number = chapter['number']
        vol_chapter_numbers.append(chapter_number)

      missing_chapters = findMissingChapters(vol_chapter_numbers)

      if len(missing_chapters) > 0:
        print(series_name)
        print(missing_chapters)
        print("\n")

if __name__ == "__main__":
    main()

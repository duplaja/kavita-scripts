import requests
import csv
import json
import datetime

########################################################
#
# Change These Settings, as desired.
#
########################################################

#Kavita ODPS url (requierd)

odps_url = 'https://example.com/api/opds/xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxx'

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


def seriesInfo(series_id, kavita_token):

  headers = {'Authorization': f'Bearer {kavita_token}'}

  series_url = base_url+'/api/Series/'+str(+series_id)+'/?seriesId='+str(series_id)

  response = requests.get(series_url, headers=headers)

  seriesinfo = response.json()

  return seriesinfo


def userstats(user_id, kavita_token):

  headers = {'Authorization': f'Bearer {kavita_token}'}

  stats_url = base_url+'/api/Stats/user/'+str(user_id)+'/read'

  response = requests.get(stats_url, headers=headers)

  stats = response.json()

  return stats

def userhistory(user_id, kavita_token):

  headers = {'Authorization': f'Bearer {kavita_token}'}

  history_url = base_url+'/api/Stats/user/reading-history/?userId='+str(user_id)

  response = requests.get(history_url, headers=headers)

  history = response.json()

  #print(history)

  history_dict = {}

  for item in history:
    series_name = item['seriesName']
    read_date = item['readDate']
    read_date_dt = datetime.datetime.strptime(read_date[:19], "%Y-%m-%dT%H:%M:%S")
    
    # Add the series to the dictionary if it's not already there, or if the read date is more recent
    if series_name not in history_dict or history_dict[series_name]['readDate'] < read_date_dt:
        if True: 
          history_dict[series_name] = {'readDate': read_date_dt, 'chapterNumber': item['chapterNumber'], 'seriesId': item['seriesId']}
  

  sorted_history_dict = {k: {'readDate': v['readDate'].strftime("%m/%d/%Y"), 'chapterNumber': v['chapterNumber'],  'seriesId': v['seriesId']} for k, v in sorted(history_dict.items(), key=lambda x: x[1]['readDate'], reverse=True)}

  return sorted_history_dict

def calculate_percentage(part, whole):
    return round((part / whole) * 100, 2)


def main():

  kavita_token = kauth()


  user_id = myuserid(kavita_token)

  #stats = userstats(user_id, kavita_token)
  
  history = userhistory(user_id, kavita_token)
  
  for key in history:

    item = history[key]

    series_id = item['seriesId']

    seriesinfo = seriesInfo(series_id, kavita_token)

    #print(seriesinfo)

    pagesRead = seriesinfo['pagesRead']
    pagesTotal = seriesinfo['pages']

    percentRead = calculate_percentage(pagesRead,pagesTotal)

    if str(item['chapterNumber']) != '-100000':
      disp_string = item['readDate'] +' - '+key+' ( '+str(percentRead)+"% "+' - Last Chapter Read: '+str(item['chapterNumber'])+' )'
    else:
      disp_string = item['readDate'] +' - '+key+' ( '+str(percentRead)+"% "+')'
    
    print(disp_string)
    


if __name__ == "__main__":
    main()

from lxml import html
from datetime import datetime, timedelta
import csv, os, requests, json

with open('config.json') as json_data_file:
    config = json.load(json_data_file)

LOGIN_URL = "https://mywingo.wingo.ch/eCare/users/sign_in"
URL = "https://mywingo.wingo.ch/eCare/de/ajax_load_cdr?user_type=wireless"
CSV_PATH = os.path.dirname(os.path.realpath(__file__)) + "/results"

class Entry:
  def __init__(self, rawItem):
    self.date = datetime.strptime(rawItem["start_date"], '%d.%m.%Y %H:%M:%S ')
    self.type = rawItem["type"].rstrip()
    self.isData = rawItem["is_data"]
    self.targetNumber = rawItem["target_number"]
    self.amount = rawItem["amount"]
    self.isPhone = False
    if isinstance(self.amount, str):
      self.amount = self.amount.replace("&#x27;", "")
      if ":" not in self.amount:
        self.amount = int(self.amount)
      else:
        self.isPhone = True

def main():
    print('Just started & this may take some time...')
    session_requests = requests.session()

    # Get login csrf token
    print('Get login authenticity token...')
    result = session_requests.get(LOGIN_URL)
    tree = html.fromstring(result.text)
    authenticity_token = list(set(tree.xpath("//input[@name='authenticity_token']/@value")))[0]

    # Create payload
    payload = {
        "user[id]": config['username'], 
        "user[password]": config['password'], 
        "authenticity_token": authenticity_token
    }

    # Perform login
    print('Perform login...')
    result = session_requests.post(LOGIN_URL, data = payload, headers = dict(referer = LOGIN_URL))
    
    data = []
    index = 0
    while(True):
      # Scrape url
      print('Get data...')
      result = session_requests.get(URL + "&index=" + str(index), headers = dict(referer = URL))
      
      # Create dict
      result = result.json()
    
      data.extend(result["data"])
      
      if result["status"] == "pending":
        index = result["index"]
      else:
        break
    
    print('All data fetched...')
    
    formattedData = [["datetime",
      "type_string",
      "amount",
      "targetNumber",
      "isData",
      "isPhone"]]
      
    dailyStat = {}
    monthlyStat = {}
    
    for item in data:
      entry = Entry(item)  
          
      formattedData.append([entry.date.strftime("%Y-%m-%d %H:%M:%S"),
        entry.type,
        entry.amount,
        entry.targetNumber,
        entry.isData,
        entry.isPhone])
      
      amount = entry.amount
      if isinstance(amount, str) and ":" in amount:
          amount = get_sec(amount)
      
      # make dict with all day-results
      if entry.date.strftime("%Y-%m-%d") not in dailyStat:
        dailyStat[entry.date.strftime("%Y-%m-%d")] = {}
      
      if entry.type in dailyStat[entry.date.strftime("%Y-%m-%d")]:
        dailyStat[entry.date.strftime("%Y-%m-%d")][entry.type] += amount
      else:
        dailyStat[entry.date.strftime("%Y-%m-%d")][entry.type] = amount
      
      # make dict with all month-results
      if entry.date.strftime("%Y-%m") not in monthlyStat:
        monthlyStat[entry.date.strftime("%Y-%m")] = {}
      
      if entry.type in monthlyStat[entry.date.strftime("%Y-%m")]:
        monthlyStat[entry.date.strftime("%Y-%m")][entry.type] += amount
      else:
        monthlyStat[entry.date.strftime("%Y-%m")][entry.type] = amount
        
    print('Datapoints: ' + str(len(formattedData)))
    print('Days: ' + str(len(dailyStat)))
    print('Months: ' + str(len(monthlyStat)))
    
    write_csv('output.csv', formattedData)
    
    output_stats('output_daily_stats', dailyStat)
    output_stats('output_monthly_stats', monthlyStat)


def output_stats(name, data):    
  keys = []
    
  for date_key in data:
    for key in data[date_key]:
      if key not in keys:
        keys.append(key) 

  elem = ["datetime"]
  elem.extend(keys)
    
  formattedData = [elem]
  
  for date_key in sorted(data, reverse=True):
    elem = [date_key]
    for key in keys:
      if key in data[date_key]:
        elem.append(data[date_key][key])
      else:
        elem.append(0)
    formattedData.append(elem)
  
  write_csv(name + '.csv', formattedData)
      

def write_csv(fileName, data):
  path = os.path.join(CSV_PATH, fileName)
  print('Writing to: ' + path)
  with open(path, 'w', newline="") as f:
    writer = csv.writer(f)
    writer.writerows(data)

def get_sec(time_str):
  h, m, s = time_str.split(':')
  return int(h) * 3600 + int(m) * 60 + int(s)

def get_hhmmss(time_sec):
  m, s = divmod(seconds, 60)
  h, m = divmod(m, 60)
  return "%02d:%02d:%02d" % (h, m, s)

if __name__ == '__main__':
  main()
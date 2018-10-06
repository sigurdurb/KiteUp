
# coding: utf-8

# In[1]:


import requests as r
import datetime as dt
import pandas as pd
import json
import os
try:
    from emailer import send_mail
except ModuleNotFoundError as e:
    print("Running without email")


# # KiteUp - Icelandic weather alert system for kitesurfers

# In[2]:



'''CONSTANTS
Weather Station Id's'''
REY = 1 # Reykjavík : Grótta
EYR = 1395 # Eyrarbakki : Ölfurárós
GEL = 1480 # Geldingarnes : Geldingarnes
STR = 1473 # Straumsvík : Skógtjörn, Grótta

'''
TIDE Station Id's
''' 
REY_TIDE = 23 # Reykjavík
TLH_TIDE = 25 # Þorlákshöfn

'''END OF CONTANTS'''


'''Configure your variables:
hour_range - Hour range, compared with <= and >=
wind_range - In m/s, <= and >=
min_rows - Minimum rows per day. Some forecasts only predict every 3 hours, Some every hour. compared with <= and >=
locations - Put in the stations you want to get updates about along with the directions you want to filter for
            Each weather station can have many kiteable locations you can check for, see STR(Straumsvík) station for example.
'''

# Time range
hour_range = ['09:00','20:00']
# Wind with m/s range that will be compared with <= and >=
# A 9 metre kite your wind range could be around [6,12] m/s
wind_range = [6,12]

# For rain filter, checks if it contains any of these in a string lowercase
do_not_want = ['rign','skúr'] # Leave empty if you want any kind of weather condition


check_days = 2 # How many days ahead to check, including today, highest is 5

include_directions = True # if to include the directions for the spots given below
min_rows = 2 # Setting min rows as 2 because some forecasts only predict for every 3 hours

# Spots:
# Stores directions
# Each spot also stores a Tide ID and Minimum tide height in meters for each spot. Empty list if not applicable.
# Try to come up with the best locations, directions and tides to look for. Tide height will be compared with >= row['Sjávarhæð [m]']
GROTTA = {'Grótta':[['N','NNA','NV','NNV','VNV','V','VSV','SV'],[REY_TIDE, 2]]}
SKOGTJ = {'Skógtjörn':[['S','SA','SSA','SV','SSV','VSV'],[]]}
GELNES = {'Geldingarnes':[['A','ASA','SSA','SA','V','VNV'],[REY_TIDE, 0]]}
OLFUS = {'Ölfusárlón':[['A','ASA','SSA','S','SA','SSV','VSV','VNV','V'],[TLH_TIDE, 1.5]]}


# Weather stations can have many spots
locations = {
                REY:[GROTTA],
                EYR:[OLFUS],
                GEL:[GELNES],
                STR:[SKOGTJ, 
                    GROTTA]
            }


# In[3]:


# WRITE YOUR CUSTOM SETTINGS TO A JSON FILE

my_settings = {
    'yourname': {
            'locations': locations,
            'hour_range': hour_range,
            'wind_range': wind_range,
            'do_not_want': do_not_want,
            'check_days': check_days,
            'include_directions': include_directions,
            'min_rows': min_rows,
            'email': 'siggibald4@gmail.com',
    }
}

with open("settings.json", 'w', encoding='latin-1') as f:
    json.dump(my_settings, f, ensure_ascii=False, indent=4, sort_keys=True) 


# In[4]:


class kiter:
    def __init__(self, attributes):
        if type(attributes) == str:
            attributes =  json.loads(attributes)
        for attribute, value in attributes.items():
            self.__setattr__(attribute, value)


# In[5]:


def query_weather_api(locations):
    base_url = "https://apis.is"
    path = "/weather/forecasts/is/?stations="
    station_text_format = "{}," * len(locations)
    stations = station_text_format.format(*locations.keys())
    res = r.get(url=base_url + path + stations)
    return res
    '''
    Response:
    results - listi af dict:
        id - Stöðvanúmer
        name - Nafn á stöð
        atime - tími hvenær spá er gefin út á forminu %Y-%m-%d %H:%M:%S
        forecast - list af dict: 
            ftime - tími á forminu %Y-%m-%d %H:%M:%S
            F - vindhraði, 
            D - vindstefnu'''


# In[6]:


def query_tides_api(location_id, day):
    # This function returns a dataframe about the tides 24 hours from starting daytime
    base_url = "http://www.vegagerdin.is"
    path = "/vs/StationsDetails.aspx"
    query_format = "?ID={}&Per=24&Dt={}&nohead=true".format(location_id, day.strftime("%Y%m%d%H%M"))
    df = pd.read_html(base_url + path + query_format, decimal=',', thousands='.')[0]
    return df

def clean_tides_df(df):
    df.columns = df.iloc[0,:].values
    df = df.iloc[1:,:].reset_index(drop=True) 
    df['Tími'] = pd.to_datetime(df['Tími'],format='%d.%m.%Y %H:%M') # example format we get from vegagerdin: '6.10.2018 19:00'
    df['Sjávarhæð [m]'] = pd.to_numeric(df['Sjávarhæð [m]'])
    df.rename(columns={'Tími':'ftime'}, inplace=True)
    return df


# In[7]:


def wind_filter(df, wind_range):
    return df[(df.F  >= wind_range[0]) & (df.F <= wind_range[1])]

def directions_filter(df, directions): # Checks the 'D' column (Direction)
    return df[df.D.isin(directions)]

def hour_range_filter(df, hour_range):
    return df.between_time(*hour_range)

def rain_filter(df, wcond): # Checks the 'W' column (Weather)
    if not wcond:
        return df
    for cw in wcond: # use ~ for to reverse the booleans because we do not want it to contain this weather description
        df = df[~df.W.str.lower().str.contains(cw)]
    return df

def tides_filter(df, min_height):
    return df[df['Sjávarhæð [m]'] >= min_height] # Returns only the rows for which the statement is true 
    


# In[30]:


def run_filters(df, k, direction_tide, day):
    df = wind_filter(df, k.wind_range)
    df = rain_filter(df, k.do_not_want)

    if not df.empty:
        if include_directions: # Wind directions
            df = directions_filter(df, direction_tide[0])
        # Query for the tides sea stations for day interval for the next 24hours
        if direction_tide[1]: # If the list is not empty, such as with Skógtjörn, We only go here where it is needed or we want to merge the datasets for display purposes
            df_tides = clean_tides_df(query_tides_api(direction_tide[1][0], day - pd.DateOffset(hour=0))) # Always reset the hour to 00:00, to get the next 24 hours
            df = pd.merge(left=df, right=df_tides, on='ftime', how='inner')
            df = tides_filter(df, direction_tide[1][1])
    return df
    
'''
day_check function:
Filters out if the forecast of the day has the right wind and kite–able directions
Parameters:
df – df containing weather for one day
location_id - weather station id '''
def day_check(df, k, location_id, link, utgafutimi, day):
    message = ""
    for spot in k.locations[str(location_id)]:
        clean_df = df.copy() # For all the spots we need a fresh copy from here
        for name, direction_tide in spot.items():
            df = run_filters(df, k, direction_tide, day)
            if df.shape[0] >= min_rows:
                df = df.reset_index(drop=True)
                message += "{}\n{}\nStart: {}\n{}\n".format(spot,link,df.loc[0,'ftime'],df.to_string(justify='justify-all', col_space=5))
                
            df = clean_df.copy()
    return message        
            


# In[31]:


def main(k):
    
    response_weather = query_weather_api(k.locations)
    vedur = response_weather.json()['results']
    alert = list()
    for i in range(len(vedur)):
        location_id = int(vedur[i]['id'])
        link = vedur[i]['link']
        
        utgafutimi = vedur[i]['atime']
        df = pd.DataFrame(vedur[i]['forecast'])
        df['ftime'] = df['ftime'].astype('datetime64[s]')
        df['F'] = df['F'].astype('float')
        
        # Set the index to a DateTimeIndex so we can filter by hour
        df.set_index(pd.DatetimeIndex(df['ftime']), inplace=True)
        df.index.names=['index']
        df = hour_range_filter(df, k.hour_range)
        
        # Get the first date
        day = df['ftime'].iloc[0]

        for i in range(0, check_days):
            df_day = df[df.ftime.dt.day == day.day]
            # Call day_check with a dataframe for each day
            message = day_check(df_day, k, location_id, link, utgafutimi, day)
            if message:
                message = "Spá gefin út: " + utgafutimi + '\n' + message
                alert.append(message)
            # Iterate to the next day
            day += pd.DateOffset(days=1)
    
    print("\n".join(alert))
    if alert:
        try:
            send_mail("\n".join(alert), k.email)
            print("Email/s sent")
        except NameError as e:
            print("Not sending email")


# In[32]:


if __name__ == '__main__':
    filename = "settings.json"
    if os.path.exists(filename):
        with open(filename, 'r', encoding='latin-1') as f:
            settings = json.load(f)
    for name,v in settings.items():
        k = kiter(v)
        # Run the program for every different kiter settings
        main(k)


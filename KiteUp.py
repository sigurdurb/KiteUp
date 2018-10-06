
# coding: utf-8

# In[48]:


import requests as r
import datetime as dt
import pandas as pd


# # KiteUp - Icelandic weather alert system for kitesurfers

# In[49]:



'''Constants
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


check_days = 3 # How many days ahead to check, including today, highest is 5

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


# In[50]:


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


# In[51]:


def query_tides_api(location_id, day):
    # This function returns a dataframe about the tides 24 hours from starting daytime
    base_url = "http://www.vegagerdin.is"
    path = "/vs/StationsDetails.aspx"
    query_format = "?ID={}&Per=24&Dt={}&nohead=true".format(location_id, day.strftime("%Y%m%d%H%M"))
    df = pd.read_html(base_url + path + query_format, decimal=',', thousands='.')[0]
    return df

def clean_tides_df(df):
    df.columns = df.iloc[0,:].values
    df = df.iloc[1:,:].reset_index(drop=True) #'6.10.2018 19:00'
    df['Tími'] = pd.to_datetime(df['Tími'],format='%d.%m.%Y %H:%M')
    df['Sjávarhæð [m]'] = pd.to_numeric(df['Sjávarhæð [m]'])
    df.rename(columns={'Tími':'ftime'}, inplace=True)
    return df


# In[52]:


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
    


# In[53]:



def run_filters(df, direction_tide, day):
    df = wind_filter(df, wind_range)
    df = rain_filter(df, do_not_want)

    if not df.empty:
        if include_directions:
            df = directions_filter(df, direction_tide[0])
        # If we get through all this we query for the tides sea stations for day variable
        if direction_tide[1]: # If the list is not empty, such as with Skógtjörn
            df_tides = clean_tides_df(query_tides_api(direction_tide[1][0], day - pd.DateOffset(hour=0))) # Always reset the hour to 00:00
            df = pd.merge(left=df, right=df_tides, on='ftime', how='inner')
            df = tides_filter(df, direction_tide[1][1])
    return df
    
'''
day_check function:
Filters out if the forecast of the day has the right wind and kite–able directions
Parameters:
df – df containing weather for one day
location_id - weather station id '''
def day_check(df, location_id, link, utgafutimi, day):
    for spot in locations[location_id]:
        clean_df = df.copy() # For all the spots we need a fresh copy from here
        for name, direction_tide in spot.items():
            df = run_filters(df, direction_tide, day)
            if df.shape[0] >= min_rows:
                print(spot)
                print("Spá gefin út: " + utgafutimi)
                print(link)
                print(df.head())
            df = clean_df.copy()
            
            
            
            


# In[54]:


def main():
    
    response_weather = query_weather_api(locations)
    vedur = response_weather.json()['results']
    
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
        df = hour_range_filter(df, hour_range)
        
        # Get the first date
        day = df['ftime'].iloc[0]

        for i in range(0, check_days):
            df_day = df[df.ftime.dt.day == day.day]
            # Call day_check with a dataframe for each day
            day_check(df_day, location_id, link, utgafutimi, day)
            # Iterate to the next day
            day += pd.DateOffset(days=1)


# In[55]:


if __name__ == '__main__':
    main()

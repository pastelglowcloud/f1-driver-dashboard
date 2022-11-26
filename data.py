
# import packages and create cache folder for F1 data

import fastf1
fastf1.Cache.enable_cache('cache')  
import pandas as pd
import numpy as np

seasons_wanted = [2022, 2021, 2020, 2019, 2018] # specify desired timeframe

# create race result dataframe
historical_races = pd.DataFrame(columns= 
    ['Year', 'GP', 'DriverNumber', 'BroadcastName','Abbreviation', 'TeamName', 
    'TeamColor', 'FirstName', 'LastName','FullName', 'Position', 'GridPosition', 
    'Q1','Q2','Q3','Time', 'Status', 'Points'])
for year in seasons_wanted:
    schedule = fastf1.get_event_schedule(year)
    gp_list = [i for i in schedule['EventName'] if 'Grand' in i]
    for gp in gp_list:
        session = fastf1.get_session(year, gp, 'Race')
        session.load()
        temp_df = session.results
        temp_df.insert(0,'Year','')
        temp_df.insert(1,'GP','')
        temp_df = temp_df.assign(Year=str(year))
        temp_df = temp_df.assign(GP=str(gp))
        historical_races = historical_races.append(temp_df, ignore_index=True)

# create event detail dataframe

all_events = pd.DataFrame(columns= 
    ['Year', 'RoundNumber', 'Country', 'Location', 'EventDate', 'EventName', 'EventFormat', 
    'Session1', 'Session1Date', 'Session2', 'Session2Date', 'Session3', 'Session3Date', 
    'Session4','Session4Date', 'Session5', 'Session5Date', 'F1ApiSupport'])
for year in seasons_wanted:
    schedule = fastf1.get_event_schedule(year=year)
    schedule.insert(0,'Year','')
    schedule = schedule.assign(Year=str(year))
    all_events = pd.concat([all_events, schedule])

# merge the two dataframes

race_df = pd.merge(
    historical_races, 
    all_events,  
    how='left', 
    left_on=['Year','GP'], 
    right_on = ['Year','EventName'])

# create data buckets

race_df['ResultType'] = np.where(race_df['Position']<= 3, 'Podium', 'Points')
race_df['ResultType'] = np.where(race_df['Points']!=0, race_df['ResultType'], 'NoPoints')
race_df['QualiStatus'] = "Q3"
race_df['QualiStatus'] = np.where(race_df['GridPosition'] >= 15, 'Q2', race_df['QualiStatus'])
race_df['QualiStatus'] = np.where(race_df['GridPosition'] >= 10, 'Q1', race_df['QualiStatus'])
race_df['QualiStatus'] = np.where(race_df['GridPosition'] == 1, 'Pole', race_df['QualiStatus'])
race_df['Counter'] = 1

race_df["EventDate"] = pd.to_datetime(race_df["EventDate"])
race_df["EventDate"] = race_df["EventDate"].dt.date 
race_df = race_df.sort_values(by=['EventDate']) 

race_df.to_csv('data/races.csv', index=False)

# race = 'Singapore Grand Prix'
# year = 2018
# session = fastf1.get_session(year, race, 'Race')
# session.load()
# session.date
# session.session_status
# session.laps
# session.get_driver('SAI')
# session.car_data
# session.race_control_messages

#! /usr/bin/python3

import urllib
import datetime
from bs4 import BeautifulSoup
import pandas as pd
from os import system as sys

def getDateRange():
    """getDateRange function requests user input for start and end dates and returns a list of datetime objects to be used
    as parameters for future scraping operations"""
    
    print('')
    print('')
    startDate = input("What is the start date? Ex. 2018-12-25      ").replace("-",",")
    print('')
    print('')
    endDate   = input("What is the end date? Ex. 2018-12-25        ").replace("-",",")
   
    startYear = int(startDate[:4])
    startMonth = int(startDate[5:7])
    startDay = int(startDate[8:])

    endYear = int(endDate[:4])
    endMonth = int(endDate[5:7])
    endDay = int(endDate[8:])

    start = datetime.date(startYear,startMonth,startDay)
    end = datetime.date(endYear,endMonth,endDay)

    dateRange = [start + datetime.timedelta(days=x) for x in range((end-start).days + 1)]

    return dateRange, start, end


def scrapeDay(date, city, state):
    """scrapeDay function receives datetime object for one day, parses date to strings, formats the appropriate url for scraping,
    scrapes data, generates a dataframe with appropriately formatted data, and returns the dataframe to the sunMoonData function
    for aggregation"""

    year = str(date.year)
    month = str(date.month)
    day = str(date.day)

    url = """http://aa.usno.navy.mil/rstt/onedaytable?ID=AA&year={0}&month={1}&day={2}&state={3}&place={4}""".format(year,month,day,state,city)

    with urllib.request.urlopen(url) as response:
        html = response.read()
    soup = BeautifulSoup(html, 'html.parser')
    df = pd.read_html(url)

    ###Find Date
    date = df[0][0][0]
    date = date[date.find(',') + 2 :]
    
    ###Find Begin civil twilight
    bct = df[1][1][1]

    ###Find Sunrise
    sr = df[1][1][2]

    ###Find Sunset
    ss = df[1][1][4]
    
    ###Find End civil twilight
    ect = df[1][1][5]
    
    ###Find Moon visibility
    moonLine = str(soup.find_all('p'))
    perPos = moonLine.find('%')
    i1 = perPos - 2
    i2 = perPos +1
    moon = moonLine[i1:i2]


    ###Make new dataframe
    data = {'Date':[date],
            'Begin_Civil_Twilight':[bct],
            'Sunrise':[sr],
            'Sunset':[ss],
            'End_Civil_Twilight':[ect],
            'Moon_Visibility':[moon]}
    df2 = pd.DataFrame(data)
    df2.set_index('Date', inplace=True)

    print('Collecting Data for ' + date)

    return df2

def cleanMoon(df):
    """cleanMoon function cleans data scraped from Naval Observatory website.  Cleaning is necessary because new, quarters,
    and full moons are annotated as such rather than a visibility percentage on the Naval Observatory website.  Function
    checks the preceeding entries to determine the appropriate data to be entered."""
    print('')
    print('')
    print('Cleaning up some funny business...')
    
    for i in range(len(df.index)):
        j = df.index[i]
        if df['Moon_Visibility'][j] == '00%':
            df['Moon_Visibility'][j] = '100%'
        if df['Moon_Visibility'][j] == '':
            if 10 > int(str(df['Moon_Visibility'][df.index[i-1]])[:-1]) >= 0:
                df['Moon_Visibility'][j] = '0%'
            elif 100 >= int(str(df['Moon_Visibility'][df.index[i-1]])[:-1]) >= 90:
                df['Moon_Visibility'][j] = '100%'
            elif 25 < int(str(df['Moon_Visibility'][df.index[i-1]])[:-1]) <  75:
                df['Moon_Visibility'][j] = '50%'



def sunMoonDate():
    """sunMoonDate function instantiates a dataframe, requests user input for city and output filename, calls getDateRange 
    function to get list of datetime objects for scraping operation, calls scrapeDay function to gather data from the Naval
    Observatory website, calls cleanMoon function to clean data, writes the .csv file to the local directory, and asks
    user if they want to view the file (default uses LibreOffice, update lines 157-159 to user preference"""
    sys('clear')

    df = pd.DataFrame()
    print('')
    print('')
    print('')
    fN = input('Desired filename of .csv?     ')
    print('')
    print('')
    print('')
    if fN[-4:] in ['.csv','.CSV','.Csv','.CSv']:
        fN = fN[:-4]

    city = input('What City?                    ')
    city = city.lower()
    city = city.replace(' ','+')
    print('')
    print('')
    print('')
    
    state = input('What State? (ex. NY)          ')
    state = state.upper()
        
    dateRange, s, e = getDateRange()

    print('')
    print('')
    print('Collecting Sun/Moon Data for ' + city.title() + ', ' + state + ' from ' + str(s.ctime())[4:].replace('00:00:00 ', '') + ' to ' + str(e.ctime())[4:].replace('00:00:00 ', ''))
    for i in dateRange:
        dfi = scrapeDay(i, city, state)
        df = df.append(dfi)

    cleanMoon(df)

    print('Saving file as ' + fN + '.csv')
    df.to_csv(fN + '.csv')

    print('')
    print('')
    print('')
    openfile = input('Open .csv in LibreOffice? (y/n)     ')
    if openfile == 'y' or openfile == 'Y':
        sys('localc --view ' +  fN + '.csv')
    sys('clear')

if __name__ == "__main__":
    sunMoonDate()




        

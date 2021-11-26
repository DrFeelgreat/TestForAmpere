from bs4 import BeautifulSoup
import requests
import csv

def removeParenthesis(str):
    return str.replace('(', '').replace(')', '')


def parseDocument():
    file = open('imdb_most_popular_movies_dump.html', encoding='utf-8') #opening html file
    parsedFile = BeautifulSoup(file, features="html.parser") #parsing html file
    tableRows = parsedFile.body.find('table', attrs={'class': 'chart'}).find('tbody').find_all('tr') #getting table from parsed html file

    titlesInfo = []

    for row in tableRows: #searching through all the rows in the table
        titleInfo = {} #creating empty dictionary to store title info
        titleColumn = row.find('td', attrs={'class': 'titleColumn'}) #getting titleColumn

        titleInfo['Poster'] = row.find('td', attrs={'class': 'posterColumn'}).find('img')['src'] #getting poster link
        titleInfo['Title'] = titleColumn.find('a').text #getting title
        #titleInfo['crew'] = titleColumn.find('a')['title'] #OMDb api returns broader info, but with a better structure, so I decided to skip this
        titleInfo['Year'] = int(removeParenthesis(titleColumn.find('span', attrs={'class': 'secondaryInfo'}).text)) #getting year
        titleInfo['Velocity'] = int(titleColumn.find('div', attrs={'class': 'velocity'}).find(text=True)) #getting velocity
        titleInfo['imdbID'] = row.find('td', attrs={'class': 'watchlistColumn'}) \
            .find('div', attrs={'class': 'wlb_ribbon'})['data-tconst'] #getting IMDb id


        try:
            titleInfo['imdbRating'] = float(row.find('td', attrs={'class': 'imdbRating'}).text) #trying to get imdbRating
        except:
            pass

        titlesInfo.append(titleInfo) #appending created dictionary to the list of titles info

    return titlesInfo


def updateInfoWithApi(titlesInfo, apikey):
    newTitlesInfo = []
    for titleInfo in titlesInfo: #searching through all the found titles
        id = titleInfo['imdbID'] #getting title id
        response = requests.get(f'http://www.omdbapi.com/?i={id}&apikey={apikey}').json() #sending request to the api and parsing json response

        if 'Error' in response.keys(): #adding info from html, if api has returned error
            newTitlesInfo.append(titleInfo)
            continue

        response.pop('Response', None) #removing response info from the dictionary
        response.update(titleInfo) #updating info from html with info from api
        ratings = response.pop('Ratings', None) #getting ratings list and removing it from the dictionary

        try:
            for rating in ratings:
                response[rating['Source']] = rating['Value'] #adding each rating to the dictionary as a separate value
        except:
            pass

        newTitlesInfo.append(response) #adding created disctionary to the result list

    return newTitlesInfo

def main():
    apikey = '471d2e5'

    titlesInfo = updateInfoWithApi(parseDocument(), apikey) #getting titles info

    keys = set([key for title in titlesInfo for key in title.keys()]) #getting all the distinct keys

    with open('Titles.csv', 'w', encoding='utf-8') as csvfile: #opening csv file
        writer = csv.DictWriter(csvfile, fieldnames=keys) #creating csv writer
        writer.writeheader() #writing header to the csv file
        writer.writerows(titlesInfo) #writing titles info to the csv file


if __name__ == '__main__':
    main()

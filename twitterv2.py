import os

import requests
import csv
import json
import datetime

class TwitterRecentSearch:
    bearer_token = os.environ.get("BEARER_TOKEN")
    search_url = "https://api.twitter.com/2/tweets/search/recent"
    author = None
    maximum = None
    pagination = 10
    startTime = None

    def __init__(self, author, maximum, days):
        self.author = author
        self.maximum = maximum
        previous_date = datetime.datetime.today() - datetime.timedelta(days=days)
        self.startTime = previous_date.strftime('%Y-%m-%dT%H:%M:%SZ')

    def queryBuilder(self, next_token= None):
        query_str = f'(from:{self.author} -is:retweet) OR #twitterdev'
        if next_token is not None:
            query_params = {'query': query_str, 'next_token':next_token}
        else:
            query_params = {'query': query_str}
        if self.startTime is not None:
            query_params['start_time'] = self.startTime
        query_params['user.fields'] = 'name'
        query_params['tweet.fields'] ='author_id,created_at'

        return query_params
    def bearer_oauth(self,r):
        """
        Method required by bearer token authentication.
        """
        r.headers["Authorization"] = f"Bearer {self.bearer_token}"
        r.headers["User-Agent"] = "v2RecentSearchPython"
        return r

    def connect_to_endpoint(self,url, params):
        response = requests.get(url, auth=self.bearer_oauth, params=params)
        print(response.status_code)
        if response.status_code != 200:
            raise Exception(response.status_code, response.text)
        return response.json()

    def fetchTweets(self):
        next_token = None
        data = []
        round = int (self.maximum/self.pagination)
        for i in range (0,round):
            query_params = self.queryBuilder(next_token)
            json_response = self.connect_to_endpoint(self.search_url, query_params)
            next_token = json_response['meta']['next_token']
            data.extend(json_response['data'])
        return data

    def writeCSV(self, csvFile, data):
        with open(csvFile, 'w', newline='') as csvfile:
            spamwriter = csv.writer(csvfile, delimiter=',',
                                    quotechar='"', quoting=csv.QUOTE_MINIMAL)
            spamwriter.writerow(['author_id','author_name','tweet_id','created_at','text'])
            for d in data:
                spamwriter.writerow([d['author_id'], self.author, d['id'], d['created_at'],  d['text']])
        csvfile.close()

if __name__ == "__main__":
    bbc = TwitterRecentSearch('BBCNews',60, 2)
    results = bbc.fetchTweets()
    print ('number of tweets : {}'.format(len(results)))
    print (json.dumps(results, indent=4, sort_keys=True))
    bbc.writeCSV('csvoutput.csv',results)



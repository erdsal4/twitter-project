from bs4 import BeautifulSoup
import requests
import sys
import json
from itertools import cycle


def get_proxies(proxy_url='https://free-proxy-list.net/'):
    
    """ Extract proxy from web site and create proxy pool
        Source: https://github.com/taspinar/twitterscraper/blob/master/twitterscraper/query.py
    """
    
    response = requests.get(proxy_url)
    soup = BeautifulSoup(response.text, 'lxml')
    table = soup.find('table',id='proxylisttable')
    list_tr = table.find_all('tr')
    list_td = [elem.find_all('td') for elem in list_tr]
    list_td = list(filter(None, list_td))
    list_ip = [elem[0].text for elem in list_td]
    list_ports = [elem[1].text for elem in list_td]
    list_proxies = [':'.join(elem) for elem in list(zip(list_ip, list_ports))]
    
    proxy_pool = cycle(list_proxies )
    
    return proxy_pool 


def get_this_page_tweets(soup, searched_tweet_ids=[]):

    #res = soup.find_all(string="Bu aramayla ilgili hiç sonuç çıkmadı.")
    
    replies = retweets = likes = tweet_count = 0
       
    tweets = soup.find_all('li', 'js-stream-item')
    
    for tweet in tweets:
        
        t_id = tweet["data-item-id"]
        
        if t_id not in searched_tweet_ids:
        
            replies += int(tweet.find(
                'span', 'ProfileTweet-action--reply u-hiddenVisually').find(
                'span', 'ProfileTweet-actionCount')['data-tweet-stat-count'] or '0')
            retweets += int(tweet.find(
                'span', 'ProfileTweet-action--retweet u-hiddenVisually').find(
                'span', 'ProfileTweet-actionCount')['data-tweet-stat-count'] or '0')
            likes += int(tweet.find(
                'span', 'ProfileTweet-action--favorite u-hiddenVisually').find(
                'span', 'ProfileTweet-actionCount')['data-tweet-stat-count'] or '0')
            #html = str(tweet.find('p', 'tweet-text')) or ""
            print(t_id,tweet_count,replies, retweets, likes )
            
            searched_tweet_ids.append(t_id)
    
    print("here", len(searched_tweet_ids))
    tweet_count = len(searched_tweet_ids)
    return searched_tweet_ids,tweet_count,replies, retweets, likes

def get_tweets_data(tweet_id, soup):
    
    proxy = next(proxy_pool)
    print('Parsing result for ',tweet_id,' proxy : ', proxy)
    searched_tweet_ids = []
    searched_tweet_ids, tweet_count, replies, retweets, likes = get_this_page_tweets(soup,searched_tweet_ids)
    if soup.find("li", {"class": "js-stream-item stream-item stream-item"}) is not None:
        next_pointer = soup.find_all("li", {"class": "js-stream-item stream-item stream-item"})[-1]["data-item-id"]
        query = "https://twitter.com/trt2tv/status/{}".format(tweet_id)
    
        while True:
            
            next_url = "https://twitter.com/i/search/timeline?f=tweets&vertical=%27%20\%20%27default&include_available_features=1&include_entities=1&%27%20\%20%27reset_error_state=false&src=typd&max_position={}&q={}&l=tr%27".format(next_pointer,query)
            next_response = None
            try:
                next_response = requests.get(next_url, headers = {'User-Agent': 'Mozilla/5.0'}, proxies={"http": proxy})
                    
                if next_response.status_code != 200:
                    print("Non success status code returned "+str(next_response.status_code))
                    pass
                else:
                    print('Response : ', next_response)
                    
            except Exception as e:
                # in case there is some issue with request. None encountered so far.
                print(e)
                return tweet_count, replies, retweets, likes
    
            tweets_data = next_response.text
            tweets_obj = json.loads(tweets_data)
            
            print("has more",tweets_obj["has_more_items"]," and min pos", tweets_obj["min_position"])
            
            if tweets_obj["has_more_items"] and tweets_obj["min_position"]:
                # using two checks here bcz in one case has_more_items was false but there were more items
                next_pointer = tweets_obj["min_position"]
                html = tweets_obj["items_html"]
                print("html,", html)
                soup = BeautifulSoup(html, 'lxml')
                searched_tweet_ids,tweet_count,replies1, retweets1, likes1 = get_this_page_tweets(soup,searched_tweet_ids)
                replies += replies1
                retweets += retweets1
                likes += likes1
            else:
                print("\nNo more tweets returned")
                break
    
    return tweet_count, replies, retweets, likes
 
proxy_pool = get_proxies(proxy_url='https://free-proxy-list.net/')
    
def start(tweet_id = None):
    url = 'https://twitter.com/search?q=https://twitter.com/trt2tv/status/'+tweet_id+'&src=typed_query'
    response = None
    
    # Crawl data of the quote tweets of one tweet. In case "get_tweets_data" somehow returns
    # 0 for all values, the embedded function "incase" tries again at most 
    # 25 times to find quote tweet data with a recursive call to itself.
    
    def incase(url,response,retry):
        
        try:
            response = requests.get(url, headers = {'User-Agent': 'Mozilla/5.0'}) #headers=header) 
        except Exception as e:
            print(repr(e))
            sys.exit(1)
        
        if response.status_code != 200:
            print("Non success status code returned "+str(response.status_code))
            sys.exit(1)
            
        soup = BeautifulSoup(response.text, 'lxml')
        
        if soup.find("div", {"class": "errorpage-topbar"}):
            print("\n\n Error: Invalid username.")
            sys.exit(1)
    
        #print('my_url', url)
        tweet_count,replies, retweets, likes = get_tweets_data(tweet_id, soup)
        
        # recursive call to function if there is no quote_tweets. It could be that 
        # there actually is no quote tweets, or more likely that something went wrong with
        # get_tweets_data function
        
        if tweet_count == 0 and retry > 0:
            return incase(url,response,retry-1)
        
        return tweet_count,replies, retweets, likes
    
    #print("%s" % tweet_id + " has ", tweet_count," quote tweets. The quote tweets have ", replies, " replies, ", retweets, " retweets and ", likes, "likes")
    
    return incase(url,response, 25)
    


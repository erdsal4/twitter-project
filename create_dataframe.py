#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Aug 27 11:37:03 2019

@author: macintosh
"""

import pandas as pd
from get_quote_dataframe import start
from twitter_get_usertimeline import get_tweets
import pygsheets

def create_dataframe(jsonfile):

    df = pd.read_json(jsonfile,  lines=True)
    print(df)
    return df

def edit_data_df(df,jsonfile):
    #create empty lists which will be used
    med_typ=[]
    med_url=[]
    twt_url=[]
    quote_tweets=[]

    #begin for loop on each tweet
    for index in df.index:

        #append tweet urls except that if it is a retweet append 'retweet'
        if type(df.loc[index, 'retweeted_status']) == dict:
            twt_url.append('retweet')
            print("here!!!!!!")

        else:
            twt_url.append('https://twitter.com/'+df.loc[index, 'user']['screen_name']+'/status/'+str(df.loc[index, 'id_str']))
            print("here2")
        #begin if structure of media attachments
        if type(df.loc[index, 'extended_entities']) == dict:

            #create a counter of media count and zero out previous tweet's media count
            a=0

            #create empty media dictionaries and zero out previous tweet's dictionaries
            med_urls_dic={}
            med_typs_dic={}

            #begin second for loop on each media element
            for media in df.loc[index, 'extended_entities']['media']:

                #record count:media_url and count:media_type pairs to appropriate dictionaries as key:value pairs
                med_urls_dic[a]=media['media_url_https']
                med_typs_dic[a]=media['type']

                #count each media element
                a=a+1

            #at the end of media loop for each tweet record created dictionaries to the lists
            med_url.append(med_urls_dic)
            med_typ.append(med_typs_dic)

        #if no media, append empty dictionaries to the lists of dictionaries
        else:
            med_typ.append({0:'-'})
            med_url.append({0:'-'})
        
        quote_dict = {} # Create dictionary for each tweet's quote tweet data
        tweet_count,replies, retweets, likes = start(str(df.loc[index, 'id'])) # call function to get the data.
        
        # Append the data to the dictionary, and append the dictionary to the tweet list.
        
        quote_dict["qt_totalcount"] = tweet_count 
        quote_dict["qt_totalreplies"] = replies
        quote_dict["qt_totalretweets"] = retweets
        quote_dict["qt_totallikes"] = likes
        quote_tweets.append(quote_dict)
            

    #create dataframes from each list and edit them accordingly
    typ_df=pd.DataFrame(med_typ)
    typ_df=typ_df.replace(float('nan'), '-')
    new_col_typ=[x+1 for x in list(typ_df.columns)]
    typ_df.columns=new_col_typ
    typ_df=typ_df.add_prefix('media').add_suffix(' type')
    
    turl_df=pd.DataFrame(twt_url)
    print(turl_df)
    turl_df.columns=['tweet_url']
    print(turl_df)
    
    murl_df=pd.DataFrame(med_url)
    murl_df=murl_df.replace(float('nan'), '-')
    new_col_url=[x+1 for x in list(murl_df.columns)]
    murl_df.columns=new_col_url
    murl_df=murl_df.add_prefix('media').add_suffix(' url')
    
    quote_df = pd.DataFrame(quote_tweets)
    quote_df=quote_df.replace(float('nan'), '-')
    
    #pull ready-to-use columns from mother dataframe
    new_df=df.filter(items=['full_text', 'created_at', 'favorite_count', 'retweet_count'])

    #merge all columns
    new_df=turl_df.join(new_df).join(typ_df).join(murl_df).join(quote_df)

    #reorder columns for UX
    new_df=new_df.reindex(columns=['tweet_url', 'full_text', 'created_at', "favorite_count",'retweet_count',"qt_totalcount","qt_totalreplies","qt_totalretweets","qt_totallikes", 'media1 type', 'media1 url', 'media2 type', 'media2 url', 'media3 type', 'media3 url', 'media4 type', 'media4 url'])
    new_df.to_json(r'denemedata.json')
    
    #get the last id in the entire tweet dataframe to use it as parameter for the next tweet mining.
    last_id = int(df.loc[0, 'id_str'])
    
    return new_df, last_id

def write_to_sheet(df):
    #authorization
    gc = pygsheets.authorize(service_file='TRT2tweets-c9a966f7d786.json')
    
    #open the google spreadsheet
    sh = gc.open('TRT2_tweets')
    
    #select the first sheet 
    wks = sh[0]
    
    #clear the sheet
    wks.clear(fields='*')
    
    #update the first sheet with df
    wks.set_dataframe(df,(1,1))

def edit_sheet(df):
    
    # add the new dataframe in the existing spreadsheet
    
    gc = pygsheets.authorize(service_file='TRT2tweets-c9a966f7d786.json')
    
    #open the google spreadsheet
    sh = gc.open('TRT2_tweets')
    
    #select the first sheet 
    wks = sh[0]
    
    list_rows = df.values.tolist() # take each row in the dataframe and make a list of rows.
    
    #append rows as table starting from the lef-uppermost corner.
    for row in list_rows:

        wks.append_table(row, start='B2', dimension='ROWS', overwrite=False)
    

def main(username):
    
    request_count = 1 #count mining requests to seperate between the json files of each request
    get_tweets(request_count,username) #call function from "twitter_get_usertimeline.py"
    jsonfile = "user_timeline_{}.json1".format(username+str(request_count))
    df = create_dataframe(jsonfile)
    #print(df)
    df,last_id = edit_data_df(df,jsonfile)
    #print(df)
    write_to_sheet(df)
    
    """loop structure to request new tweets in user timeline :
        request_count += 1
        get_tweets(username, last_id, request_count)
        jsonfile = "user_timeline_{}.json1".format(username+request_count)
        df = create_dataframe(jsonfile)
        last_id, df = edit_data_df(df,jsonfile)      
        edit_sheet(df)   """        

main("trt2tv")    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    


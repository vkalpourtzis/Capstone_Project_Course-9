#!/usr/bin/env python
# coding: utf-8

# # Capstone Project - The Battle of the Neighborhoods (Week 2)
# ### Applied Data Science Capstone by IBM/Coursera

# ## Table of contents
# * [Introduction: Business Problem](#introduction)
# * [Data](#data)
# * [Methodology](#methodology)
# * [Analysis](#analysis)
# * [Results and Discussion](#results)
# * [Conclusion](#conclusion)

# ## Introduction: Business Problem <a name="introduction"></a>

# This project's goal is to find an optimal kind of venue (increased probability of high demand) to be opened in the downtown of a capital city. More specifically, this report aims to people interested in opening a business in the center of 
#  **Athens, Greece**.
# 
# To maximize the chances of success data from centers of seven big cities will be compared to conclude, according to Athens' downtown data, **what is the recommended type of venue to open**. Instead of extensive globalization, there is a prospect that the downtown of Athens may miss something.
# 
# The data will be collected via foursquare API. To increase models odds for a satisfying result will be checked the **venues for all city centers**. Cities that will be explored are **Cape Town, Moscow, Paris, Rio De Janeriro, San Francisco, Seoul, Sydney**.

# ## Data <a name="data"></a>

# Following data sources will be needed to extract/generate the required information:
# * number of venues, their type and location in every downtown 
# * a venue being frequently tipped indicates that people are interested in the venue and would like to share their experience with all other users. So, we will use tips per category as feature for the final recommendation. Because Venue Tips is a premium endpoint (it is not free) we limit our search in 10 venues. 
# 
# The above data will be obtained by **Foursquare API**

# **To Explore venues**
# > `https://api.foursquare.com/v2/venues/`**explore**`?client_id=`**CLIENT_ID**`&client_secret=`**CLIENT_SECRET**`&ll=`**LATITUDE**`,`**LONGITUDE**`&v=`**VERSION**`&limit=`**LIMIT**

# ### City Centers
# 
# Let's first define the address for every capital city center.
# 
# * **Athens**: Ermou street, Athens, Greece
# * **Cape Town**: Cape Town City Centre, Cape Town, South Africa
# * **Moscow**: Red Square, Moscow, Russia
# * **Paris**: 1st arrondissement of Paris, Paris, France
# * **Rio de Janeiro**: Centro, Rio de Janeiro, Brasil
# * **San Francisco**: Union Square, San Francisco, CA, USA
# * **Seoul**: Gangnam, Seoul, South Korea
# * **Sydney**: Circular Quay, Sydney NSW, Australia

# ### Import necessary Libraries

# In[1]:


import requests # library to handle requests
import pandas as pd # library for data analsysis
import numpy as np # library to handle data in a vectorized manner
import random # library for random number generation

get_ipython().system('conda install -c conda-forge geopy --yes ')
from geopy.geocoders import Nominatim # module to convert an address into latitude and longitude values

# libraries for displaying images
from IPython.display import Image 
from IPython.core.display import HTML 
    
# tranforming json file into a pandas dataframe library
from pandas.io.json import json_normalize

get_ipython().system('conda install -c conda-forge folium=0.5.0 --yes')
import folium # plotting library

print('Folium installed')
print('Libraries imported.')


# ### Define Foursquare Credentials and Version

# In[2]:


CLIENT_ID = 'OKAJYH2AGQSQZB1NTE1YFEODZ1TGV3UN3N4XQGB5WQRXFFQV' # your Foursquare ID
CLIENT_SECRET = 'XRGKGGB4XWMJU0DRE2VPO2LJMQGTFV40NPL22XDJLTFBOFPG' # your Foursquare Secret
VERSION = '20200702'
LIMIT = 50
radius = 4500 # Radius from the center to create the downtown area
print('Your credentails:')
print('CLIENT_ID: ' + CLIENT_ID)
print('CLIENT_SECRET:' + CLIENT_SECRET)


# ### Converting every city's center address to its latitude and longitude coordinates.
# 
# In order to define an instance of the geocoder, we need to define a user_agent. We will name our agent <em>foursquare_agent</em>, as shown below.

# In[3]:


# function that extracts the category of the venue
def get_category_type(row):
    try:
        categories_list = row['categories']
    except:
        categories_list = row['venue.categories']
        
    if len(categories_list) == 0:
        return None
    else:
        return categories_list[0]['name']


# ### Rio de Janeiro, Brasil

# In[4]:


addr_Rio = 'Centro, Rio de Janeiro, Brasil'

geolocator = Nominatim(user_agent="foursquare_agent")
location = geolocator.geocode(addr_Rio)
latitude = location.latitude
longitude = location.longitude
print("Coordinates:", latitude, longitude)
print("Radius from city's center, to determine downtown area, is:", radius, "meters")


# Define a URL

# In[5]:


url = 'https://api.foursquare.com/v2/venues/explore?client_id={}&client_secret={}&ll={},{}&v={}&radius={}&limit={}'.format(CLIENT_ID, CLIENT_SECRET, latitude, longitude, VERSION, radius, LIMIT)
url


# Send GET request and examine results

# In[6]:


results = requests.get(url).json()
'There are {} venues in a radius of {} m from the downtown`s center. '.format(len(results['response']['groups'][0]['items']), radius)


# Get relevant part of JSON

# In[7]:


items = results['response']['groups'][0]['items']


# Process JSON and convert it to a clean dataframe

# In[8]:


dataframe = json_normalize(items) # flatten JSON
dataframe.head(5)


# In[9]:


# filter columns
filtered_columns = ['venue.name', 'venue.categories'] + [col for col in dataframe.columns if col.startswith('venue.location.')] + ['venue.id']
dataframe_filtered = dataframe.loc[:, filtered_columns]

# filter the category for each row
dataframe_filtered['venue.categories'] = dataframe_filtered.apply(get_category_type, axis=1)

# clean columns
dataframe_filtered.columns = [col.split('.')[-1] for col in dataframe_filtered.columns]

dataframe_filtered.head(5)


# In[10]:


rio_ven = dataframe_filtered['categories'].value_counts()
rio_ven


# Let's create a dataframe that will contain the type of venues for every city

# In[11]:


ven_types = pd.DataFrame(rio_ven)
ven_types.columns = ['Rio']
ven_types.index.name = 'Venue Type'
ven_types


# Let's create a dataframe with the number of TIPS from Rio.

# In[12]:


cat_tips1 = pd.DataFrame()

for row in dataframe_filtered.index.values.tolist()[0:7]: # Limit to 7 venues because venue tips is a premium endpoint
    venue_id = dataframe_filtered.loc[row, 'id']
    url = 'https://api.foursquare.com/v2/venues/{}?client_id={}&client_secret={}&v={}'.format(venue_id, CLIENT_ID, CLIENT_SECRET, VERSION)
    
    # Send GET request for result
    result = requests.get(url).json()
    
    # Get the number of TIPS
    cat_tips1.loc[row, 'Tips'] = result['response']['venue']['tips']['count']
    cat_tips1.loc[row, 'Category'] = venue_id = dataframe_filtered.loc[row, 'categories']


# In[13]:


cat_tips1


# ### Seoul, South Korea

# In[14]:


addr_Seoul = 'Gangnam, Seoul, South Korea'

geolocator = Nominatim(user_agent="foursquare_agent")
location = geolocator.geocode(addr_Seoul)
latitude = location.latitude
longitude = location.longitude
print("Coordinates:", latitude, longitude)
print("Radius from city's center, to determine downtown area, is:", radius, "meters")


# Define a URL

# In[15]:


url = 'https://api.foursquare.com/v2/venues/explore?client_id={}&client_secret={}&ll={},{}&v={}&radius={}&limit={}'.format(CLIENT_ID, CLIENT_SECRET, latitude, longitude, VERSION, radius, LIMIT)
url


# Send GET request and examine results

# In[16]:


results = requests.get(url).json()
'There are {} venues in a radius of {} m from the downtown`s center. '.format(len(results['response']['groups'][0]['items']), radius)


# Get relevant part of JSON

# In[17]:


items = results['response']['groups'][0]['items']


# Process JSON and convert it to a clean dataframe

# In[18]:


dataframe = json_normalize(items) # flatten JSON
dataframe.head(5)


# In[19]:


# filter columns
filtered_columns = ['venue.name', 'venue.categories'] + [col for col in dataframe.columns if col.startswith('venue.location.')] + ['venue.id']
dataframe_filtered = dataframe.loc[:, filtered_columns]

# filter the category for each row
dataframe_filtered['venue.categories'] = dataframe_filtered.apply(get_category_type, axis=1)

# clean columns
dataframe_filtered.columns = [col.split('.')[-1] for col in dataframe_filtered.columns]

dataframe_filtered.head(5)


# Let's check Seoul's number of different type of venues.

# In[20]:


seoul_ven = dataframe_filtered['categories'].value_counts()
seoul_ven


# In[21]:


seoul_ven = pd.DataFrame(seoul_ven)
seoul_ven.columns = ['Seoul']
seoul_ven.index.name = 'Venue Type'

# Add them to the ven_types dataframe
ven_types = pd.merge(left=seoul_ven, right=ven_types, how='outer', left_on='Venue Type', right_on='Venue Type')


# In[115]:


ven_types


# Let's create a dataframe with the number of TIPS from Seoul.

# In[22]:


cat_tips2 = pd.DataFrame()

for row in dataframe_filtered.index.values.tolist()[0:7]: # Limit to 7 venues because venue tips is a premium endpoint
    venue_id = dataframe_filtered.loc[row, 'id']
    url = 'https://api.foursquare.com/v2/venues/{}?client_id={}&client_secret={}&v={}'.format(venue_id, CLIENT_ID, CLIENT_SECRET, VERSION)
    
    # Send GET request for result
    result = requests.get(url).json()
    
    # Get the number of TIPS
    cat_tips2.loc[row, 'Tips'] = result['response']['venue']['tips']['count']
    cat_tips2.loc[row, 'Category'] = venue_id = dataframe_filtered.loc[row, 'categories']


# In[23]:


cat_tips2


# ### San Francisco

# In[24]:


addr_SanFrancisco= 'Union Square, San Francisco, CA, USA'

geolocator = Nominatim(user_agent="foursquare_agent")
location = geolocator.geocode(addr_SanFrancisco)
latitude = location.latitude
longitude = location.longitude
print("Coordinates:", latitude, longitude)
print("Radius from city's center, to determine downtown area, is:", radius, "meters")


# Define a URL

# In[25]:


url = 'https://api.foursquare.com/v2/venues/explore?client_id={}&client_secret={}&ll={},{}&v={}&radius={}&limit={}'.format(CLIENT_ID, CLIENT_SECRET, latitude, longitude, VERSION, radius, LIMIT)
url


# Send GET request and examine results

# In[26]:


results = requests.get(url).json()
'There are {} venues in a radius of {} m from the downtown`s center. '.format(len(results['response']['groups'][0]['items']), radius)


# Get relevant part of JSON

# In[27]:


items = results['response']['groups'][0]['items']


# Process JSON and convert it to a clean dataframe

# In[28]:


dataframe = json_normalize(items) # flatten JSON
dataframe.head(5)


# In[29]:


# filter columns
filtered_columns = ['venue.name', 'venue.categories'] + [col for col in dataframe.columns if col.startswith('venue.location.')] + ['venue.id']
dataframe_filtered = dataframe.loc[:, filtered_columns]

# filter the category for each row
dataframe_filtered['venue.categories'] = dataframe_filtered.apply(get_category_type, axis=1)

# clean columns
dataframe_filtered.columns = [col.split('.')[-1] for col in dataframe_filtered.columns]

dataframe_filtered.head(5)


# Let's check San Fransisco's number of different type of venues. 

# In[30]:


san_francisco_ven = pd.DataFrame(dataframe_filtered['categories'].value_counts())
san_francisco_ven.columns = ['San Francisco']
san_francisco_ven.index.name = 'Venue Type'

# Add them to the ven_types dataframe
ven_types = pd.merge(left=san_francisco_ven, right=ven_types, how='outer', left_on='Venue Type', right_on='Venue Type')


# In[34]:


ven_types.head()


# Let's create a dataframe with the number of TIPS from San Francisco.

# In[35]:


cat_tips3 = pd.DataFrame()

for row in dataframe_filtered.index.values.tolist()[0:7]: # Limit to 7 venues because venue tips is a premium endpoint
    venue_id = dataframe_filtered.loc[row, 'id']
    url = 'https://api.foursquare.com/v2/venues/{}?client_id={}&client_secret={}&v={}'.format(venue_id, CLIENT_ID, CLIENT_SECRET, VERSION)
    
    # Send GET request for result
    result = requests.get(url).json()
    
    # Get the number of TIPS
    cat_tips3.loc[row, 'Tips'] = result['response']['venue']['tips']['count']
    cat_tips3.loc[row, 'Category'] = venue_id = dataframe_filtered.loc[row, 'categories']


# In[36]:


cat_tips3


# ### Sydney, Australia

# In[37]:


addr_Sydney= 'Circular Quay, Sydney NSW, Australia'

geolocator = Nominatim(user_agent="foursquare_agent")
location = geolocator.geocode(addr_Sydney)
latitude = location.latitude
longitude = location.longitude
print("Coordinates:", latitude, longitude)
print("Radius from city's center, to determine downtown area, is:", radius, "meters")


# Define a URL

# In[38]:


url = 'https://api.foursquare.com/v2/venues/explore?client_id={}&client_secret={}&ll={},{}&v={}&radius={}&limit={}'.format(CLIENT_ID, CLIENT_SECRET, latitude, longitude, VERSION, radius, LIMIT)
url


# Send GET request and examine results

# In[39]:


results = requests.get(url).json()
'There are {} venues in a radius of {} m from the downtown`s center. '.format(len(results['response']['groups'][0]['items']), radius)


# Get relevant part of JSON

# In[40]:


items = results['response']['groups'][0]['items']


# Process JSON and convert it to a clean dataframe

# In[41]:


dataframe = json_normalize(items) # flatten JSON
dataframe.head(5)


# In[42]:


# filter columns
filtered_columns = ['venue.name', 'venue.categories'] + [col for col in dataframe.columns if col.startswith('venue.location.')] + ['venue.id']
dataframe_filtered = dataframe.loc[:, filtered_columns]

# filter the category for each row
dataframe_filtered['venue.categories'] = dataframe_filtered.apply(get_category_type, axis=1)

# clean columns
dataframe_filtered.columns = [col.split('.')[-1] for col in dataframe_filtered.columns]

dataframe_filtered.head(5)


# Let's check Sydney's number of different type of venues.

# In[43]:


sydeny_ven = pd.DataFrame(dataframe_filtered['categories'].value_counts())
sydeny_ven.columns = ['Sydney']
sydeny_ven.index.name = 'Venue Type'

# Add them to the ven_types dataframe
ven_types = pd.merge(left=sydeny_ven, right=ven_types, how='outer', left_on='Venue Type', right_on='Venue Type')


# In[44]:


ven_types


# Let's create a dataframe with the number of TIPS from Sydney.

# In[45]:


cat_tips4 = pd.DataFrame()

for row in dataframe_filtered.index.values.tolist()[0:7]: # Limit to 7 venues because venue tips is a premium endpoint
    venue_id = dataframe_filtered.loc[row, 'id']
    url = 'https://api.foursquare.com/v2/venues/{}?client_id={}&client_secret={}&v={}'.format(venue_id, CLIENT_ID, CLIENT_SECRET, VERSION)
    
    # Send GET request for result
    result = requests.get(url).json()
    
    # Get the number of TIPS
    cat_tips4.loc[row, 'Tips'] = result['response']['venue']['tips']['count']
    cat_tips4.loc[row, 'Category'] = venue_id = dataframe_filtered.loc[row, 'categories']


# In[46]:


cat_tips4


# ### Moscow, Russia

# In[47]:


addr_Moscow = 'Red Square, Moscow, Russia'

geolocator = Nominatim(user_agent="foursquare_agent")
location = geolocator.geocode(addr_Moscow)
latitude = location.latitude
longitude = location.longitude
print("Coordinates:", latitude, longitude)
print("Radius from city's center, to determine downtown area, is:", radius, "meters")


# Define a URL

# In[48]:


url = 'https://api.foursquare.com/v2/venues/explore?client_id={}&client_secret={}&ll={},{}&v={}&radius={}&limit={}'.format(CLIENT_ID, CLIENT_SECRET, latitude, longitude, VERSION, radius, LIMIT)
url


# Send GET request and examine results

# In[49]:


results = requests.get(url).json()
'There are {} venues in a radius of {} m from the downtown`s center. '.format(len(results['response']['groups'][0]['items']), radius)


# Get relevant part of JSON

# In[50]:


items = results['response']['groups'][0]['items']


# Process JSON and convert it to a clean dataframe

# In[51]:


dataframe = json_normalize(items) # flatten JSON
dataframe.head(5)


# In[52]:


# filter columns
filtered_columns = ['venue.name', 'venue.categories'] + [col for col in dataframe.columns if col.startswith('venue.location.')] + ['venue.id']
dataframe_filtered = dataframe.loc[:, filtered_columns]

# filter the category for each row
dataframe_filtered['venue.categories'] = dataframe_filtered.apply(get_category_type, axis=1)

# clean columns
dataframe_filtered.columns = [col.split('.')[-1] for col in dataframe_filtered.columns]

dataframe_filtered.head(5)


# Let's check Moscow's number of different type of venues.

# In[53]:


moscow_ven = pd.DataFrame(dataframe_filtered['categories'].value_counts())
moscow_ven.columns = ['Moscow']
moscow_ven.index.name = 'Venue Type'

# Add them to the ven_types dataframe
ven_types = pd.merge(left=moscow_ven, right=ven_types, how='outer', left_on='Venue Type', right_on='Venue Type')


# In[55]:


ven_types.head()


# Let's create a dataframe with the number of TIPS from Moscow.

# In[56]:


cat_tips5 = pd.DataFrame()

for row in dataframe_filtered.index.values.tolist()[0:7]: # Limit to 7 venues because venue tips is a premium endpoint
    venue_id = dataframe_filtered.loc[row, 'id']
    url = 'https://api.foursquare.com/v2/venues/{}?client_id={}&client_secret={}&v={}'.format(venue_id, CLIENT_ID, CLIENT_SECRET, VERSION)
    
    # Send GET request for result
    result = requests.get(url).json()
    
    # Get the number of TIPS
    cat_tips5.loc[row, 'Tips'] = result['response']['venue']['tips']['count']
    cat_tips5.loc[row, 'Category'] = venue_id = dataframe_filtered.loc[row, 'categories']


# In[57]:


cat_tips5


# ### Cape Town, S. Africa

# In[58]:


addr_CapeTown = 'Cape Town City Centre, Cape Town, South Africa'

geolocator = Nominatim(user_agent="foursquare_agent")
location = geolocator.geocode(addr_CapeTown)
latitude = location.latitude
longitude = location.longitude
print("Coordinates:", latitude, longitude)
print("Radius from city's center, to determine downtown area, is:", radius, "meters")


# Define a URL

# In[59]:


url = 'https://api.foursquare.com/v2/venues/explore?client_id={}&client_secret={}&ll={},{}&v={}&radius={}&limit={}'.format(CLIENT_ID, CLIENT_SECRET, latitude, longitude, VERSION, radius, LIMIT)
url


# Send GET request and examine results

# In[60]:


results = requests.get(url).json()
'There are {} venues in a radius of {} m from the downtown`s center. '.format(len(results['response']['groups'][0]['items']), radius)


# Get relevant part of JSON

# In[61]:


items = results['response']['groups'][0]['items']


# Process JSON and convert it to a clean dataframe

# In[62]:


dataframe = json_normalize(items) # flatten JSON
dataframe.head(5)


# In[63]:


# filter columns
filtered_columns = ['venue.name', 'venue.categories'] + [col for col in dataframe.columns if col.startswith('venue.location.')] + ['venue.id']
dataframe_filtered = dataframe.loc[:, filtered_columns]

# filter the category for each row
dataframe_filtered['venue.categories'] = dataframe_filtered.apply(get_category_type, axis=1)

# clean columns
dataframe_filtered.columns = [col.split('.')[-1] for col in dataframe_filtered.columns]

dataframe_filtered.head(5)


# Let's check Cape Town's number of different type of venues.

# In[64]:


capetown_ven = pd.DataFrame(dataframe_filtered['categories'].value_counts())
capetown_ven.columns = ['Cape Town']
capetown_ven.index.name = 'Venue Type'

# Add them to the ven_types dataframe
ven_types = pd.merge(left=capetown_ven, right=ven_types, how='outer', left_on='Venue Type', right_on='Venue Type')
ven_types.head(50)


# Let's create a dataframe with the number of TIPS from Cape Town.

# In[65]:


cat_tips6 = pd.DataFrame()

for row in dataframe_filtered.index.values.tolist()[0:7]: # Limit to 7 venues because venue tips is a premium endpoint
    venue_id = dataframe_filtered.loc[row, 'id']
    url = 'https://api.foursquare.com/v2/venues/{}?client_id={}&client_secret={}&v={}'.format(venue_id, CLIENT_ID, CLIENT_SECRET, VERSION)
    
    # Send GET request for result
    result = requests.get(url).json()
    
    # Get the number of TIPS
    cat_tips6.loc[row, 'Tips'] = result['response']['venue']['tips']['count']
    cat_tips6.loc[row, 'Category'] = venue_id = dataframe_filtered.loc[row, 'categories']


# In[66]:


cat_tips6


# ### Paris, France

# In[67]:


addr_Paris = '1st arrondissement of Paris, Paris, France'

geolocator = Nominatim(user_agent="foursquare_agent")
location = geolocator.geocode(addr_Paris)
latitude = location.latitude
longitude = location.longitude
print("Coordinates:", latitude, longitude)
print("Radius from city's center, to determine downtown area, is:", radius, "meters")


# Define a URL

# In[68]:


url = 'https://api.foursquare.com/v2/venues/explore?client_id={}&client_secret={}&ll={},{}&v={}&radius={}&limit={}'.format(CLIENT_ID, CLIENT_SECRET, latitude, longitude, VERSION, radius, LIMIT)
url


# Send GET request and examine results

# In[69]:


results = requests.get(url).json()
'There are {} venues in a radius of {} m from the downtown`s center. '.format(len(results['response']['groups'][0]['items']), radius)


# Get relevant part of JSON

# In[70]:


items = results['response']['groups'][0]['items']


# Process JSON and convert it to a clean dataframe

# In[71]:


dataframe = json_normalize(items) # flatten JSON
dataframe.head(5)


# In[72]:


# filter columns
filtered_columns = ['venue.name', 'venue.categories'] + [col for col in dataframe.columns if col.startswith('venue.location.')] + ['venue.id']
dataframe_filtered = dataframe.loc[:, filtered_columns]

# filter the category for each row
dataframe_filtered['venue.categories'] = dataframe_filtered.apply(get_category_type, axis=1)

# clean columns
dataframe_filtered.columns = [col.split('.')[-1] for col in dataframe_filtered.columns]

dataframe_filtered.head(5)


# Let's check Paris' number of different type of venues.

# In[73]:


paris_ven = pd.DataFrame(dataframe_filtered['categories'].value_counts())
paris_ven.columns = ['Paris']
paris_ven.index.name = 'Venue Type'

# Add them to the ven_types dataframe
ven_types = pd.merge(left=paris_ven, right=ven_types, how='outer', left_on='Venue Type', right_on='Venue Type')
ven_types.head(50)


# Let's create a dataframe with the number of TIPS from Cape Town.

# In[74]:


cat_tips7 = pd.DataFrame()

for row in dataframe_filtered.index.values.tolist()[0:7]: # Limit to 7 venues because venue tips is a premium endpoint
    venue_id = dataframe_filtered.loc[row, 'id']
    url = 'https://api.foursquare.com/v2/venues/{}?client_id={}&client_secret={}&v={}'.format(venue_id, CLIENT_ID, CLIENT_SECRET, VERSION)
    
    # Send GET request for result
    result = requests.get(url).json()
    
    # Get the number of TIPS
    cat_tips7.loc[row, 'Tips'] = result['response']['venue']['tips']['count']
    cat_tips7.loc[row, 'Category'] = venue_id = dataframe_filtered.loc[row, 'categories']


# In[75]:


cat_tips7


# ### Athens, Greece

# In[76]:


addr_Athens = 'Ermou street, Athens, Greece'

geolocator = Nominatim(user_agent="foursquare_agent")
location = geolocator.geocode(addr_Athens)
latitude = location.latitude
longitude = location.longitude
print("Coordinates:", latitude, longitude)
print("Radius, from city's center to determine downtown area, is:", radius, "meters")


# Define a URL

# In[77]:


url = 'https://api.foursquare.com/v2/venues/explore?client_id={}&client_secret={}&ll={},{}&v={}&radius={}&limit={}'.format(CLIENT_ID, CLIENT_SECRET, latitude, longitude, VERSION, radius, LIMIT)
url


# Send GET request and examine results

# In[78]:


results = requests.get(url).json()
'There are {} venues in a radius of {} m from the downtown`s center. '.format(len(results['response']['groups'][0]['items']), radius)


# Get relevant part of JSON

# In[79]:


items = results['response']['groups'][0]['items']


# In[80]:


dataframe = json_normalize(items) # flatten JSON
dataframe.head(5)


# In[81]:


# filter columns
filtered_columns = ['venue.name', 'venue.categories'] + [col for col in dataframe.columns if col.startswith('venue.location.')] + ['venue.id']
dataframe_filtered = dataframe.loc[:, filtered_columns]

# filter the category for each row
dataframe_filtered['venue.categories'] = dataframe_filtered.apply(get_category_type, axis=1)

# clean columns
dataframe_filtered.columns = [col.split('.')[-1] for col in dataframe_filtered.columns]

dataframe_filtered.head(5)


# **Let's check Athens' number of different type of venues and add them into a dataframe** 

# In[82]:


athens_ven = pd.DataFrame(dataframe_filtered['categories'].value_counts())
athens_ven.columns = ['Athens']
athens_ven.index.name = 'Venue Type'


# * At the moment, we have gathered all types of venues at a radius of ~4.5 km around city centers. 
# * Each city's data is limited to 50 venues. 
# * We will keep categories that appear in 2 out of 5 cities, at least. 'Cleaning' our data in that way to avoid local outliers.  

# In[83]:


athens_ven


# Concatenate the category tips from cat_tips dataframes (1~7) to one dataframe. Then, we will group the categories with the average number of TIPS per category.

# In[84]:


category_tips = pd.concat([cat_tips1, cat_tips2 , cat_tips3, cat_tips4 , cat_tips5, cat_tips6, cat_tips7], ignore_index=True)


# In[86]:


category_tips.columns = ['Tips', 'Venue Type']


# In[88]:


category_tips.head()


# In[89]:


category_tips = category_tips.groupby(['Venue Type']).mean()


# In[90]:


category_tips.sort_values(['Tips'], ascending=False, inplace=True)


# In[91]:


category_tips


# ## Methodology <a name="methodology"></a>

# In this project we will direct our efforts on detecting venue types that our not so famous in Athens while they are famous in the majority of the other 7 cities. We will limit our analysis to area ~4.5 km around city center and to 50 venues per city center. Regarding tips number we will limit our analysis to 7 due to API's endpoint restrictions (limit at 50 premium calls per day).
# 
# In first step we have collected the required data: location and type (category) of every venue within 4.5 km from city center for every city. We have also collected tips number for the first 10 venues per city.
# 
# Second step in our analysis will be calculation and exploration of most common venue types. Then we will normalize the data according to min-max normalization.
# 
# Finally, we will apply a simple **Multiple-Criteria Decision Analysis MCDA** to conclude, according to our data, to the suggested type of venue that will have increased odds of success in the downtown of Athens.

# ## Analysis <a name="analysis"></a>

# In this basic explanatory data analysis we will derive some useful info from our data. 
# 
# Let's drop the categories that appear only in one city center (outliers).

# In[92]:


missing_types = ven_types.isnull()
ven_types_temp = ven_types.copy(deep=True)
for row in missing_types.index.values.tolist():
    if missing_types.loc[row, :].value_counts()[0] < 2:
        ven_types_temp.drop(row, axis=0, inplace=True)
ven_types_temp.head(15)        


# We will merge the results from Athens with the main dataframe (df).

# In[93]:


df = pd.DataFrame()
df = pd.merge(left=athens_ven, right=ven_types_temp, how='outer', left_on='Venue Type', right_on='Venue Type')


# In[96]:


df.head(50)


# Let's concatenate similar venue types to simplify our dataframe.

# In[97]:


# Sum venue types that contain words café and coffee to a venue type called Café
df.loc['Café', :] = df[df.index.str.contains('Café') | df.index.str.contains('Coffee')].sum(axis=0)

# Drop the row Coffee Shop, it is unnecessary
df.drop('Coffee Shop', axis=0, inplace=True)


# In[98]:


# Sum venue types that contain words gym to a venue type called Gym
df.loc['Gym', :] = df[df.index.str.contains('Gym') | df.index.str.contains('Fitness')].sum(axis=0)

# Drop the row Coffee Shop, it is unnecessary
df.drop('Gym / Fitness Center', axis=0, inplace=True)


# In[101]:


df.head()


# **We will add a column that will show the most common venue type among cities and a column with the sum of veues from every category.**

# In[102]:


df[(df.isnull() == True)] = 0
df['Most Common'] = 0 # Initialize the column
for row in df.index.values.tolist():
    df.loc[row, 'Most Common'] = (df.loc[row ,:] != 0).value_counts()[1]


# In[104]:


df.head(50)


# We will add a column that will sum venues for every venue type.

# In[105]:


df['Sum'] = df['Cape Town'] + df['Moscow'] + df['Sydney'] + df['San Francisco'] + df['Seoul']


# **Sort the dataframe in descending order of the Most Common (venue type) and Sum. In that way, we will see the most popular venue types.**

# In[106]:


df.sort_values(['Most Common', 'Sum'], ascending=False, inplace=True)
df.head(15)


# **We will merge the results from Category Tips too.**

# In[108]:


df = pd.merge(left=df, right=category_tips, how='outer', left_on='Venue Type', right_on='Venue Type')


# **We will clean the dataframe from venue types that exist only in 3 ou of 8 cities and less.**

# In[109]:


df = df.drop(df[(df['Most Common'] < 3)].index.values.tolist(), axis=0)


# In[110]:


df = df.dropna()
df


# Similarly to **Content-Based Recommendation Systems** will be applied the same techniques to recommend a venue type with the highest prospects of success according to our data from foursquare API.

# We're going to use a simple **MCDA**. Firstly, we will assign weights for every feature (cities, most common, tips and sum). Then will normalize the values of the dataframe. Finally, we will multiply weights with the datadrame's normalized values and then summing up the resulting table by column. This operation is actually a dot product between a matrix and a vector, so we can simply accomplish by calling Pandas's "dot" function.

# Ranks sum to 1:
# 
# * assign a negative rank for **Athens** because we need to increase our chances to open an uncommon venue.
# * assign a big rank to **Most Common**, in that way will advance a venue type that is widespread in the 7 cities and together with the negative rank of Athens will suggest venue types common in 7 cities except Athens.
# * assign a big rank to **Tips** based on the principle that the higher the number of tips, which indicates that people are interested in the venue and would like to share their experience with all other users, the higher the popularity.
# * split the other ranks to the **remaining cities and Sum**, we do not consider them so important.

# In[132]:


weights = np.array([-1.0, 0.05, 0.05, 0.05, 0.05, 0.05, 0.05, 0.05, 0.85, 0.05, 0.75]) 


# In[133]:


weights


# ### We apply *Min-Max normalization* which is one of the most common ways to normalize data. 
# * for every feature, the minimum value of that feature gets transformed into a 0
# * the maximum value gets transformed into a 1 
# * and every other value gets transformed into a decimal between 0 and 1.

# In[134]:


from sklearn import preprocessing

x = df.values #returns a numpy array
min_max_scaler = preprocessing.MinMaxScaler()
x_scaled = min_max_scaler.fit_transform(x)


# In[135]:


df = pd.DataFrame(x_scaled, index=df.index, columns=df.columns)
df


# ### We will use *dot function* to multiply weights vector with our dataframe. And then we will sort the dataframe according to the results produced by the dot operation. 

# In[136]:


results = pd.DataFrame(df.dot(weights), columns = ['Scores'])
results.sort_values(['Scores'], ascending=False, inplace=True)


# Finally, let's get the results from our analysis.

# In[137]:


results


# To conclude our analysis we will choose ranks hihger than 50 %.

# In[138]:


print("Suggested venue types for downtown Athens are the following: ")
results[(results["Scores"] > 0.5)]


# ## Results and Discussion <a name="results"></a>

# Project's analysis shows that although there is a broad diversity of venues in Athens, there is a potential for venue types that are not so widespread in the center of Athens. The Top-four categories which score more than 0.5 are Art Museum, Bookstore, Plaza, Theater. **Art Museum outstands with a double score from the second category.**
# 
# After considering Athens venue categories the number of tips that each venue has received was calculated. This assumption based on the principle that the higher the number of tips, the more famous the venue. 
# 
# Finally, weights were set for the features (cities, number of different cities that a venue presents, number of tips) to calculate the final score for every category. For the final recommendation, the top four results proposed. It is worth mentioning that those categories are not optimal. The purpose of this analysis was to suggest a worldwide commonly known and successful venue that does not exist in Athens. Further examination of data's integrity required for more accurate results (ex. algorithm shows that there are zero hotels in the downtown of Athens, which is wrong).

# ## Conclusion <a name="conclusion"></a>

# The scope of this project was to recommend a global venue type commonly spread in many of the datasets cities and unknown in Athens. This recommendation based on the principle that a venue type that is famous in the majority of the dataset's cities will be respectively desirable, recognizable, and profitable in Athens too. For the final decision correctness of the principle and integrity of the data must be carefully examined.

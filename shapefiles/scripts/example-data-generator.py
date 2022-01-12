"""This basic script creates a single output csv of random data to make
it easy to test the interface without constantly having to upload new
datasets.

It reads all the composites available for a site, concatenates every
'zone_id' into its first column and adds three columns of random data
(integer, 1-10) to be plotted.
"""


import os
from random import randint

import geopandas as gpd
import pandas as pd


# list all directories within a deims site and remove
# files/directories we aren't interested in
# TODO: make this accept user input and update for new structure
dirs = os.listdir('../deims/cairngorms')
dirs.remove('raw')
dirs.remove('scottish-national-sources.txt')

# intialise empty series
x = pd.Series(dtype='object')
y1 = pd.Series(dtype='int')
y2 = pd.Series(dtype='int')
y3 = pd.Series(dtype='int')

# for each directory previously discovered, read its
# shapefile and append the IDs to the series x
#for a in ['atelier-alpes','braila-islands','cairngorms','donana','eisenwurzen']:
for a in ['cairngorms']:
    for b in dirs:
        z = gpd.read_file('../deims/{}/{}/boundaries.shp'.format(a,b))
        x = x.append(z['zone_id'])

# for each id, generate three random numbers to act as data
for a in range(len(x)):
    y1 = y1.append(pd.Series(randint(1,10)))
    y2 = y2.append(pd.Series(randint(1,10)))
    y3 = y3.append(pd.Series(randint(1,10)))

# reset the index of each series as there are duplicates
# in each, due to the way pandas allows repeated indexes
x.reset_index(drop=True,inplace=True)
y1.reset_index(drop=True,inplace=True)
y2.reset_index(drop=True,inplace=True)
y3.reset_index(drop=True,inplace=True)

# construct a dataframe with the desired column names
# and specify a dtype, since pandas doesn't respect the
# type of each series for some reason. Object avoids
# mangling of integers to float
outframe = pd.DataFrame({
    'zone_id' : x,
    'data1' : y1,
    'data2' : y2,
    'data3' : y3
},dtype='object')

outframe.to_csv('../../data/testdata.csv',index=False)

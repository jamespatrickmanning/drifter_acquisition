#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Feb 12 06:10:24 2023

@author: JiM
Example Cartopy code to plot a track taken from https://notebook.community/rsignell-usgs/ipython-notebooks/files/Cartopy%20Examples

"""
import matplotlib.patches as mpatches
import matplotlib.pyplot as plt
import shapely.geometry as sgeom
import cartopy
import cartopy.crs as ccrs
import cartopy.io.shapereader as shpreader
import pandas as pd

#lons, lats = katrina_sample_data()
case='drift_glerl_2022_1.csv'
df=pd.read_csv('/home/user/drift/'+case)
lons=df.LON.values
lats=df.LAT.values


plt.figure(figsize=(8,6))
ax = plt.axes(projection=cartopy.crs.PlateCarree())

ax.add_feature(cartopy.feature.LAND)
ax.add_feature(cartopy.feature.OCEAN)
ax.add_feature(cartopy.feature.COASTLINE)
ax.add_feature(cartopy.feature.BORDERS, linestyle=':')
ax.add_feature(cartopy.feature.LAKES, alpha=0.5)
ax.add_feature(cartopy.feature.RIVERS)
ax.gridlines(draw_labels=True, dms=True, x_inline=False, y_inline=False)
#ax.set_extent([-20, 60, -40, 40])
#plt.show()


ax.set_xlim([int(min(lons)-1.), int(max(lons)+1.)])
ax.set_ylim([int(min(lats)-1.), int(max(lats)+1.)])
#ax.set_xlim([-88., -86.])
#ax.set_ylim([44., 46.])
plt.show()

shpname='admin_1_states_provinces_lakes'
states_shp = shpreader.natural_earth(resolution='110m',
                                     category='cultural',
                                     name=shpname)

# to get the effect of having just the states without a map "background"
# turn off the outline and background patches
ax.background_patch.set_visible(False)
ax.outline_patch.set_visible(False)

plt.title('track of '+case[0:-4])

# turn the lons and lats into a shapely LineString
track = sgeom.LineString(zip(lons, lats))

# buffer the linestring by two degrees (note: this is a non-physical
# distance)
#track_buffer = track.buffer(2)


for state in shpreader.Reader(states_shp).geometries():
    # pick a default color for the land with a black outline,
    # this will change if the storm intersects with our track
    facecolor = [0.9375, 0.9375, 0.859375]
    edgecolor = 'black'

    if state.intersects(track):
        facecolor = 'red'
    #elif state.intersects(track_buffer):
     #   facecolor = '#FF7E00'

    ax.add_geometries([state], ccrs.PlateCarree(),
                      facecolor=facecolor, edgecolor=edgecolor)

#ax.add_geometries([track_buffer], ccrs.PlateCarree(),
#                  facecolor='#C8A2C8', alpha=0.5)
ax.add_geometries([track], ccrs.PlateCarree(),
                  facecolor='none')

# make two proxy artists to add to a legend
'''
direct_hit = mpatches.Rectangle((0, 0), 1, 1, facecolor="red")
within_2_deg = mpatches.Rectangle((0, 0), 1, 1, facecolor="#FF7E00")
labels = ['State directly intersects\nwith track',
          'State is within \n2 degrees of track']
plt.legend([direct_hit, within_2_deg], labels,
           loc=3, fancybox=True)
'''

plt.show()
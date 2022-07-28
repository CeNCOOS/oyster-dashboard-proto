from unittest import skip
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import datetime as dt
import os
from dateutil import tz
import seaborn as sns
import numpy as np
import urllib
import airsea, warnings
from astral import sun, Observer
import logging
for handler in logging.root.handlers[:]:
    logging.root.removeHandler(handler)

logging.basicConfig(filename='./oyster.log', level=logging.ERROR)


def get_shore_station_data(back_bay=False):
    '''Get shore station data from the CeNCOOS ERDDAP'''
    if back_bay:
        url = "http://erddap.cencoos.org/erddap/tabledap/morro-bay-bs1.csvp?time%2Cmass_concentration_of_chlorophyll_in_sea_water%2Cmass_concentration_of_oxygen_in_sea_water%2Cfractional_saturation_of_oxygen_in_sea_water%2Csea_water_practical_salinity%2Csea_water_temperature%2Csea_water_turbidity%2Csea_water_ph_reported_on_total_scale_internal%2Csea_water_ph_reported_on_total_scale_external&time>now-7days"

    else:
        url = "http://erddap.cencoos.org/erddap/tabledap/edu_calpoly_marine_morro.csvp?time%2Cmass_concentration_of_chlorophyll_in_sea_water%2Cmass_concentration_of_oxygen_in_sea_water%2Cfractional_saturation_of_oxygen_in_sea_water%2Csea_water_practical_salinity%2Csea_water_temperature%2Csea_water_turbidity%2Csea_water_ph_reported_on_total_scale_internal%2Csea_water_ph_reported_on_total_scale_external&time>now-7days"
    
    headers= ['time','chlorophyll','oxygen_conc','oxygen_frac','salinity','swtemp','turbidity','pH_internal','pH_external']
    try:
        df = pd.read_csv(url, names=headers,skiprows=1)
        df['dateTime'] = pd.to_datetime(df['time'])
        df.index = df['dateTime']
        df = df.tz_convert('US/Pacific')
        df_hourly = df.resample('1H').mean()
        df_rolling = df[["chlorophyll","oxygen_conc","oxygen_frac","salinity","swtemp","turbidity","pH_internal","pH_external"]].rolling(window=12,center=True,win_type='hamming').mean()
        return df, df_hourly, df_rolling
    except urllib.error.HTTPError:
        logging.error("Trouble reaching the CeNCOOS ERDDAP",exc_info=True)
        return None, None, None

def get_wind_data():
    """
    Retrieve offshore wind data
    """
    url = 'http://erddap.cencoos.org/erddap/tabledap/wmo_46028.csvp?time%2Csea_water_temperature%2Cwind_speed%2Cwind_from_direction&time>now-7days'
    headers= ['time','wtemp_offshore','wind_speed_ms','wind_from_direction']
    try:
        wind_df = pd.read_csv(url,names=headers,skiprows=1)
        wind_df['dateTime'] = pd.to_datetime(wind_df['time'])
        wind_df.index = wind_df['dateTime']
        wind_df = wind_df.tz_convert('US/Pacific')
        wind_df.resample('1h').nearest()
        return wind_df
    except Exception as e:
        logging.error("Trouble reaching the CeNCOOS ERDDAP", exc_info=True)
        return None

def process_wind(wind_df):
    """Calculate upwelling (ekman transport) from wind data and resample
    """
    wind_df['windstress'] = airsea.windstress.stress(wind_df['wind_speed_ms'],z=4.1, drag='largepond')
    v = wind_df['windstress'] * -np.cos(np.deg2rad(wind_df['wind_from_direction']))
    u = wind_df['windstress'] * -np.sin(np.deg2rad(wind_df['wind_from_direction']))
    ekman = (-1/0.935)*v # 1/coriolis parameter
    return(ekman)

def get_sunset_sunrise(days=7):
    """Using the `astral` api package we can request sunrise and sunset times for humboldt to use for shading the plots."""

    stime = dt.date.today()
    etime = stime - dt.timedelta(days=days)
    obs = Observer(latitude=35.339658, longitude=-120.850287,elevation=0)
    sunrise = []
    sunset = []
    for day in range(days+1):
        sunrise.append(sun.sun(obs,date=stime - dt.timedelta(days=day),tzinfo='US/Pacific')['sunrise'])
        sunset.append(sun.sun(obs,date=stime - dt.timedelta(days=day),tzinfo='US/Pacific')['sunset'])
    return sunset, sunrise

def add_nighttime(ax,sunrise,sunset,stime,etime):
    ax.axvspan(stime, etime, color='.85',zorder=-5)
    for sr,ss in zip(sunrise,sunset):
        ax.axvspan(ss.astimezone(tz=None),sr.astimezone(tz=None), color='w',zorder=-2)
    return ax

def generate_plot():
    df_backbay, df_hourly_backbay, df_rolling_backbay = get_shore_station_data(back_bay=True)
    df_forebay, df_hourly_forebay, df_rolling_forebay = get_shore_station_data(back_bay=False)
    skip_front = False
    skip_back = False
    
    wind_df = get_wind_data()
    sunset, sunrise = get_sunset_sunrise(days=7)
    # stime = df.index.max() + dt.timedelta(hours=1)
    stime = dt.date.today()
    etime = stime - dt.timedelta(days=7)
    fig, (ax_temp,ax_chl,ax_ph,ax_wind) = plt.subplots(4,sharex=True,gridspec_kw=dict(hspace=0.4))
    fig.set_size_inches(10,10)

    ax_temp = add_nighttime(ax_temp,sunrise,sunset,stime,etime)
    try:
        ax_temp.scatter(df_hourly_backbay.index,df_hourly_backbay['swtemp'], s=5, c='#4876B1')
        ax_temp.plot(df_rolling_backbay.index,df_rolling_backbay['swtemp'], color='#4876B1', label='BS1')
    
    except:
        skip_back = True
        ax_temp.text(.5,.5,"BS1 Data Unavailable - {}".format(dt.datetime.now()),transform=ax_temp.transAxes)
    
    try:
        ax_temp.scatter(df_hourly_forebay.index,df_hourly_forebay['swtemp'], s=5, c='#1B1725')
        ax_temp.plot(df_rolling_forebay.index,df_rolling_forebay['swtemp'], color='#1B1725', label='T-Pier')
    except:
        skip_front = True
        ax_temp.text(.5,.5,"T-Pier Data Unavailable - {}".format(dt.datetime.now()),transform=ax_temp.transAxes)  

    if wind_df is not None:
        ekman = process_wind(wind_df)
        ax_temp.plot(wind_df.index, wind_df['wtemp_offshore'],color='#B14E48',lw=2,label='Offshore')

    ax_temp.get_xaxis().set_visible(False)
    sns.despine(ax=ax_temp,bottom=True,trim=False);
    ax_temp.yaxis.set_label_position("right")
    ax_temp.yaxis.set_label_coords(1.025,.6)


    ax_temp.set_ylabel('Seawater\nTemperature [C]',rotation=0,labelpad=0,size=20,color='#4876B1',fontweight='bold', horizontalalignment='left')
    ax_temp.tick_params(axis='y', labelsize=14)
    leg = ax_temp.legend(ncol=3,frameon=False, fontsize=16, loc=(.0,-.23),markerscale=3, labelspacing=1)
    for legobj in leg.legendHandles:
        legobj.set_linewidth(3.0)


    ax_chl = add_nighttime(ax_chl,sunrise,sunset,stime,etime)
    if not skip_back:
        ax_chl.scatter(df_hourly_backbay.index, df_hourly_backbay['chlorophyll'],s=5,c='#5C8D42')
        ax_chl.plot(df_rolling_backbay.index, df_rolling_backbay['chlorophyll'], color='#5C8D42', label='BS1')
        if df_rolling_backbay['chlorophyll'].max() < 10:
            ax_chl.set_ylim(0,10)
    else:
        ax_chl.text(.5,.5,"BS1 Data Unavailable - {}".format(dt.datetime.now()),transform=ax_chl.transAxes)


    if not skip_front:
        ax_chl.scatter(df_hourly_forebay.index, df_hourly_forebay['chlorophyll'],s=5,c='k')
        ax_chl.plot(df_rolling_forebay.index, df_rolling_forebay['chlorophyll'], color='k', label='T-Pier')
    else:
        ax_chl.text(.5,.5,"T-Pier Data Unavailable - {}".format(dt.datetime.now()),transform=ax_chl.transAxes)

    leg = ax_chl.legend(ncol=3,frameon=False, fontsize=16, loc=(.0,-.23),markerscale=3, labelspacing=1)
    for legobj in leg.legendHandles:
        legobj.set_linewidth(3.0)

    ax_chl.yaxis.set_label_coords(1.025,.42)
    ax_chl.get_xaxis().set_visible(False)
    ax_chl.set_ylabel('Chlorophyll\n[μg/L]',rotation=0,labelpad=90,size=20,color='#5C8D42',fontweight='bold', horizontalalignment='left')
    sns.despine(ax=ax_chl,offset=0,bottom=True,trim=False);
    ax_chl.tick_params(axis='y', labelsize=14 )
    

    ax_ph = add_nighttime(ax_ph,sunrise,sunset,stime,etime)
    if not skip_back:
        ax_ph.scatter(df_hourly_backbay.index, df_hourly_backbay['pH_internal'],s=15,marker='x' ,c='#586994',label='BS1 - Internal') #E16F1C
        ax_ph.plot(df_rolling_backbay.index, df_rolling_backbay['pH_internal'], color='#586994')
        ax_ph.scatter(df_hourly_backbay.index, df_hourly_backbay['pH_external'],s=15,c='#586994',label='BS1 - External')
        ax_ph.plot(df_rolling_backbay.index, df_rolling_backbay['pH_external'], color='#586994')
    else:
        ax_ph.text(.5,.5,"BS1 Data Unavailable - {}".format(dt.datetime.now()),transform=ax_ph.transAxes)
    
    if not skip_front:
        ax_ph.scatter(df_hourly_forebay.index, df_hourly_forebay['pH_internal'],s=15,marker='x' ,c='#E16F1C',label='BS1 - Internal') #E16F1C
        ax_ph.plot(df_rolling_forebay.index, df_rolling_forebay['pH_internal'], color='#E16F1C')
        ax_ph.scatter(df_hourly_forebay.index, df_hourly_forebay['pH_external'],s=15,c='#E16F1C',label='T-Pier - External')
        ax_ph.plot(df_rolling_forebay.index, df_rolling_forebay['pH_external'], color='#E16F1C')
    else:
        ax_ph.text(.5,.5,"T-Pier Data Unavailable - {}".format(dt.datetime.now()),transform=ax_ph.transAxes)

    ax_ph.legend(ncol=4,frameon=False, fontsize=12, loc=(-.01,-.25),markerscale=2, handletextpad=-0.1)
    
    # ax_ph.set_ylim(7.5,8.3)
    ax_ph.get_xaxis().set_visible(False)
    ax_ph.set_ylabel('pH\n[total scale]',rotation=0,labelpad=90,size=20,color='#E16F1C',fontweight='bold',horizontalalignment='left')
    sns.despine(ax=ax_ph,offset=0,bottom=True,trim=True)
    ax_ph.tick_params(axis='y', labelsize=14)
    ax_ph.yaxis.set_label_coords(1.025,.42)

    ax_wind = add_nighttime(ax_wind,sunrise,sunset,stime,etime)
    if wind_df is not None:
        ax_wind.plot(ekman.index,ekman,color='#482C3D',lw=4)
        ax_wind.plot(ekman.index,ekman,color='k',lw=1)
        ax_wind.fill_between(ekman.index,ekman,0,color='#482C3D',alpha=.5)
    else:
        ax_wind.text(.3,.65,'Data Unavailable',color='k',size=18,transform=ax_wind.transAxes)
    ax_wind.hlines(0,stime,etime,color='k',zorder=1)
    ax_wind.set_ylabel('Ekman Transport\n[m^2 per S]',rotation=0,labelpad=90,size=20,color='#482C3D',fontweight='bold')
    ax_wind.yaxis.set_label_coords(1.2,.42)

    date_fmt = mdates.DateFormatter('%b %d')
    sns.despine(ax=ax_wind,offset=0,trim=False);
    ax_wind.xaxis.set_major_formatter(date_fmt)
    ax_wind.xaxis.set_minor_locator(mdates.HourLocator(12,tz=tz.gettz('US/Pacific')))
    ax_wind.tick_params(axis='both', labelsize=14)
    ax_wind.set_ylim(-1,1)
    ax_wind.set_xlim(etime,stime)
    ax_wind.text(0,-.3,'Updated on: {}'.format(dt.datetime.now()),transform=ax_wind.transAxes)

    plt.savefig('morro_bay_conditions.png',dpi=150,bbox_inches='tight', pad_inches=0.1,)


def copy_file_to_webserver(FILE):
    """Copy images from to webserver where they can be viewed publically."""
    try:
        os.system('scp -i /etc/ssh/keys/pdaniel/scp_rsa {} skyrocket8.mbari.org:/var/www/html/data/oyster-dash-proto/ '.format(FILE))
        # print("Copied {} to webserver.".format(FILE))
    except Exception as e:
        print(e)
        

if __name__ == "__main__":
    warnings.filterwarnings("ignore")
    generate_plot()
    copy_file_to_webserver("morro_bay_conditions.png")
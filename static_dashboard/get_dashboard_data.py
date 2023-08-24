import pandas as pd
import json
import urllib.error
from astral import sun, Observer
import datetime as dt
# from . import plotting
import plotting # only uses if debugging in the __main__
import numpy as np
import os


class StationData:

    def __init__(self, param_fname) -> None:
        self.params = self.load_station_parameters(param_fname)
        self.data_url = self.build_url()
        self.short_names, self.units = self.get_headers()
        self.rolling = self.is_rolling()
        self.sunset, self.sunrise = self.get_sunset_sunrise()
        self.df = self.get_data_from_erddap()


    def load_station_parameters(self, param_fname):
        """ Return parameter dict with all of the info for making requests of data

        Args:
            param_file (str): location of JSON file for parameters

        Returns:
            dict: parameters for downloading data from CeNCOOS ERDDAP
        """
        with open(param_fname) as json_file:
            data = json.load(json_file)
        return data

    def build_url(self):
        """
        Build the URL for making the erddap request
        """
        ext = ".csvp"
        BASE_URL = "http://erddap.cencoos.org/erddap/tabledap/" + self.params['erddap-id'] + ext + "?time"
        date_range = "&time>now-" + str(self.params['past_days']) + "days"
        data_vars = ""
        for vars in self.params['data_variables']:
            data_vars += "%2C" + vars['var-id']
        return BASE_URL + data_vars + date_range

    def get_headers(self):
        """
        Return list of short names and the units from the parameter data

        Returns:
            short_names[list]: List of of the short names for each parameter
            units[list]: List of units for each parameter
        """
        short_names = []
        units = []
        for vars in self.params['data_variables']:
            short_names.append(vars['short_name'])
            units.append(vars['units'])
        return short_names, units

    def is_rolling(self):
        """
        Return a list of parameters that should have a rolling average applied
        """
        rolling = []
        for vars in self.params['data_variables']:
            if "running_mean" in vars.keys():
                rolling.append(vars['short_name'])
        return(rolling)


    def get_data_from_erddap(self):
        """
        Make a call to the erddap REST service to get data and process the data.
        Data are first downsampled to an hourly mean from whatever their native resolution is.
        If the rolling parameter is added, take a rolling mean of the that parameter and add it to the data frame.

        Returns:
            pd.Dataframe: A dataframe with the hourly data from the station.
        """
        headers = ['time'] + self.short_names
        try:
            df = pd.read_csv(self.data_url, names=headers, skiprows=1)
            df['dateTime'] = pd.to_datetime(df['time'])
            df.index = df['dateTime']
            df = df.tz_convert('US/Pacific')
            df_hourly = df.resample('1H').mean()
            if len(self.rolling) > 0:
                for roll in self.rolling:
                    df_hourly[roll + "_rolling"] = df_hourly[roll].rolling(window=6,center=True,win_type='hamming').mean()

            return df_hourly

        except urllib.error.HTTPError:
            print("Trouble reaching the CeNCOOS ERDDAP", exc_info=True)


    def get_sunset_sunrise(self):
        """Using the `astral` api package we can request sunrise and sunset times for humboldt to use for shading the plots."""
        days = int(self.params['past_days']) + 1
        stime = dt.date.today() + dt.timedelta(days=1)

        obs = Observer(latitude=35.339658, longitude=-120.850287,elevation=0)
        sunrise = []
        sunset = []
        for day in range(days+1):
            sunrise.append(sun.sun(obs,date=stime - dt.timedelta(days=day),tzinfo='US/Pacific')['sunrise'])
            sunset.append(sun.sun(obs,date=stime - dt.timedelta(days=day),tzinfo='US/Pacific')['sunset'])
        return sunset, sunrise


    def get_ylims(self,ix,sname):
        """
        Check json for ylims, if not, use default from data.
        Check the ylims against values and make sure that data isn't cut out
        """
        if "ylims" in self.params['data_variables'][ix].keys():
            ylims = self.params['data_variables'][ix]['ylims']
            if self.df[sname].max() > ylims[1]:
                ylims[1] = self.df[sname].max()
            if self.df[sname].min() < ylims[0]:
                ylims[0] = self.df[sname].min()
            return ylims

        else:
            return None


    def make_plot(self):
        """ Generate the Plot for the page
        1. make the figure to size
        2. generate color cycle
        3. Loop through short names and plot data
        """
        num_axes=len(self.short_names)
        fig, ax = plotting.make_figure(num_axes)
        plotting.add_title(super_string=self.params['station-name'], sub_string=self.params['data-provider'])
        colors = plotting.color_maps(num_axes)

        stime = dt.datetime.now()
        etime = stime - dt.timedelta(days=7)

        not_last = True
        comments = None
        for i, sname in enumerate(self.short_names):

            ax[i].scatter(self.df.index, self.df[sname],s=5, c=colors[i])
            plotting.add_nighttime(ax=ax[i],sunrise=self.sunrise, sunset=self.sunset, stime=stime + dt.timedelta(hours=14), etime=etime - dt.timedelta(hours=14))

            if sname in self.rolling:
                ax[i].plot(self.df.index, self.df[sname+"_rolling"], color=colors[i])

            if i+1 == len(self.short_names):
                not_last=False
                if "comments" in self.params.keys():
                    comments = self.params['comments']


            ylims = self.get_ylims(i, sname)
            if ylims is not None:
                ax[i].set_ylim(ylims[0],ylims[1])

            ax[i].set_xlim(etime, stime + dt.timedelta(hours=8))
            plotting.format_axes(ax=ax[i], short_name=sname, unit=self.units[i], label_color=colors[i], not_last=not_last, comments=comments)

    def fill_data_to_present(self):
        """Fill data from the last available data point to the current hour. If no data is available, fill with NaN. 
        This will get made into a 'null' value later.
        """
        now = pd.Timestamp.now().round('60min').to_pydatetime() # Round the time to the nearest hour
        trange = pd.date_range(start=now-dt.timedelta(days=14),end=now, freq='1H') # This will be the range of the data to fill
        return self.df.tz_localize(None).reindex(trange) # Reindex the dataframe to the new range, its that easy. Dont forget to drop the TZ info
        
    def calculate_slope(self, var):
        
        try:
            roll = self.df[var].rolling(window=44,win_type="hann",min_periods=20).mean()
            x = np.arange(roll[20:].index.size) # = array([0, 1, 2, ..., 3598, 3599, 3600])
            fit = np.polyfit(x, roll[20:].values, 1)
            slope, intercept = fit[0], fit[1]
            slope = slope * 24 * 14 # Convert to per 14
            print("slope: ",slope)
            
        except:
            slope = np.nan
        
        return slope


    def write_JSON(self, out_dir, copy_to_web=False):
        """ Generate a JSON file from the data to be used for the dynamic plotting on the website
        Args:
            out_dir (str): the path to save the json file in locally. Filenames are based on the erddap-id specified in the parameter file.
            copy_to_web (bool, optional): Defaults to False. True will copy the file to the spyglass webserver to the hardcoded directory.
        """
        df_drop_na = self.fill_data_to_present()
        time = df_drop_na.index.values
        seconds_in_seven_hours = 7 * 60 * 60 # Offset for timezone in seconds
        unix_time = [int((pd.to_datetime(t) - dt.datetime(1970, 1, 1)).total_seconds()) + seconds_in_seven_hours for t in time]
        
        for var_name in self.short_names:
            df_drop_na[var_name] = df_drop_na[var_name].round(2)    
        
        # Replace NaN with NULL
        df_drop_na = df_drop_na.fillna(value="null")
        # Start JSON as dict
        dictionary = {
            "name": self.params['station-name'],
            "datetime": unix_time,
        }
        
        for var_name, var_unit in zip(self.short_names, self.units):
            dictionary[var_name] = {
                "values" : list(df_drop_na[var_name].values),
                "units": self.units[self.short_names.index(var_name)],
                "slope_scale" : "null",
                'slope' : round(self.calculate_slope(var_name),3)
            }
            # Chose scale based on absolute range of slope over 14 days
            # For temp that might be -5 C to 5 C, so scale is 10.
            
            if var_name == "Temperature":
                dictionary[var_name]['slope_scale'] = 10
            
            elif var_name == "Dissolved Oxygen":
                dictionary[var_name]['slope_scale'] = 10
            
            elif var_name == "Chlorophyll-a":
                dictionary[var_name]['slope_scale'] = 40
            
            elif var_name == "pH":
                dictionary[var_name]['slope_scale'] = 1
            
        # Serializing json
        json_object = json.dumps(dictionary, indent=4)
        
        # Writing to sample.json
        FILE = os.path.join(out_dir,self.params['erddap-id']+".json")
        with open(FILE, "w") as outfile:
            outfile.write(json_object)
        
        if copy_to_web:
            plotting.copy_file_to_webserver(FILE, server_dest="data/oyster-dash-proto/dynamic_dashboard")


if __name__ == "__main__":
    # fname = "/home/pdaniel/static-dashboards/parameter_files/bs-SLO-params.json"
    fname = "./dynamic_dashboard/bm-morro-params.json"
    stationData = StationData(fname)
    print(stationData.fill_data_to_present().tail())
    stationData.write_JSON("./dynamic_dashboard/", copy_to_web=False)
    # print(stationData.write_JSON("/home/pdaniel/static-dashboards/dynamic_json", write_to_web=False))
    # stationData.make_plot()
    # plotting.save_fig(stationData.params['web-url-fname'], directory="/Users/patrick/Documents/CeNCOOS/oyster-dashboard-proto/figures/",transfer=True)

    




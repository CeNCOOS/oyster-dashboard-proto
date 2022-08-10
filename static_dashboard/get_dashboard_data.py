import pandas as pd
import json
import urllib.error
from astral import sun, Observer
import datetime as dt
from . import plotting

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
        days = int(self.params['past_days'])
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
            plotting.add_nighttime(ax=ax[i],sunrise=self.sunrise, sunset=self.sunset, stime=stime + dt.timedelta(hours=14), etime=etime)

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

    


if __name__ == "__main__":
    fname = "/Users/patrick/Documents/CeNCOOS/oyster-dashboard-proto/tests/hsu-params.json"
    stationData = StationData(fname)
    stationData.make_plot()
    plotting.save_fig(stationData.params['web-url-fname'], directory="/Users/patrick/Documents/CeNCOOS/oyster-dashboard-proto/figures/",transfer=False)

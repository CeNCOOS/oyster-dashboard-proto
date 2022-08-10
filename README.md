# Static Oyster Dashboard

static_dashboard is a Python library for making static plots (.pngs) of time series data that are available on the [erddap.cencoos.org](erddap.cencoos.org).  Plots are made by providing JSON file with the relevant information about what dataset and what variables to use.

## Installation

Install the package using the `setup.py` after cloning this repo.

```bash
python setup.py install
pip install -r requirements.txt
```

## Usage

```python
import static_dashboard.get_dashboard_data
import static_dashboard.plotting

# Point to parameters JSON file
param_fname = "bm-SLO-params.json"
stationData = static_dashboard.get_dashboard_data.StationData(param_fname)
stationData.make_plot()
static_dashboard.plotting.save_fig(stationData.params['web-url-fname'])
```

## License
[MIT](https://choosealicense.com/licenses/mit/)


---
## Old Version ##
A static version of the oyster dashboard was created to for the CeNCOOS website. Data from the past 7 days is pulled from the [CeNCOOS ERDDAP](http://erddap.cencoos.org/erddap/index.html) via a RESTful call. Currently, Temperature, Salinity, Chlorophyll-a, and pH are displayed, however, this is configurable. For each parameter, a six hour rolling average (boxcar) is calculated to show trends, the filter type and window size are both adjustable. Local Ekman mass transport, a proxy for upwelling, is calculated as:  

$ M_x = \frac{1}{f}\tau_{W}^{Y} $

Where $\tau_{W}^{Y}$ is the alongshore windstress estimated from an offshore weather buoy using Large and Pond to estimate the drag coefficient and account for the height of the wind measurements. Day and night cycles are shown as the grey shading and retrieved using the [Astral Package](https://pypi.org/project/astral/).

Check out the `Oyster-Dashboard-Proto.ipynb` notebook to see how each step works.

A script located at `concave.shore.mbari.org/home/pdaniel/oyster-dashboard/humboldt-oyster-proto.py` is run every 15 minutes on the `pdaniel crontab` and a new image is copied to `https://www.cencoos.org/data/oyster-dash-proto/humboldt_bay_conditions.png` and displayed on `https://www.cencoos.org/humboldt-bay-oyster-dashboard/`.

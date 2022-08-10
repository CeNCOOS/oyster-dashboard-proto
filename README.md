# Static Oyster Dashboard

P. Daniel

___
__Update__  
The architecture has been updated to allow for scaling to other sites. 

Use the parameter JSON files to pass along information for processing. See example in ./tests/ directory


Generate requirements.txt with:  
`python -m  pipreqs.pipreqs --encoding utf-8  /path/to/project`

To install from requirements.txt:  
`pip install -r requirements.txt`

___



## Old Version ##
A static version of the oyster dashboard was created to for the CeNCOOS website. Data from the past 7 days is pulled from the [CeNCOOS ERDDAP](http://erddap.cencoos.org/erddap/index.html) via a RESTful call. Currently, Temperature, Salinity, Chlorophyll-a, and pH are displayed, however, this is configurable. For each parameter, a six hour rolling average (boxcar) is calculated to show trends, the filter type and window size are both adjustable. Local Ekman mass transport, a proxy for upwelling, is calculated as:  

$ M_x = \frac{1}{f}\tau_{W}^{Y} $

Where $\tau_{W}^{Y}$ is the alongshore windstress estimated from an offshore weather buoy using Large and Pond to estimate the drag coefficient and account for the height of the wind measurements. Day and night cycles are shown as the grey shading and retrieved using the [Astral Package](https://pypi.org/project/astral/).

Check out the `Oyster-Dashboard-Proto.ipynb` notebook to see how each step works.

A script located at `concave.shore.mbari.org/home/pdaniel/oyster-dashboard/humboldt-oyster-proto.py` is run every 15 minutes on the `pdaniel crontab` and a new image is copied to `https://www.cencoos.org/data/oyster-dash-proto/humboldt_bay_conditions.png` and displayed on `https://www.cencoos.org/humboldt-bay-oyster-dashboard/`.

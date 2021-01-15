# Static Oyster Dashboard

P. Daniel

A static version of the oyster dashboard was created to for the CeNCOOS website. Data are pulled from the Humbold Bay shore station via a RESTful call to the CeNCOOS ERDDAP. A six hour rolling average (boxcar) is calculated for each parameter.

Data are displayed for the past 7 days. Nighttime is shaded with a grey coloring. Check out the `Oyster-Dashboard-Proto.ipynb` notebook to see how each step works.



A script located at `concave.shore.mbari.org/home/pdaniel/oyster-dashboard/humboldt-oyster-proto.py` is run every 15 minutes on the `pdaniel crontab` and a new image is copied to `https://www.cencoos.org/data/oyster-dash-proto/humboldt_bay_conditions.png` and displayed on `https://www.cencoos.org/humboldt-bay-oyster-dashboard/`.


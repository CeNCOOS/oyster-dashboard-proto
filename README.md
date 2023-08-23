# Dynamic Dahshboard
The dynamic dashboards are bit more complicated than the static versions. There are two basic componenets, __data retrieval__ and __plotting__.
## Data Retrieval ##
### Parameter Files ###
A JSON file is used to store the parameters for each dashboard. The JSON file is used to store the following information:
1. __erddap-id__: The unique identifier for the dataset on the ERDDAP server
2. __station-name__: The name of the station to be displayed in the dashboard
3. __data-provider__: The organization that provides the data
4. __past_days__: The number of days of data to retrieve
5. __data_variables__: Each data variable to be displayed. The varaible name from the ERDDAP dataset sould be used.

__Example JSON File__:
~~~json
"erddap-id": "morro-bay-bs1",
	"station-name": "BS Station - Morro Bay",
	"data-provider": "Cal Poly SLO",
	"past_days": 14,
	"data_variables": [
		{
			"var-id": "sea_water_temperature",
			"short_name":"Temperature",
			"units":"°C",
			"running_mean": "True",
			"ylims":[12,22]
			
		},
~~~

### `get_dashboard_data.py` ###

Create a `StationData` objct by passing the path to the JSON file. The `StationData` object will retrieve the data from the ERDDAP server and store it in a `pandas.DataFrame`. 

Data can be exported as a JSON file using the `write_JSON()` class method and can be copied to the websever by using `copy_to_web = True` parameter of the `write_JSON()` method.

### Deploying to the website ###
On `concave` the package is installed at: `/home/pdaniel/python_modules/oyster-dashboard`

To get the latest version pull the main branch down from git, using `git pull`.

### Install to Python virtual environment ###
Activate the virtual environment using:
`source ~/.virtualenvs/dashboard-cron/bin/activate`

While in the project directory, install package using:
`python setup.py develop`

With the `develop` tag when the files get updated in the package, the changes should persist in the virtual environment.

### Running the Script ###
On `concave`, scripts and parameter files for each station can be found at `/home/pdaniel/static-dashboards/`.

Example Script:
```python
#!/home/pdaniel/.virtualenvs/dashboard-cron/bin/python3
import os
import static_dashboard.get_dashboard_data

if __name__ == "__main__":
	BASE_DIR = "/home/pdaniel/static-dashboards"
	param_fname = os.path.join(BASE_DIR, "parameter_files/bs-SLO-params.json")
	stationData = static_dashboard.get_dashboard_data.StationData(param_fname)
	stationData.write_JSON(out_dir="/home/pdaniel/static-dashboards/dynamic_json", copy_to_web=True) 
```

The python script is then added to a shell scipt called: `run-static-dashboard.sh` that runs each of scipts for each station.

## Plotting on the Website ##
Plot are made using [μPlot](https://github.com/leeoniya/uPlot), a ligthweight Javasccript plotting library.

For each station, a station specific `.js` file should be created that lives in the `/var/www/html/wp-content/themes/cencoos/js/bs1-morro-plot.js` on Skyrocket8.

The baisics of the plotting scipt is that it loads the JSON file and creates a `<div>` element and plot for each data variable. Since `fetch()` is an asynchronous request, this is done in the promises `.then()` method.

## Linking up with Wordpress ##
Injecting custom Javascript in wordpress can be a bit daunting, but isn't too challenging. Style and script files should be copied into the theme folder `\wp-content\theme\cencoos\`.

With the theme folder, you can add custom scripts and stylesheets to the `functions.php` file. __Use Caution!__ Syntax errors here can break the website. If you are unsure make a copy of the file before making changes, but __don't store unused copies here after you are done__. 

For each site you will need to make a function that looks something like this:

```php
function enque_dashboard_bs1() {
	# These files are loaded loaded right before the closing of the </body> tag using enqueing
		if ( is_page( array(2691) ) ) {
			wp_enqueue_style( 'uplot-style', get_stylesheet_directory_uri() . '/js/pckgs/uPlot.min.css', array(), null );
			wp_enqueue_script('uplot',get_stylesheet_directory_uri() . '/js/pckgs/uPlot.iife.min.js', true);
			wp_enqueue_script('bs1-dashboard',get_stylesheet_directory_uri() . '/js/bs1-morro-plot.js', true);
		}
}

add_action( 'wp_enqueue_scripts', 'enque_dashboard_bs1' );
```

The `is_page()` function takes an array of page IDs that the script should be loaded on. The page ID can be found by editing the page and looking at the URL. For example, the page ID for the Morro Bay Dashboard is __2691__. You can also use the page name, but since the ID is immutable, I would recommend using that instead.

The basic idea is that if the page matcheds the page id, then it will load in the style (css) and scipts (.js) at the top of file before any other scripts are loaded.

If you need to load the script after other scripts or html elements are made you need to use a dependenccy hook. [See the shore station map](https://www.cencoos.org/data/Website%20How%20Tos/Shore-Station-Map-How-To.pdf) for an example.

## Creating a Page in Wordpress ##
There are a couple of html tags that you need to add to a new page. Since the code uses `bootstrap` to format the plots, you need to create a container for the plots. Then a row that will contains a message for the reader. Here is an example:

```html
<div class="container">
    <div class="row">

        Data are updated every hour. Click and drag to zoom. <strong>Double-click to reset the zoom.</strong>
        <strong>If data looks out-of-date, refresh the page to reset the cache.</strong>

        <div class="plots"><!-- Generate divs dynamically in JS file --></div>
    </div>
</div>
```

### Finding the page ID ###
When you are editing the page, look at the URL. The ID will be in the URL.
![page id](/docs/page_id.png)

### Other things ###
If you use the no-sidebar template the site looks much nicer:
![template](/docs/full_width.png)



---
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

from static_dashboard.get_dashboard_data import StationData
import unittest

class TestLoadMethods(unittest.TestCase):

    def test_load_parameters(self):
        station_data = StationData("./tests/bs1-morro-params.json")
        msg = "Unable to load station parameter data"
        self.assertEqual (station_data.params['erddap-id'], "morro-bay-bs1", msg=msg)

    def test_url_builder(self):
        station_data = StationData("./tests/bm-morro-params.json")
        msg = "Unable to build station parameter data"
        url = "http://erddap.cencoos.org/erddap/tabledap/edu_calpoly_marine_morro.csvp?time%2Cmass_concentration_of_chlorophyll_in_sea_water%2Cmass_concentration_of_oxygen_in_sea_water%2Cfractional_saturation_of_oxygen_in_sea_water%2Csea_water_practical_salinity%2Csea_water_temperature%2Csea_water_turbidity%2Csea_water_ph_reported_on_total_scale_internal&time>now-7days"
        self.assertEqual (station_data.build_url(), url, msg=msg)
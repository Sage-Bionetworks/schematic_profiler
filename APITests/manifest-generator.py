
from utils import get_input_token, cal_time_api_call, record_run_time_result
import requests

EXAMPLE_SCHEMA_URL = "https://raw.githubusercontent.com/Sage-Bionetworks/schematic/develop/tests/data/example.model.jsonld"
HTAN_SCHEMA_URL = "https://raw.githubusercontent.com/ncihtan/data-models/main/HTAN.model.jsonld"
DATA_FLOW_SCHEMA_URL = "https://raw.githubusercontent.com/Sage-Bionetworks/data_flow/main/inst/data_flow_component.jsonld"
CONCURRENT_THREADS = 1

base_url = "https://schematic-dev.api.sagebionetworks.org/v1/manifest/generate"



class GenerateExampleManifest():
    def __init__(self): 
        self.base_url = EXAMPLE_SCHEMA_URL
        self.use_annotation = False
        self.token = get_input_token()
        self.title = "example"
        self.data_type = ["Patient"]

        # organize parameter for generating an example manifeset
        self.params = {
            "schema_url": self.base_url,
            "title": self.title,
            "data_type": self.data_type, 
            "use_annotations": False,
            "input_token":self.token,
        }
    
    def generate_new_manifest_example_model(self):
        """
        Generate a new manifest as a google sheet by using the example data model 
        """
        try: 
            # send request and calculate run time
            dt_string, time_diff, status_code_dict = cal_time_api_call(base_url, self.params, CONCURRENT_THREADS)
        except: 
            print('there is an exception')

        df = record_run_time_result("manifest/generate", dt_string, "Generating a manifest as a google sheet by using the example data model", 
                                    time_diff, CONCURRENT_THREADS, status_code_dict)
        

    def generate_new_manifest_example_model_excel(self):
        """
        Generate a new manifest as an excel spreadsheet by using the example data model 
        """
        params = self.params
        params["output"] = "excel"
        try: 
            # send request and calculate run time
            dt_string, time_diff, status_code_dict = cal_time_api_call(base_url, params, CONCURRENT_THREADS)
        except: 
            print('there is an exception')

        df = record_run_time_result("manifest/generate", dt_string, "Generating a manifest as an excel spreadsheet by using the example data model", 
                                    time_diff, CONCURRENT_THREADS, status_code_dict)


gm = GenerateExampleManifest()
gm.generate_new_manifest_example_model()
gm.generate_new_manifest_example_model_excel()


        


    





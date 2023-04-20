from utils import get_input_token, cal_time_api_call, record_run_time_result

EXAMPLE_SCHEMA_URL = "https://raw.githubusercontent.com/Sage-Bionetworks/schematic/develop/tests/data/example.model.jsonld"
HTAN_SCHEMA_URL = (
    "https://raw.githubusercontent.com/ncihtan/data-models/main/HTAN.model.jsonld"
)

DATA_FLOW_SCHEMA_URL = "https://raw.githubusercontent.com/Sage-Bionetworks/data_flow/main/inst/data_flow_component.jsonld"
CONCURRENT_THREADS = 1

base_url = "https://schematic-dev.api.sagebionetworks.org/v1/manifest/generate"


class GenerateExampleManifest:
    def __init__(self, url):
        self.schema_url = url
        self.use_annotation = False
        self.token = get_input_token()
        self.title = "example"
        self.data_type = ["Patient"]

        # organize parameter for generating an example manifeset
        self.params = {
            "schema_url": self.schema_url,
            "title": self.title,
            "data_type": self.data_type,
            "use_annotations": False,
            "input_token": self.token,
        }

    def send_request(self):
        """
        sending requests to manifest/generate endpoint
        Return:
            dt_string: start time of running the API endpoints.
            time_diff: time of finish running all requests.
            all_status_code: dict; a dictionary that records the status code of run.
        """
        try:
            # send request and calculate run time
            dt_string, time_diff, status_code_dict = cal_time_api_call(
                base_url, self.params, CONCURRENT_THREADS
            )
        # TO DO: add more details about raising different exception
        # Should exception based on response type?
        except Exception as err:
            print(f"Unexpected {err=}, {type(err)=}")
            raise
        return dt_string, time_diff, status_code_dict

    def record_runtime(
        self,
        endpoint_name,
        dt_string,
        description,
        time_diff,
        CONCURRENT_THREADS,
        status_code_dict,
    ):
        """
        record run time of API endpoints and upload the result as a CSV to synapse
        Args:
            endpoint_name: Name of endpoint (manifest/generate)
            dt_string: start time of running the API endpoints.
            description: description of the test
            time_diff: latency of finishing running the API endpoint
            concurrent_threads: Number of concurrent threads (defined as a global variable)
            status_code_dict: status_code_dict: dictionary; dictionary of status code
        """
        record_run_time_result(
            endpoint_name,
            dt_string,
            description,
            time_diff,
            CONCURRENT_THREADS,
            status_code_dict,
        )

    def generate_new_manifest_example_model(self):
        """
        Generate a new manifest as a google sheet by using the example data model
        """
        dt_string, time_diff, status_code_dict = self.send_request()

        self.record_runtime(
            "manifest/generate",
            dt_string,
            "Generating a manifest as a google sheet by using the example data model",
            time_diff,
            CONCURRENT_THREADS,
            status_code_dict,
        )

    def generate_new_manifest_example_model_excel(self, output_format):
        """
        Generate a new manifest as an excel spreadsheet by using the example data model
        Args:
            output_format: specify the output of manifest. For this function, the output_format is excel
        """
        params = self.params
        params["output"] = output_format

        dt_string, time_diff, status_code_dict = self.send_request()

        self.record_runtime(
            "manifest/generate",
            dt_string,
            "Generating a manifest as an excel spreadsheet by using the example data model",
            time_diff,
            CONCURRENT_THREADS,
            status_code_dict,
        )

    def generate_new_manifest_HTAN_google_sheet(self):
        """
        Generate a new manifest as a google sheet by using the HTAN manifest
        """
        dt_string, time_diff, status_code_dict = self.send_request()

        self.record_runtime(
            "manifest/generate",
            dt_string,
            "Generating a manifest as a google spreadsheet by using the HTAN data model",
            time_diff,
            CONCURRENT_THREADS,
            status_code_dict,
        )

    def generate_existing_manifest_google_sheet(self):
        """
        Generate a new manifest as a google sheet by using the existing manifest
        """
        params = self.params
        params["dataset_id"] = "syn51078367"
        params["asset_view"] = "syn23643253"

        dt_string, time_diff, status_code_dict = self.send_request()

        self.record_runtime(
            "manifest/generate",
            dt_string,
            "Generating an existing manifest as a google sheet by using the example data model",
            time_diff,
            CONCURRENT_THREADS,
            status_code_dict,
        )


gm_example = GenerateExampleManifest(EXAMPLE_SCHEMA_URL)
gm_example.generate_existing_manifest_google_sheet()
gm_example.generate_new_manifest_example_model()
gm_example.generate_new_manifest_example_model_excel("excel")

gm_htan = GenerateExampleManifest(HTAN_SCHEMA_URL)
gm_htan.generate_new_manifest_HTAN_google_sheet()

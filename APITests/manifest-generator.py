from APITests.utils import get_input_token, record_run_time_result, send_request
from APITests.utils import HTAN_SCHEMA_URL, EXAMPLE_SCHEMA_URL, BASE_URL

CONCURRENT_THREADS = 1
base_url = f"{BASE_URL}/manifest/generate"


class GenerateExampleManifest:
    def __init__(self, url):
        self.schema_url = url
        self.use_annotation = False
        self.token = get_input_token()
        self.title = "example"
        self.data_type = "Patient"  # TO DO: add other data types

        # organize parameter for generating an example manifeset
        self.params = {
            "schema_url": self.schema_url,
            "title": self.title,
            "data_type": self.data_type,
            "use_annotations": False,
            "input_token": self.token,
        }

    def generate_new_manifest_example_model(self):
        """
        Generate a new manifest as a google sheet by using the example data model
        """
        dt_string, time_diff, status_code_dict = send_request(
            base_url, self.params, CONCURRENT_THREADS
        )

        record_run_time_result(
            endpoint_name="manifest/generate",
            description="Generating a manifest as a google sheet by using the example data model",
            data_schema="example data schema",
            data_type=self.data_type,
            output_format="google sheet",
            dt_string=dt_string,
            num_concurrent=CONCURRENT_THREADS,
            latency=time_diff,
            status_code_dict=status_code_dict,
        )

    def generate_new_manifest_example_model_excel(self, output_format: str):
        """
        Generate a new manifest as an excel spreadsheet by using the example data model
        Args:
            output_format: specify the output of manifest. For this function, the output_format is excel
        """
        params = self.params
        params["output"] = output_format

        dt_string, time_diff, status_code_dict = send_request(
            base_url, self.params, CONCURRENT_THREADS
        )

        record_run_time_result(
            endpoint_name="manifest/generate",
            description="Generating a manifest as an excel spreadsheet  by using the example data model",
            data_schema="example data schema",
            data_type=self.data_type,
            output_format="excel",
            dt_string=dt_string,
            num_concurrent=CONCURRENT_THREADS,
            latency=time_diff,
            status_code_dict=status_code_dict,
        )

    def generate_new_manifest_HTAN_google_sheet(self):
        """
        Generate a new manifest as a google sheet by using the HTAN manifest
        """
        dt_string, time_diff, status_code_dict = send_request(
            base_url, self.params, CONCURRENT_THREADS
        )

        record_run_time_result(
            endpoint_name="manifest/generate",
            description="Generating a manifest as a google spreadsheet by using the HTAN data model",
            data_schema="HTAN data schema",
            data_type=self.data_type,
            output_format="google sheet",
            dt_string=dt_string,
            num_concurrent=CONCURRENT_THREADS,
            latency=time_diff,
            status_code_dict=status_code_dict,
        )

    def generate_existing_manifest_google_sheet(self):
        """
        Generate a new manifest as a google sheet by using the existing manifest
        """
        params = self.params
        params["dataset_id"] = "syn51078367"
        params["asset_view"] = "syn23643253"

        dt_string, time_diff, status_code_dict = send_request(
            base_url, self.params, CONCURRENT_THREADS
        )

        record_run_time_result(
            endpoint_name="manifest/generate",
            description="Generating an existing manifest as a google sheet by using the example data model",
            data_schema="example data schema",
            num_rows=542,  # number of rows of the existing manifest
            data_type=self.data_type,
            output_format="google sheet",
            dt_string=dt_string,
            num_concurrent=CONCURRENT_THREADS,
            latency=time_diff,
            status_code_dict=status_code_dict,
        )


gm_example = GenerateExampleManifest(EXAMPLE_SCHEMA_URL)
gm_example.generate_new_manifest_example_model()
gm_example.generate_new_manifest_example_model_excel("excel")
gm_example.generate_existing_manifest_google_sheet()

gm_htan = GenerateExampleManifest(HTAN_SCHEMA_URL)
gm_htan.generate_new_manifest_HTAN_google_sheet()

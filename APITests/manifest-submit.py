from utils import (
    get_input_token,
    record_run_time_result,
    send_example_patient_manifest,
    send_post_request,
)
from utils import HTAN_SCHEMA_URL, EXAMPLE_SCHEMA_URL, BASE_URL
import time

CONCURRENT_THREADS = 1
base_url = f"{BASE_URL}/model/submit"


class ManifestSubmit:
    def __init__(self, url):
        self.schema_url = url
        self.dataset_id = "syn51376664"
        self.token = get_input_token()
        self.asset_view = "syn51376649"

        # organize parameters for submitting a manifest
        self.params = {
            "schema_url": self.schema_url,
            "dataset_id": self.dataset_id,
            "asset_view": self.asset_view,
            "input_token": self.token,
        }

    def submit_example_manifeset_patient_as_table_and_file(self):
        """
        submitting an example data manifest
        """
        params = self.params
        # update parameter.
        params["table_manipulation"] = "replace"
        params["restrict_rules"] = False
        params["use_schema_label"] = True

        # try submitting a manifest with and without validation and with different record type
        data_type_lst = ["Patient", None]
        record_type_lst = ["table_and_file", "file_only"]
        for opt in data_type_lst:
            for record_type in record_type_lst:
                params["data_type"] = opt
                params["manifest_record_type"] = record_type

                dt_string, time_diff, status_code_dict = send_post_request(
                    params, base_url, CONCURRENT_THREADS, send_example_patient_manifest
                )

                record_run_time_result(
                    "model/submit",
                    dt_string,
                    f"Submitting an example patient manifest as {record_type} with validation set to {opt}. The manifest has 600 rows.",
                    time_diff,
                    CONCURRENT_THREADS,
                    status_code_dict,
                )
                time.sleep(2)


sm_example_manifest = ManifestSubmit(EXAMPLE_SCHEMA_URL)
sm_example_manifest.submit_example_manifeset_patient_as_table_and_file()

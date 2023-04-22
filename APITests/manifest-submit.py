import time
import requests
from utils import (
    get_input_token,
    record_run_time_result,
    send_example_patient_manifest,
    send_post_request,
)
from utils import DATA_FLOW_SCHEMA_URL, EXAMPLE_SCHEMA_URL, BASE_URL

CONCURRENT_THREADS = 1
base_url = f"{BASE_URL}/model/submit"


class ManifestSubmit:
    def __init__(self, url):
        self.schema_url = url
        self.dataset_id = "syn51376664"
        self.token = get_input_token()
        self.asset_view = "syn51376649"
        self.restrict_rules = False  # TO DO: consider restrict_rules = True?
        self.use_schema_label = True

        # organize parameters for submitting a manifest
        self.params = {
            "schema_url": self.schema_url,
            "dataset_id": self.dataset_id,
            "asset_view": self.asset_view,
            "restrict_rules": self.restrict_rules,
            "use_schema_label": self.use_schema_label,
            "input_token": self.token,
        }

    @staticmethod
    def send_HTAN_dataflow_manifest(url: str, params: dict):
        """
        sending an example dataflow manifest for HTAN
        Args:
            url: url of endpoint
            params: a dictionary of parameters specified by the users
        """
        return requests.post(
            url,
            params=params,
            files={
                "file_name": open(
                    "test_manifests/synapse_storage_manifest_dataflow.csv", "rb"
                )
            },
        )

    @staticmethod
    def execute_manifest_submission(
        data_type_lst: list,
        record_type_lst: list,
        params: dict,
        description: str,
        manifest_to_send_func,
    ):
        """
        Submitting a manifest with different parameters set by users and record latency
        Args:
            data_type_lst: a list of data type
            record_type_lst: a list of record s
            params: a dictionary of parameters specified by the users
            description: a short description of what the submission is. I.E. submitting XX manifest as
            manifest_to_send_func: a function that sends a post request that upload a manifest to be sent
        """
        for opt in data_type_lst:
            for record_type in record_type_lst:
                params["data_type"] = opt
                params["manifest_record_type"] = record_type

                dt_string, time_diff, status_code_dict = send_post_request(
                    params, base_url, CONCURRENT_THREADS, manifest_to_send_func
                )

                if opt:
                    validate_setting = True
                else:
                    validate_setting = False

                record_run_time_result(
                    "model/submit",
                    dt_string,
                    f"{description} {record_type} with validation set to {validate_setting}. The manifest has 600 rows.",
                    time_diff,
                    CONCURRENT_THREADS,
                    status_code_dict,
                )
                time.sleep(2)

    def submit_example_manifeset_patient(self):
        """
        submitting an example data manifest
        """
        params = self.params
        # update parameter.
        params["table_manipulation"] = "replace"
        data_type_lst = ["Patient"]
        record_type_lst = ["table_and_file"]

        description = "Submitting an example manifest as"
        self.execute_manifest_submission(
            data_type_lst,
            record_type_lst,
            params,
            description,
            send_example_patient_manifest,
        )

    def submit_dataflow_manifest_HTAN(self):
        params = self.params
        # update parameter.
        params["table_manipulation"] = "replace"

        # update parameter
        data_type_lst = ["Dataflow"]
        record_type_lst = ["table_and_file"]
        description = "Submitting a dataflow manifest for HTAN as"

        self.execute_manifest_submission(
            data_type_lst,
            record_type_lst,
            params,
            description,
            self.send_HTAN_dataflow_manifest(base_url, params),
        )


sm_example_manifest = ManifestSubmit(EXAMPLE_SCHEMA_URL)
sm_example_manifest.submit_example_manifeset_patient()

sm_dataflow_manifest = ManifestSubmit(DATA_FLOW_SCHEMA_URL)
sm_dataflow_manifest.submit_dataflow_manifest_HTAN()

import os
import time
from dataclasses import dataclass
from typing import Callable

import requests
from requests import Response

from utils import (
    BASE_URL,
    DATA_FLOW_SCHEMA_URL,
    EXAMPLE_SCHEMA_URL,
    get_access_token,
    record_run_time_result,
    send_example_patient_manifest,
    send_post_request,
)

CONCURRENT_THREADS = 1
base_url = f"{BASE_URL}/model/submit"


@dataclass
class ManifestSubmit:
    url: str
    dataset_id: str = "syn51376664"
    token: str = get_access_token()
    asset_view: str = "syn51376649"
    restrict_rules: bool = False
    use_schema_label: bool = True

    def __post_init__(self):
        self.params = {
            "schema_url": self.url,
            "dataset_id": self.dataset_id,
            "asset_view": self.asset_view,
            "restrict_rules": self.restrict_rules,
            "use_schema_label": self.use_schema_label,
            "access_token": self.token,
        }

    @staticmethod
    def send_HTAN_dataflow_manifest(url: str, params: dict) -> Response:
        """
        sending an example dataflow manifest for HTAN
        Args:
            url: url of endpoint
            params: a dictionary of parameters specified by the users
        """
        wd = os.getcwd()
        test_manifest_path = os.path.join(
            wd, "test_manifests/synapse_storage_manifest_dataflow.csv"
        )
        return requests.post(
            url,
            params=params,
            files={"file_name": open(test_manifest_path, "rb")},
        )

    @staticmethod
    def execute_manifest_submission(
        data_type_lst: list,
        record_type_lst: list,
        params: dict,
        description: str,
        manifest_to_send_func: Callable[[str, dict], Response],
    ):
        """
        Submitting a manifest with different parameters set by users and record latency
        Args:
            data_type_lst (list): a list of data type
            record_type_lst (list): a list of record s
            params (dict): a dictionary of parameters specified by the users
            description (str): a short description of what the submission is. I.E. submitting XX manifest as
            manifest_to_send_func (Callable): a function that sends a post request that upload a manifest to be sent
        """
        for opt in data_type_lst:
            for record_type in record_type_lst:
                params["data_type"] = opt
                params["manifest_record_type"] = record_type

                dt_string, time_diff, status_code_dict = send_post_request(
                    base_url, params, CONCURRENT_THREADS, manifest_to_send_func
                )

                if opt:
                    validate_setting = True
                else:
                    validate_setting = False

                if "example" in description:
                    data_schema = "example data schema"
                    # TO DO: added way to automatically calculate the number of rows
                    num_rows = 600
                elif "dataflow" in description:
                    data_schema = "Data flow schema"
                    num_rows = 30
                else:
                    data_schema = None

                record_run_time_result(
                    endpoint_name="model/submit",
                    description=f"{description} {record_type} with validation set to {validate_setting}. The manifest has {num_rows} rows.",
                    data_schema=data_schema,
                    num_rows=num_rows,  # number of rows of manifest being submitted
                    data_type=params["data_type"],
                    restrict_rules=False,  # restrict_rules # TO DO: add restrict_rules = True?
                    dt_string=dt_string,
                    manifest_record_type=params["manifest_record_type"],
                    num_concurrent=CONCURRENT_THREADS,
                    latency=time_diff,
                    status_code_dict=status_code_dict,
                )
                time.sleep(2)

    def submit_example_manifeset_patient(self):
        """
        submitting an example data manifest
        """
        params = self.params
        # update parameter.
        params["table_manipulation"] = "replace"
        data_type_lst = ["Patient", None]
        record_type_lst = ["table_and_file", "file_only"]

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
        data_type_lst = ["DataFlow", None]
        record_type_lst = ["file_only"]
        description = "Submitting a dataflow manifest for HTAN as"

        self.execute_manifest_submission(
            data_type_lst,
            record_type_lst,
            params,
            description,
            self.send_HTAN_dataflow_manifest,
        )


sm_example_manifest = ManifestSubmit(EXAMPLE_SCHEMA_URL)
sm_example_manifest.submit_example_manifeset_patient()

sm_dataflow_manifest = ManifestSubmit(DATA_FLOW_SCHEMA_URL)
sm_dataflow_manifest.submit_dataflow_manifest_HTAN()

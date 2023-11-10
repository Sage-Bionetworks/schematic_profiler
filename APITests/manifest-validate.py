import os
from dataclasses import dataclass

import requests
from requests import Response

# import from internal package
from utils import (
    BASE_URL,
    EXAMPLE_SCHEMA_URL,
    HTAN_SCHEMA_URL,
    record_run_time_result,
    send_example_patient_manifest,
    send_post_request,
    get_access_token,
)

CONCURRENT_THREADS = 2

base_url = f"{BASE_URL}/model/validate"


@dataclass
class ManifestValidate:
    url: str
    token: str = get_access_token()

    def __post_init__(self):
        self.params: dict = {
            "schema_url": self.url,
        }
        self.headers = {"Authorization": f"Bearer {self.token}"}

    @staticmethod
    def send_HTAN_biospecimen_manifest_to_validate(url: str, params: dict) -> Response:
        """
        sending a HTAN biospecimen manifest to validate
        Args:
            url (str): schematic validation endpoint
            params (dict): a dictionary of parameters defined in schematic used by validation

        Returns:
            a response object
        """
        wd = os.getcwd()
        test_manifest_path = os.path.join(
            wd, "APITests/test_manifests/synapse_storage_manifest_HTAN_HMS.csv"
        )
        return requests.post(
            url,
            params=params,
            files={"file_name": open(test_manifest_path, "rb")},
        )

    def validate_example_data_manifest(self):
        """
        validating an example data manifest
        """
        params = self.params
        # update parameter. For this example, validate a Patient manifest
        params["data_type"] = "Patient"

        restrict_rules_opt = [True, False]
        # calculate latency of running /model/validate with different parameters
        for opt in restrict_rules_opt:
            params["restrict_rules"] = opt

            dt_string, time_diff, status_code_dict = send_post_request(
                base_url, params, CONCURRENT_THREADS, send_example_patient_manifest
            )

            record_run_time_result(
                endpoint_name="model/validate",
                description=f"Validate an example data model using the patient component with restrict_rules set to {opt}. The manifest has 600 rows.",
                data_schema="example data schema",
                num_rows=600,  # number of rows of the manifest being validated
                data_type=params["data_type"],
                restrict_rules=opt,
                dt_string=dt_string,
                num_concurrent=CONCURRENT_THREADS,
                latency=time_diff,
                status_code_dict=status_code_dict,
            )

    def validate_HTAN_data_manifest(self):
        """
        validating a HTAN manifest
        """
        params = self.params
        # update parameter. For this example, validate a Biospecimen manifest
        params["data_type"] = "Biospecimen"

        dt_string, time_diff, status_code_dict = send_post_request(
            base_url, params, CONCURRENT_THREADS, send_example_patient_manifest
        )

        record_run_time_result(
            endpoint_name="model/validate",
            description="Validate a HTAN data model using the biospecimen component with restrict_rules set to False. The manifest has around 700 rows.",
            data_schema="HTAN data schema",
            num_rows=773,  # number of rows of the manifest being validated
            data_type=params["data_type"],  # data type
            restrict_rules=False,  # Restrict rules is set to False
            dt_string=dt_string,
            num_concurrent=CONCURRENT_THREADS,
            latency=time_diff,
            status_code_dict=status_code_dict,
        )


vm_example_manifest = ManifestValidate(EXAMPLE_SCHEMA_URL)
vm_example_manifest.validate_example_data_manifest()

vm_htan_manifest = ManifestValidate(HTAN_SCHEMA_URL)
vm_htan_manifest.validate_HTAN_data_manifest()

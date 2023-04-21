import requests
from utils import (
    record_run_time_result,
    send_example_patient_manifest,
    send_post_request,
)
from utils import HTAN_SCHEMA_URL, EXAMPLE_SCHEMA_URL, BASE_URL

CONCURRENT_THREADS = 2

base_url = f"{BASE_URL}/model/validate"


class ValidateManifest:
    def __init__(self, url: str):
        self.schema_url = url

        # organize parameter for generating an example manifeset
        self.params = {
            "schema_url": self.schema_url,
        }

    @staticmethod
    def send_HTAN_biospecimen_manifest_to_validate(url: str, params: dict):
        """
        sending a HTAN biospecimen manifest to validate
        """
        return requests.post(
            url,
            params=params,
            files={
                "file_name": open(
                    "test_manifests/synapse_storage_manifest_HTAN_HMS.csv", "rb"
                )
            },
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
                params, base_url, CONCURRENT_THREADS, send_example_patient_manifest
            )

            record_run_time_result(
                "model/validate",
                dt_string,
                f"Validate an example data model using the patient component with restrict_rules set to {opt}. The manifest has 600 rows.",
                time_diff,
                CONCURRENT_THREADS,
                status_code_dict,
            )

    def validate_HTAN_data_manifest(self):
        """
        validating a HTAN manifest
        """
        params = self.params
        # update parameter. For this example, validate a Biospecimen manifest
        params["data_type"] = "Biospecimen"

        dt_string, time_diff, status_code_dict = send_post_request(
            params, base_url, CONCURRENT_THREADS, send_example_patient_manifest
        )

        record_run_time_result(
            "model/validate",
            dt_string,
            f"Validate a HTAN data model using the biospecimen component with restrict_rules set to False. The manifest has around 700 rows.",
            time_diff,
            CONCURRENT_THREADS,
            status_code_dict,
        )


vm_example_manifest = ValidateManifest(EXAMPLE_SCHEMA_URL)
vm_example_manifest.validate_example_data_manifest()

vm_htan_manifest = ValidateManifest(HTAN_SCHEMA_URL)
vm_htan_manifest.validate_HTAN_data_manifest()

import requests
from utils import cal_time_api_call_post_request, record_run_time_result

EXAMPLE_SCHEMA_URL = "https://raw.githubusercontent.com/Sage-Bionetworks/schematic/develop/tests/data/example.model.jsonld"
HTAN_SCHEMA_URL = (
    "https://raw.githubusercontent.com/ncihtan/data-models/main/HTAN.model.jsonld"
)
CONCURRENT_THREADS = 2

base_url = "https://schematic-dev.api.sagebionetworks.org/v1/model/validate"


class ValidateManifest:
    def __init__(self, url: str):
        self.schema_url = url

        # organize parameter for generating an example manifeset
        self.params = {
            "schema_url": self.schema_url,
        }

    @staticmethod
    def send_example_patient_manifest_to_validate(url: str, params: dict):
        """
        sending an example patient manifest to validate
        """
        return requests.post(
            url,
            params=params,
            files={
                "file_name": open(
                    "test_manifests/synapse_storage_manifest_patient.csv", "rb"
                )
            },
        )

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

    def send_post_request(self, manifest_to_validate_funct):
        """
        sending post requests to manifest/validate endpoint
        Args:
            manifest_to_validate_funct: a function; a function call that determines
        Return:
            dt_string: start time of running the API endpoints.
            time_diff: time of finish running all requests.
            all_status_code: dict; a dictionary that records the status code of run.
        """
        try:
            # send request and calculate run time
            dt_string, time_diff, status_code_dict = cal_time_api_call_post_request(
                base_url, self.params, CONCURRENT_THREADS, manifest_to_validate_funct
            )
        # TO DO: add more details about raising different exception
        # Should exception based on response type?
        except Exception as err:
            print(f"Unexpected {err=}, {type(err)=}")
            raise
        return dt_string, time_diff, status_code_dict

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

            dt_string, time_diff, status_code_dict = self.send_post_request(
                self.send_example_patient_manifest_to_validate
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

        dt_string, time_diff, status_code_dict = self.send_post_request(
            self.send_HTAN_biospecimen_manifest_to_validate
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
vm_example_manifest.validate_HTAN_data_manifest()

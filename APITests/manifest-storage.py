from utils import (
    get_input_token,
    cal_time_api_call,
    record_run_time_result,
    send_request,
)
from utils import BASE_URL

CONCURRENT_THREADS = 1


class ManifestStorageAPI:
    def __init__(self):
        self.token = get_input_token()
        self.params = {"input_token": self.token}

    def retrieve_asset_view_as_json(self):
        """
        Retrieve asset view table as a dataframe.
        """
        # define base_url
        base_url = f"{BASE_URL}/storage/assets/tables"
        # define the asset view to retrieve
        asset_view = "syn23643253"
        params = self.params
        params["asset_view"] = asset_view

        # calculate latency for different return type
        # TO DO: add csv
        params["return_type"] = "json"
        dt_string, time_diff, status_code_dict = send_request(
            base_url, params, CONCURRENT_THREADS
        )

        record_run_time_result(
            endpoint_name="storage/assets/tables",
            description=f"Retrieve asset view {asset_view} as a json",
            dt_string=dt_string,
            num_concurrent=CONCURRENT_THREADS,
            latency=time_diff,
            status_code_dict=status_code_dict,
        )

    def retrieve_project_datasets(self):
        """
        Retrieve all datasets under a given project
        """
        # define base_url
        base_url = f"{BASE_URL}/storage/project/datasets"

        # define the asset view to retrieve
        params = self.params
        asset_view = "syn23643253"
        project_id = "syn26251192"
        params["asset_view"] = asset_view
        params["project_id"] = project_id

        dt_string, time_diff, status_code_dict = send_request(
            base_url, params, CONCURRENT_THREADS
        )

        record_run_time_result(
            endpoint_name="storage/project/datasets",
            description=f"Retrieve all datasets under project {project_id} in asset view {asset_view} as a json",
            dt_string=dt_string,
            num_concurrent=CONCURRENT_THREADS,
            latency=time_diff,
            status_code_dict=status_code_dict,
        )


manifest_storage_class = ManifestStorageAPI()
manifest_storage_class.retrieve_asset_view_as_json()
manifest_storage_class.retrieve_project_datasets()

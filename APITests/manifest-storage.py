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
            params, base_url, CONCURRENT_THREADS
        )

        record_run_time_result(
            "storage/assets/tables",
            dt_string,
            f"Retrieve asset view {asset_view} as a json",
            time_diff,
            CONCURRENT_THREADS,
            status_code_dict,
        )


manifest_storage_class = ManifestStorageAPI()
manifest_storage_class.retrieve_asset_view_as_json()

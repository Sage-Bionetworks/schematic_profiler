from dataclasses import dataclass
from typing import Tuple
import logging
from utils import (
    Row,
    BASE_URL,
    StoreRuntime,
    send_request,
    save_run_time_result,
)

CONCURRENT_THREADS = 1

logger = logging.getLogger("manifest-storage")


@dataclass
class ManifestStorage:
    token: str = StoreRuntime.get_access_token()

    def __post_init__(self):
        self.params = {}
        self.headers = {"Authorization": f"Bearer {self.token}"}


class RetrieveAssetView(ManifestStorage):
    def retrieve_asset_view_as_json(self) -> Row:
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
            base_url, params, CONCURRENT_THREADS, headers=self.headers
        )

        return save_run_time_result(
            endpoint_name="storage/assets/tables",
            description=f"Retrieve asset view {asset_view} as a json",
            asset_view=asset_view,
            dt_string=dt_string,
            num_concurrent=CONCURRENT_THREADS,
            latency=time_diff,
            status_code_dict=status_code_dict,
        )


class RestrieveProjectDataset(ManifestStorage):
    def retrieve_project_dataset_api_call(
        self, project_id: str, asset_view: str
    ) -> Row:
        """
        Make the API calls to retrieve all datasets from a given project
        Args:
            project_id: ID of a storage project.
            asset_view: ID of view listing all project data assets.
        """
        base_url = f"{BASE_URL}/storage/project/datasets"
        params = self.params

        # update parameter
        params["asset_view"] = asset_view
        params["project_id"] = project_id

        dt_string, time_diff, status_code_dict = send_request(
            base_url, params, CONCURRENT_THREADS, headers=self.headers
        )

        return save_run_time_result(
            endpoint_name="storage/project/datasets",
            description=f"Retrieve all datasets under project {project_id} in asset view {asset_view} as a json",
            dt_string=dt_string,
            asset_view=asset_view,
            num_concurrent=CONCURRENT_THREADS,
            latency=time_diff,
            status_code_dict=status_code_dict,
        )

    def retrieve_project_datasets_test(self) -> Row:
        """
        Retrieve all datasets under a given example project
        """
        # define the asset view to retrieve
        asset_view = "syn23643253"
        project_id = "syn26251192"

        return self.retrieve_project_dataset_api_call(project_id, asset_view)

    def retrieve_project_datasets_HTAN(self) -> Row:
        """
        Retrieve all datasets under a given testing HTAN project (used by DCA)
        """
        # define the asset view to retrieve
        asset_view = "syn20446927"  # htan asset view
        project_id = "syn32596076"  # htan center c

        return self.retrieve_project_dataset_api_call(project_id, asset_view)


def monitor_manifest_storage() -> Tuple[Row, Row, Row]:
    logger.info("Monitoring storage endpoints")
    retrieve_asset_view_class = RetrieveAssetView()
    row_one = retrieve_asset_view_class.retrieve_asset_view_as_json()

    retrieve_project_dataset = RestrieveProjectDataset()
    row_two = retrieve_project_dataset.retrieve_project_datasets_test()
    row_three = retrieve_project_dataset.retrieve_project_datasets_HTAN()

    return row_one, row_two, row_three


monitor_manifest_storage()

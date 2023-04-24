import os
import time
import pytz
import logging
from datetime import datetime
import concurrent.futures
from concurrent.futures import ThreadPoolExecutor
import requests
from requests.exceptions import InvalidSchema
import pandas as pd
import synapseclient
from synapseclient import Table

logging.basicConfig(
    format=("%(levelname)s: [%(asctime)s] %(name)s" " - %(message)s"),
    level=logging.WARNING,
    datefmt="%Y-%m-%d %H:%M:%S",
)
logging.getLogger("utils").setLevel(logging.INFO)
logger = logging.getLogger("utils")


# define variables that will be used across scripts
EXAMPLE_SCHEMA_URL = "https://raw.githubusercontent.com/Sage-Bionetworks/schematic/develop/tests/data/example.model.jsonld"
HTAN_SCHEMA_URL = (
    "https://raw.githubusercontent.com/ncihtan/data-models/main/HTAN.model.jsonld"
)

DATA_FLOW_SCHEMA_URL = "https://raw.githubusercontent.com/Sage-Bionetworks/data_flow/main/inst/data_flow_component.jsonld"
BASE_URL = "https://schematic-dev.api.sagebionetworks.org/v1"


def fetch(url: str, params: dict):
    """
    Trigger a get request
    Args:
        url: the url to run a given api request
        params: parameter of running a given api request
    """
    return requests.get(url, params=params)


def send_example_patient_manifest(url: str, params: dict):
    """
    sending an example patient manifest
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


def send_post_request(
    base_url: str, params: dict, concurrent_threads: int, manifest_to_send_func
):
    """
    sending post requests
    Args:
        params: a dictionary of parameters to send
        base_url: url of endpoint
        concurrent_threads: number of concurrent threads
        manifest_to_send_func: a function that sends a post request that upload a manifest to be sent
    Return:
        dt_string: start time of running the API endpoints.
        time_diff: time of finish running all requests.
        all_status_code: dict; a dictionary that records the status code of run.
    """
    try:
        # send request and calculate run time
        dt_string, time_diff, status_code_dict = cal_time_api_call_post_request(
            base_url, params, concurrent_threads, manifest_to_send_func
        )
    # TO DO: add more details about raising different exception
    # Should exception based on response type?
    except Exception as err:
        print(f"Unexpected {err=}, {type(err)=}")
        raise
    return dt_string, time_diff, status_code_dict


def send_request(base_url: str, params: dict, concurrent_threads: int):
    """
    sending requests to manifest/generate endpoint
    Args:
        params: a dictionary of parameters to send
        base_url: url of endpoint
        concurrent_threads: number of concurrent threads
    Return:
        dt_string: start time of running the API endpoints.
        time_diff: time of finish running all requests.
        all_status_code: dict; a dictionary that records the status code of run.
    """
    try:
        # send request and calculate run time
        dt_string, time_diff, status_code_dict = cal_time_api_call(
            base_url, params, concurrent_threads
        )
    # TO DO: add more details about raising different exception
    # Should exception based on response type?
    except Exception as err:
        print(f"Unexpected {err=}, {type(err)=}")
        raise
    return dt_string, time_diff, status_code_dict


def return_time_now(name_funct_call=None) -> str:
    """
    Get the time now
    Args:
        name_funct_call: name of function call
    return: current time formatted as "%d/%m/%Y %H:%M:%S" as a string
    """
    now = datetime.now(pytz.timezone("US/Eastern"))
    dt_string = now.strftime("%d/%m/%Y %H:%M:%S")

    if name_funct_call:
        logger.info(
            f"when running {name_funct_call} function, the time is: {dt_string}"
        )

    return dt_string


def get_input_token() -> str:
    """
    Get access token to use asset store resources
    return: a token to access asset store
    """
    # for running on github action
    if "SYNAPSE_AUTH_TOKEN" in os.environ:
        token = os.environ["SYNAPSE_AUTH_TOKEN"]
        logger.debug("Successfully found synapse access token")
    else:
        token = os.environ["TOKEN"]
    if token is None or "":
        logger.error("Synapse access token is not found")

    return token


def login_synapse():
    """
    Login to synapse using the token provided
    return: synapse object
    """
    token = get_input_token()
    try:
        syn = synapseclient.Synapse()

        # syn.default_headers["Authorization"] = f"Bearer {token}"
        syn.login(rememberMe=True)
    except (
        synapseclient.core.exceptions.SynapseNoCredentialsError,
        synapseclient.core.exceptions.SynapseHTTPError,
    ) as e:
        raise e
    return syn


def cal_time_api_call(url: str, params: dict, concurrent_threads: int):
    """
    calculate the latency of api calls.
    Args:
        url: str; the url that users want to access
        params: dict; the parameters need to use for the request
        concurrent_thread: integer; number of concurrent threads requested by users
    return:
        dt_string: start time of running the API endpoints.
        time_diff: time of finish running all requests.
        all_status_code: dict; a dictionary that records the status code of run.
    """
    start_time = time.time()
    # get time of running the api endpoint
    dt_string = return_time_now()

    # execute concurrent requests
    with ThreadPoolExecutor() as executor:
        futures = [
            executor.submit(fetch, url, params) for x in range(concurrent_threads)
        ]
        all_status_code = {"200": 0, "500": 0, "503": 0, "504": 0}
        for f in concurrent.futures.as_completed(futures):
            try:
                status_code = f.result().status_code
                status_code_str = str(status_code)
                if status_code_str != "200":
                    logger.error(f"Error running: {url} using params {params}")
                all_status_code[status_code_str] = all_status_code[status_code_str] + 1
            except InvalidSchema:
                raise InvalidSchema(
                    f"No connection adapters were found for {url}. Please make sure that your URL is correct. "
                )

    time_diff = round(time.time() - start_time, 2)
    logger.info(f"duration time of running {url}: {time_diff}")
    return dt_string, time_diff, all_status_code


def cal_time_api_call_post_request(
    url: str, params: dict, concurrent_threads: int, manifest_to_send_func
):
    """
    calculate the latency of api calls.
    Args:
        url: str; the url that users want to access
        params: dict; the parameters need to use for the request
        concurrent_threads: integer; number of concurrent threads requested by users
        manifest_to_send_func: a function that sends a post request that upload a manifest to be sent
    return:
        dt_string: start time of running the API endpoints.
        time_diff: time of finish running all requests.
        all_status_code: dict; a dictionary that records the status code of run.
    """
    start_time = time.time()
    # get time of running the api endpoint
    dt_string = return_time_now()

    # execute concurrent requests
    with ThreadPoolExecutor() as executor:
        futures = [
            executor.submit(manifest_to_send_func, url, params)
            for x in range(concurrent_threads)
        ]
        all_status_code = {"200": 0, "500": 0, "503": 0, "504": 0}
        for f in concurrent.futures.as_completed(futures):
            try:
                status_code = f.result().status_code
                status_code_str = str(status_code)
                if status_code_str != "200":
                    logger.error(
                        f"Encountered error {status_code_str} while running: {url} using params {params}"
                    )
                all_status_code[status_code_str] = all_status_code[status_code_str] + 1
            except InvalidSchema:
                raise InvalidSchema(
                    f"No connection adapters were found for {url}. Please make sure that your URL is correct. "
                )

    time_diff = round(time.time() - start_time, 2)
    logger.info(f"duration time of running {url}: {time_diff}")
    return dt_string, time_diff, all_status_code


def record_run_time_result(
    endpoint_name: str,
    description: str,
    dt_string: str,
    num_concurrent: int,
    latency: float,
    status_code_dict: dict,
    data_schema: str = None,
    num_rows: int = None,
    data_type: str = None,
    output_format: str = None,
    restrict_rules: bool = None,
    manifest_record_type: str = None,
):
    """
    Record the result of running an endpoint as a dataframe
    Args:
    Required params:
    endpoint_name: str; name of the endpoint being run
    description: str; more details description of the case being run
    num_concurrent: integer; number of concurrent requests
    latency: double; latency of finishing the run
    status_code_dict: dictionary; dictionary of status code

    Optional params:
    data_schema: str; the data schema used by the function
    num_rows: int; number of rows of a given manifest
    data_type: str; data type/component being used
    output_format: str; output format of a given manifest
    restrict_rules: bool; if restrict_rules parameter gets set to true
    dt_string: str; start time of the test
    manifest_record_type: Manifest storage type. Four options: file only, file+entities, table+file, table+file+entities

    return:
    a dataframe that record results of the run time
    """
    # for debugging github action
    return_time_now("Record run time")

    # get specific number of status code
    num_status_200 = status_code_dict["200"]
    num_status_500 = status_code_dict["500"]
    num_status_504 = status_code_dict["504"]
    num_status_503 = status_code_dict["503"]

    # Load existing data from synapse
    syn = login_synapse()

    # get existing table from synapse
    existing_table_schema = syn.get("syn51385540")
    new_row = [
        [
            endpoint_name,
            description,
            data_schema,
            num_rows,
            data_type,
            output_format,
            restrict_rules,
            dt_string,
            manifest_record_type,
            num_concurrent,
            latency,
            num_status_200,
            num_status_500,
            num_status_504,
            num_status_503,
        ]
    ]

    # add new row to table
    table = syn.store(Table(existing_table_schema, new_row))

    logger.info("Finish uploading result to synapse. ")

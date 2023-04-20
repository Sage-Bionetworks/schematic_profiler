import os
import time
import pytz
import logging
from datetime import datetime
import concurrent.futures
from concurrent.futures import ThreadPoolExecutor
import requests
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


def fetch(url: str, params: dict):
    """
    Trigger a get request
    Args:
        url: the url to run a given api request
        params: parameter of running a given api request
    """
    return requests.get(url, params=params)


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
            except Exception as exc:
                logger.error(f"generated an exception:{exc}")

    time_diff = round(time.time() - start_time, 2)
    logger.info(f"duration time of running {url}: {time_diff}")
    return dt_string, time_diff, all_status_code


def record_run_time_result(
    endpoint_name, dt_string, description, latency, num_concurrent, status_code_dict
):
    """
    Record the result of running an endpoint as a dataframe
    Args:
    endpoint_name: str; name of the endpoint being run.
    dt_string: str; start time of the test
    description: str; more details description of the case being run
    latency: number; latency of finishing the run
    num_concurrent: integer; number of concurrent requests
    status_code_dict: dictionary; dictionary of status code

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
    existing_table_schema = syn.get("syn51365205")
    new_row = [
        [
            endpoint_name,
            description,
            dt_string,
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

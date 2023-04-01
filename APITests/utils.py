import os
import time
import logging
from datetime import datetime
import concurrent.futures
from concurrent.futures import ThreadPoolExecutor
import requests
import pandas as pd
import synapseclient
from synapseclient import File

logger = logging.getLogger(__name__)
logger = logging.getLogger("api")


def fetch(url: str, params: dict):
    """
    Trigger a get request
    Args:
        url: the url to run a given api request
        params: parameter of running a given api request
    """
    return requests.get(url, params=params)


def get_input_token() -> str:
    """
    Get access token to use asset store resources
    return: a token to access asset store
    """
    # for running on github action
    if "SYNAPSE_ACCESS_TOKEN" in os.environ:
        token = os.environ["SYNAPSE_ACCESS_TOKEN"]
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
        syn.default_headers["Authorization"] = f"Bearer {token}"
        syn.login(sessionToken=token, silent=True)
    except synapseclient.core.exceptions.SynapseHTTPError:
        raise ValueError(
            "No access to resources. Please make sure that your token is correct"
        )
    return syn


def cal_time_api_call(url: str, params: dict, concurrent_threads: int):
    """
    calculate the latency of api calls.
    Args:
        url: str; the url that users want to access
        params: dict; the parameters need to use for the request
        concurrent_thread: integer; number of concurrent threads requested by users
    return:
        time_diff: time of finish running all
        all_status_code: dict; a dictionary that records the status code of run.
    """
    start_time = time.time()
    # get time of running the api endpoint
    now = datetime.now()
    dt_string = now.strftime("%d/%m/%Y %H:%M:%S")

    # execute concurrent requests
    with ThreadPoolExecutor() as executor:
        futures = [
            executor.submit(fetch, url, params) for x in range(concurrent_threads)
        ]
        all_status_code = {"200": 0, "500": 0, "503": 0, "504": 0}
        for f in concurrent.futures.as_completed(futures):
            try:
                status_code = f.result().status_code
                logger.debug("Status code", status_code)
                status_code_str = str(status_code)
                all_status_code[status_code_str] = all_status_code[status_code_str] + 1
            except Exception as exc:
                logger.error(f"generated an exception:{exc}")

    time_diff = round(time.time() - start_time, 2)
    logger.info(f"duration time of running {url}", time_diff)
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
    # get specific number of status code
    num_status_200 = status_code_dict["200"]
    num_status_500 = status_code_dict["500"]
    num_status_504 = status_code_dict["504"]
    num_status_503 = status_code_dict["503"]

    # create a dataframe
    row = {
        "Endpoint": endpoint_name,
        "Description": description,
        "Test start time": dt_string,
        "Number of concurrent request": num_concurrent,
        "Latency": latency,
        "200": num_status_200,
        "500": num_status_500,
        "504": num_status_504,
        "503": num_status_503,
    }
    df_new_latency = pd.DataFrame(row, index=[0])

    # Load existing data from synapse
    syn = login_synapse()
    # download the latest file from synapse
    file_info = syn.get("syn51277112", downloadFile=True)
    file_path = file_info["path"]

    # read the current csv
    df_existing_latency = pd.read_csv(file_path, header=0)

    # update dataframe
    df_latest_latency = df_existing_latency.append(df_new_latency)

    upload_result_to_synapse(df_latest_latency, syn)

    return df_latest_latency


def upload_result_to_synapse(df, syn):
    """
    Update a dataframe to synapse as a csv file
    Args:
    df: dataframe to upload
    syn: synapse obj
    """

    # save dataframe to a csv
    df.to_csv("latency.csv", index=False, header=True)

    # upload to synapse
    test_entity = File(
        "latency.csv", description="Schematic api latency test", parent="syn51277111"
    )
    syn.store(test_entity)

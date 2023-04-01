import os
import synapseclient


## TO DO: will delete this
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
        print("error!!! no token was found")

    return token


def login_synapse():
    """
    Login to synapse using the token provided
    return: synapse object
    """
    token = get_input_token()
    try:
        syn = synapseclient.Synapse()
        syn.login(authToken=token, rememberMe=True)
    except synapseclient.core.exceptions.SynapseNoCredentialsError:
        raise ValueError("No synapse token found. ")
    except synapseclient.core.exceptions.SynapseHTTPError:
        raise ValueError("Please make sure you are logged into synapse.org.")
    return syn

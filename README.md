# Schematic profiler

Schematic profiler was created for developers in FAIR data team to measure performance of schematic API endpoints. For more context, please visit the jira page [here](https://sagebionetworks.jira.com/wiki/spaces/~392696258/pages/2894757895/Monitoring+schematic+APIs). See code reference [here](https://sage-bionetworks.github.io/schematic_profiler/)

## When to use schematic profiler?
Schematic profiler is primarily used for measuring the performance of endpoints after schematic dev deployment and ensure the code that we added do not significantly increase latency. Please DO NOT run schematic profiler on staging and prod. In addition, by modifying the `BASE_URL` variable in `APITests/utils.py` and `CONCURRENT_THREADS` variable in the beginning of individual test file, you could effectively send concurrent requests to either local schematic APIs or AWS schematic dev instance.

Note: schematic profiler does not check if the outputs returned are desirable. This code base focuses only on performance of the endpoints.

## How to run schematic profiler?
For running schematic profiler locally:
* step 1: Clone schematic profiler repository
* step 2: Check out the develop branch
* step 3: Save your synapse access token in `.synapseConfig` as an environment variable by running: `export TOKEN=YOUR SYNAPSE ACCESS TOKEN`
* step 4: Run individual python files after `cd APITests`. For example, for testing /manifest/generate endpoints, please run: `python3 manifest-generator.py`. If one test does not return 200, schematic profiler would print out the parameters being used for that test for you to reproduce this issue.
* step 5: View results and report issues. All the outputs are automatically saved in a synapse table [here](https://www.synapse.org/#!Synapse:syn51385540/tables/query/eyJzcWwiOiJTRUxFQ1QgKiBGUk9NIHN5bjUxMzg1NTQwIiwgImluY2x1ZGVFbnRpdHlFdGFnIjp0cnVlLCAib2Zmc2V0IjoyMjUsICJsaW1pdCI6MjV9). If the result is 5xx, please first try reproducing the errors using the same parameters that schematic profiler was using manually and then try reproducing the errors using `develop` branch of schematic library. Try to figure out if the errors are related to running schematic profiler or the errors are related to schematic/schematic API infrastructure. If it is a schematic related issue, please open a ticket and report to the team. If it is a profiler issue, please inform the team and see if other team members could reproduce the issue and open a ticket if needed.

For running schematic profiler remotely: please feel free to use the github action [here](https://github.com/Sage-Bionetworks/schematic_profiler/actions/workflows/workflow.yml).

For getting started, I would recommmend running schematic profiler locally because if you run into a 500/504/503 error, schematic profiler would print out the combination of parameters that is causing the error.

## How to contribute
This repo uses pre-commit hook. Please install pre-commit by following the guide [here](https://pre-commit.com/)

All the packages can be found in `requirements.txt`. Please create your own virtual environment and install packages listed there.

The tests in schematic profiler are organized by endpoints. If you want to add new tests for a new endpoint, please create a separate test file and modify `workflow.yml` to include the test. If you want to add test cases for existing endpoints, please feel free to add tests there.

## Current use cases covered by schematic profiler
| Endpoints | Use cases |
| --- | --- |
| manifest/generate | Generate a new manifest as a google sheet by using the example data model |
| manifest/generate | Generate a new manifest as an excel spreadsheet by using the example data model |
| manifest/generate | Generate a new manifest as a google sheet by using the HTAN manifest|
| manifest/generate | Generate a manifest as a google sheet by using an existing patient manifest |
| /storage/assets/table | Retrieve asset view table (see here) as a data frame |
| /storage/project/datasets | Retrieve all datasets in HTAN center C using HTAN file view |
| /storage/project/datasets | Retrieve all datasets under a given example project|
| /model/submit | While replacing the existing record, submitting an example patient manifest in CSV format as a table and a file or simply as a file with or without validation. |
| /model/submit | While replacing the existing record, submitting a data flow manifest in CSV format as a table and a file or simply as a file with or without validation.  |
| /model/validate | Validate a HTAN biospecimen manifest with around 770 rows with great expectation rules enabled.   |
| /model/validate | Validate an example manifest that has around 600 rows with or without great expectation rules enabled. |

## 🚨 Potential issues
You might run into issues because schema urls are outdated or example manifests are out dated. If that's the case, please feel free to open a Jira issue or message me on slack.

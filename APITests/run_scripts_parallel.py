import concurrent.futures
from manifest_validate import monitor_manifest_validator
from manifest_submit import monitor_manifest_submission
from manifest_storage import monitor_manifest_storage
from manifest_generator import monitor_manifest_generator
from utils import StoreRuntime


if __name__ == "__main__":
    all_rows_to_insert = []
    with concurrent.futures.ThreadPoolExecutor(max_workers=4) as e:
        funcs = (
            monitor_manifest_storage,
            monitor_manifest_generator,
            monitor_manifest_submission,
            monitor_manifest_validator,
        )
        futures = [e.submit(func) for func in funcs]

        for f in concurrent.futures.as_completed(futures):
            row_list = f.result()

            # save results to a new list
            for row in row_list:
                if isinstance(row, list) and row not in all_rows_to_insert:
                    all_rows_to_insert.append(row)
                else:
                    print(f"can not insert {row}")
    # store results on synapse
    srt = StoreRuntime()
    srt.record_run_time_result_synapse(rows=all_rows_to_insert)

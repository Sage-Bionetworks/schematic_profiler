import multiprocessing
import subprocess


def run_script(script):
    # Execute the script
    subprocess.run(["python3", script])


if __name__ == "__main__":
    scripts = [
        "manifest-validate.py",
        "manifest-storage.py",
        "manifest-submit.py",
        "manifest-generator.py",
    ]

    # Create a multiprocessing pool
    pool = multiprocessing.Pool(processes=len(scripts))

    # Run scripts in parallel
    pool.map(run_script, scripts)

    # Close the pool
    pool.close()
    pool.join()

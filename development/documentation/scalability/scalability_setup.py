import subprocess
from pathlib import Path


def main():
    """Run the scalability exercise.

    Define the model, a list with different number of threads and a maximum number of
    function evaluations.

    """
    model = "kw_data_one"
    maxfun = 1

    filepath = Path(__file__).resolve().parent / "run_single_scalability_exercise.py"

    # Run Python
    for num_thread in [1, 2, 4, 6, 8, 10]:
        subprocess.check_call(
            ["python", str(filepath), model, str(maxfun), "0", str(num_thread)]
        )


if __name__ == "__main__":
    main()

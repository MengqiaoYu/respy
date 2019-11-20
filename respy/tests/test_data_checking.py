import pytest

import respy as rp
from respy.config import EXAMPLE_MODELS
from respy.pre_processing.data_checking import check_simulated_data
from respy.pre_processing.model_processing import process_params_and_options
from respy.tests.utils import process_model_or_seed


@pytest.mark.parametrize("model_or_seed", EXAMPLE_MODELS)
def test_simulated_data(model_or_seed):
    """Test simulated data with ``check_simulated_data``.

    Note that, ``check_estimation_data`` is also tested in this function as these tests
    focus on a subset of the data.

    """
    params, options = process_model_or_seed(model_or_seed)

    options["n_periods"] = 5

    simulate = rp.get_simulate_func(params, options)
    df = simulate(params)

    optim_paras, _ = process_params_and_options(params, options)
    check_simulated_data(optim_paras, df)

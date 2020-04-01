"""
This module contains tests for felx choices!
"""
import numpy as np
import pandas as pd
import respy as rp
import itertools
import copy

from respy.pre_processing.model_processing import process_params_and_options
from respy.state_space import _create_core_and_indexer, create_sp
from respy.pre_processing.process_covariates import separate_covariates_into_core_dense_mixed



def test_period_choice_dense_cores():
    """
    Basic first test!
    """
    # Load model.
    params, options = rp.get_example_model("robinson_crusoe_extended", with_data=False)

    # Extend with observable characteristic.
    params.loc[("observable_health_well", "probability"), "value"] = 0.9
    params.loc[("observable_health_sick", "probability"), "value"] = 0.1

    # Sick people can never work.
    options["inadmissible_choices"] = {
        "fishing": ["health == 1"],
    }
    # Create internal specification objects.
    optim_paras, options = process_params_and_options(params, options)

    sp = create_sp(options, optim_paras)
    check = sp.period_choice_cores

    for x in check[(1,)].keys():
        assert x[1] == (False, True, True)

    for x in check[(0,)].keys():
        assert x[1] == (True, True, True)
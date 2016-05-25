""" The tests in this module compare the RESPY package to the original
RESTUD code for the special cases where they overlap.
"""

# standard library
from pandas.util.testing import assert_frame_equal

import pandas as pd
import numpy as np

import subprocess
import pytest

# project library
from codes.random_init import generate_random_dict

from respy.python.shared.shared_auxiliary import dist_class_attributes
from respy.python.shared.shared_auxiliary import print_init_dict
from respy.python.shared.shared_constants import FORTRAN_DIR

from respy.solve import solve

from respy import RespyCls
from respy import simulate


def transform_respy_to_restud(model_paras, edu_start, edu_max, num_agents_sim,
        num_periods, num_draws_emax, delta):
    """ Transform a RESPY initialization file to a RESTUD file.
    """
    # Ensure restrictions
    assert (edu_start == 10)
    assert (edu_max == 20)

    # Write to initialization file
    with open('in.txt', 'w') as file_:

        # Write out some basic information about the problem.
        file_.write(' {0:03d} {1:05d} {2:06d} {3:06f}'
            ' {4:06f}\n'.format(num_periods, num_agents_sim, num_draws_emax,
            -99.0, 500.0))

        # Write out coefficients for the two occupations.
        coeffs_a, coeffs_b = model_paras['coeffs_a'], model_paras['coeffs_b']
        for coeffs in [coeffs_a, coeffs_b]:
            line = ' {0:10.6f} {1:10.6f} {2:10.6f} {3:10.6f}  {4:10.6f}' \
                    ' {5:10.6f}\n'.format(*coeffs)
            file_.write(line)

        # Write out coefficients for education and home payoffs as well as
        # the discount factor. The intercept is scaled. This is later undone
        # again in the original FORTRAN code.
        coeffs_edu = model_paras['coeffs_edu']
        coeffs_home = model_paras['coeffs_home']

        edu_int = coeffs_edu[0] / 1000
        edu_coeffs = [edu_int]
        home = coeffs_home[0] / 1000
        for j in range(2):
            edu_coeffs += [-coeffs_edu[j + 1] / 1000]
        coeffs = edu_coeffs + [home, delta]
        fmt = ' {0:10.6f} {1:10.6f} {2:10.6f} {3:10.6f} {4:10.6f}\n'
        line = fmt.format(*coeffs)
        file_.write(line)

        # Write out coefficients of correlation and standard deviations in the
        # standard deviations in the education and home equation required.
        # This is undone again in the original FORTRAN code. All this is
        # working only under the imposed absence of any randomness.
        rho, shocks_cov = np.zeros((4, 4)), np.zeros((4, 4))
        for j in range(4):
            line = ' {0:10.5f} {1:10.5f} {2:10.5f} ' \
                   ' {3:10.5f}\n'.format(*rho[j, :])
            file_.write(line)
        file_.write(line)


@pytest.mark.usefixtures('fresh_directory', 'set_seed')
class TestClass(object):
    """ This class groups together some tests.
    """
    def test_1(self):
        """  Compare results from the RESTUD program and the RESPY package.
        """
        # Impose some constraints on the initialization file which ensures that
        # the problem can be solved by the RESTUD code. The code is adjusted to
        # run with zero draws.
        constraints = dict()
        constraints['edu'] = (10, 20)
        constraints['is_deterministic'] = True

        # Generate random initialization file. The RESTUD code uses the same
        # random draws for the solution and simulation of the model. Thus,
        # the number of draws is required to be less or equal to the number
        # of agents.
        init_dict = generate_random_dict(constraints)

        num_agents_sim = init_dict['SIMULATION']['agents']
        num_draws_emax = init_dict['SOLUTION']['draws']
        if num_draws_emax < num_agents_sim:
            init_dict['SOLUTION']['draws'] = num_agents_sim

        print_init_dict(init_dict)

        # Indicate RESTUD code the special case of zero disturbance.
        open('.restud.testing.scratch', 'a').close()

        # Perform toolbox actions
        respy_obj = RespyCls('test.respy.ini')

        # This flag aligns the random components between the RESTUD program and
        # RESPY package. The existence of the file leads to the RESTUD program
        # to write out the random components.
        model_paras, edu_start, edu_max, num_agents_sim, num_periods, \
            num_draws_emax, delta = \
                dist_class_attributes(respy_obj,
                    'model_paras', 'edu_start', 'edu_max', 'num_agents_sim',
                    'num_periods', 'num_draws_emax', 'delta')

        transform_respy_to_restud(model_paras, edu_start, edu_max,
            num_agents_sim, num_periods, num_draws_emax, delta)

        # Solve model using RESTUD code.
        cmd = FORTRAN_DIR + '/bin/kw_dp3asim'
        subprocess.call(cmd, shell=True)

        # Solve model using RESPY package.
        solve(respy_obj)
        simulate(respy_obj)

        # Compare the simulated datasets generated by the programs.
        py = pd.DataFrame(np.array(np.genfromtxt('data.respy.dat',
                missing_values='.'), ndmin=2)[:, -4:])

        fort = pd.DataFrame(np.array(np.genfromtxt('ftest.txt',
                missing_values='.'), ndmin=2)[:, -4:])

        assert_frame_equal(py, fort)

""" This modules contains the tests for the continuous integration efforts.
"""

# standard library
import numpy as np
import shutil
import glob
import sys
import os

# project library
from robupy.tests.random_init import generate_init, generate_random_dict
from robupy.tests.random_init import print_random_dict

# module variables
FILE_PATH = os.path.dirname(os.path.realpath(__file__))
TEST_PATH = os.getcwd()

# PYTHONPATH
dir_ = FILE_PATH.replace('/tests', '')
sys.path.insert(0, dir_)

from robupy import read, solve, simulate

''' Test class.
'''


class Tests(object):
    """ Test class.
    """

    @staticmethod
    def setup_class():
        """ Setup before any methods in this class.
        """
        os.chdir(FILE_PATH)

    @staticmethod
    def teardown_class():
        """ Teardown after any methods in this class.
        """
        os.chdir(TEST_PATH)

    def teardown(self):
        """ Teardown after each test method.
        """
        self.cleanup()

    @staticmethod
    def setup():
        """ Setup before each test method.
        """

    @staticmethod
    def cleanup():
        """ Cleanup after test battery.
        '"""
        files = []

        files = files + glob.glob('*.robupy.*')

        files = files + glob.glob('*.ini')

        files = files + glob.glob('*.pkl')

        files = files + glob.glob('*.txt')

        files = files + glob.glob('*.dat')

        for file_ in files:

            try:

                os.remove(file_)

            except OSError:

                pass

            try:

                shutil.rmtree(file_)

            except OSError:

                pass

    @staticmethod
    def test_1():
        """ Testing whether ten random initialization file can be
        solved and simulated.
        """
        for i in range(10):

            # Generate constraints
            constraints = dict()
            constraints['fast'] = 'False'

            # Generate random initialization file
            generate_init(constraints)

            # Perform toolbox actions
            robupy_obj = read('test.robupy.ini')

            robupy_obj = solve(robupy_obj)

            simulate(robupy_obj)

            # Distribute class attributes
            num_periods = robupy_obj.get_attr('num_periods')

            emax = robupy_obj.get_attr('emax')

            # Check that the expected future value is always
            # zero in the last period.
            assert (np.all(emax[(num_periods - 1), :] == 0.00))

    @staticmethod
    def test_2():
        """ Testing ten admissible realizations of state space
        for the first three periods.
        """
        for i in range(10):

            # Generate constraint periods
            constraints = dict()
            constraints['periods'] = np.random.randint(3, 10)
            constraints['fast'] = 'False'

            # Generate random initialization file
            generate_init(constraints)

            # Perform toolbox actions
            robupy_obj = read('test.robupy.ini')

            robupy_obj = solve(robupy_obj)

            simulate(robupy_obj)

            # Distribute class attributes
            states_number_period = robupy_obj.get_attr('states_number_period')

            states_all = robupy_obj.get_attr('states_all')

            # The next hard-coded results assume that at least two more
            # years of education are admissible.
            edu_max = robupy_obj.get_attr('edu_max')
            edu_start = robupy_obj.get_attr('edu_start')

            if edu_max - edu_start < 2:
                continue

            # The number of admissible states in the first three periods
            for j, number_period in enumerate([1, 4, 13]):
                assert (states_number_period[j] == number_period)

            # The actual realizations of admissible states in period one
            assert ((states_all[0, 0, :] == [0, 0, 0, 1]).all())

            # The actual realizations of admissible states in period two
            states = [[0, 0, 0, 0], [0, 0, 1, 1], [0, 1, 0, 0]]
            states += [[1, 0, 0, 0]]

            for j, state in enumerate(states):
                assert ((states_all[1, j, :] == state).all())

            # The actual realizations of admissible states in period three
            states = [[0, 0, 0, 0], [0, 0, 1, 0], [0, 0, 1, 1]]
            states += [[0, 0, 2, 1], [0, 1, 0, 0], [0, 1, 1, 0]]
            states += [[0, 1, 1, 1], [0, 2, 0, 0], [1, 0, 0, 0]]
            states += [[1, 0, 1, 0], [1, 0, 1, 1], [1, 1, 0, 0]]
            states += [[2, 0, 0, 0]]

            for j, state in enumerate(states):
                assert ((states_all[2, j, :] == state).all())

    @staticmethod
    def test_3():
        """ Testing whether the ex ante and ex post payoffs
        are identical if there is no random variation
        in the payoffs
        """
        for i in range(10):
            # Generate constraint periods
            constraints = dict()
            constraints['eps_zero'] = True
            constraints['fast'] = 'False'
            constraints['level'] = 0.00

            # Generate random initialization file
            generate_init(constraints)

            # Perform toolbox actions
            robupy_obj = read('test.robupy.ini')

            robupy_obj = solve(robupy_obj)

            # Distribute class attributes
            ex_ante = robupy_obj.get_attr('period_payoffs_ex_ante')
            ex_post = robupy_obj.get_attr('period_payoffs_ex_post')

            # Check
            assert (np.ma.all(
                np.ma.masked_invalid(ex_ante) == np.ma.masked_invalid(ex_post)))

    @staticmethod
    def test_4():
        """ If there is no random variation in payoffs
        then the number of draws to simulate the
        expected future value should have no effect.
        """
        # Generate constraints
        constraints = dict()
        constraints['eps_zero'] = True
        constraints['fast'] = 'False'

        # The calculation of the KL does not work for this case.
        constraints['measure'] = 'absolute'

        # Generate random initialization file
        generate_init(constraints)

        # Initialize auxiliary objects
        base = None

        for _ in range(10):

            # Draw a random number of draws for
            # expected future value calculations.
            num_draws = np.random.randint(1, 100)

            # Perform toolbox actions
            robupy_obj = read('test.robupy.ini')

            robupy_obj.unlock()

            robupy_obj.set_attr('num_draws', num_draws)

            robupy_obj.lock()

            robupy_obj = solve(robupy_obj)

            # Distribute class attributes
            emax = robupy_obj.get_attr('emax')

            if base is None:
                base = emax.copy()

            # Statistic
            diff = np.max(abs(np.ma.masked_invalid(base) - np.ma.masked_invalid(
                emax)))

            # Checks
            assert (np.isfinite(diff))
            assert (diff < 10e-10)

    @staticmethod
    def test_5():
        """ Testing whether thousand random initialization file can generated
        and read.
        """
        for i in range(1000):

            # Initialize constraints
            constraints = dict()
            constraints['fast'] = 'False'

            # Generate random initialization file
            generate_init(constraints)

            # Perform toolbox actions
            read('test.robupy.ini')

    @staticmethod
    def test_6():
        """ Testing whether the risk code is identical to the ambiguity code for
            very, very small levels of ambiguity.
        """
        # Generate random initialization dictionary
        constraints = dict()
        constraints['debug'] = 'True'
        constraints['fast'] = 'False'

        init_dict = generate_random_dict(constraints)

        # Initialize containers
        base = None

        # Loop over different uncertain environments.
        for level in [0.00, 0.000000000000001]:

            # Set varying constraints
            init_dict['AMBIGUITY']['level'] = level

            # Print to dictionary
            print_random_dict(init_dict)

            # Perform toolbox actions
            robupy_obj = read('test.robupy.ini')

            robupy_obj = solve(robupy_obj)

            # Distribute class attributes
            emax = robupy_obj.get_attr('emax')

            if base is None:
                base = emax.copy()

            # Checks
            np.testing.assert_allclose(base, emax, rtol=1e-06)

    @staticmethod
    def test_7():
        """ Testing whether the ex ante benefit calculation is unaffected by
        the level of ambiguity.
        """

        # Generate constraints
        constraints = dict()
        constraints['fast'] = 'False'

        # Generate random initialization dictionary
        init_dict = generate_random_dict(constraints)

        # Initialize containers
        base = None

        # Loop over different uncertain environments.
        for _ in range(5):

            # Set varying constraints
            init_dict['AMBIGUITY']['level'] = np.random.choice(
                [0.00, np.random.uniform()])

            # Print to dictionary
            print_random_dict(init_dict)

            # Perform toolbox actions
            robupy_obj = read('test.robupy.ini')

            robupy_obj = solve(robupy_obj)

            # Distribute class attributes
            ex_ante = robupy_obj.get_attr('period_payoffs_ex_ante')

            if base is None:
                base = ex_ante.copy()

            # Checks
            np.testing.assert_allclose(base, ex_ante)

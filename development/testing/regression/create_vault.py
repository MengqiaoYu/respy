#!/usr/bin/env python
""" This script creates and writes to disk a list of the input for numerous
regression tests. These are included in the test infrastructure.
"""

# standard library
import pickle as pkl
import numpy as np

import sys
version = str(sys.version_info[0])

if version == '2':
    sys.path.insert(0, '../../../respy/tests')
    from codes.random_init import generate_init
else:
    from respy.tests.codes.random_init import generate_init


from respy import RespyCls
from respy import simulate
from respy import estimate

num_tests = 500
fname = 'test_vault_' + version + '.respy.pkl'

tests = []
for i in range(num_tests):
    print('\n Creating test ' + str(i))

    constr = dict()
    constr['maxfun'] = int(np.random.choice([0, 1, 2, 3, 5, 6], p=[0.5, 0.1, 0.1, 0.1, 0.1, 0.1]))
    constr['flag_scaling'] = np.random.choice([True, False], p=[0.1, 0.9])

    init_dict = generate_init(constr)

    respy_obj = RespyCls('test.respy.ini')

    simulate(respy_obj)

    crit_val = estimate(respy_obj)[1]

    test = (init_dict, crit_val)

    tests += [test]

    pkl.dump(tests, open(fname, 'wb'))

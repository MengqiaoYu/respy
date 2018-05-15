import atexit
import os

from respy.python.shared.shared_auxiliary import generate_optimizer_options
from respy.python.record.record_estimation import record_estimation_sample
from respy.python.shared.shared_auxiliary import dist_class_attributes
from respy.python.shared.shared_auxiliary import remove_scratch
from respy.python.shared.shared_auxiliary import get_est_info
from respy.python.shared.shared_constants import OPT_EST_FORT
from respy.python.shared.shared_constants import OPT_EST_PYTH
from respy.python.process.process_python import process
from respy.fortran.interface import resfort_interface
from respy.python.interface import respy_interface
from respy.custom_exceptions import UserError

OPTIMIZERS = OPT_EST_FORT + OPT_EST_PYTH


def estimate(respy_obj):
    """ Estimate the model
    """
    # Cleanup
    for fname in ['est.respy.log', 'est.respy.info']:
        if os.path.exists(fname):
            os.unlink(fname)

    if respy_obj.get_attr('is_solved'):
        respy_obj.reset()

    assert check_estimation(respy_obj)

    # This locks the estimation directory for additional estimation requests.
    atexit.register(remove_scratch, '.estimation.respy.scratch')
    open('.estimation.respy.scratch', 'w').close()

    # Read in estimation dataset. It only reads in the number of agents requested for the
    # estimation (or all available, depending on which is less). It allows read in only a subset of
    # the initial conditions.
    data_frame = process(respy_obj)
    record_estimation_sample(data_frame)
    data_array = data_frame.as_matrix()

    # Distribute class attributes
    version = respy_obj.get_attr('version')

    # Select appropriate interface
    if version in ['PYTHON']:
        respy_interface(respy_obj, 'estimate', data_array)
    elif version in ['FORTRAN']:
        resfort_interface(respy_obj, 'estimate', data_array)
    else:
        raise NotImplementedError

    rslt = get_est_info()
    x, val = rslt['paras_step'], rslt['value_step']

    for fname in ['.estimation.respy.scratch', '.stop.respy.scratch']:
        remove_scratch(fname)

    # Finishing
    return x, val


def check_estimation(respy_obj):
    """ Check input arguments.
    """
    # Check that class instance is locked.
    assert respy_obj.get_attr('is_locked')

    # Check that no other estimations are currently running in this directory.
    assert not os.path.exists('.estimation.respy.scratch')

    # Distribute class attributes
    optimizer_options, optimizer_used, optim_paras, version, maxfun, num_paras, file_est = \
        dist_class_attributes(respy_obj, 'optimizer_options', 'optimizer_used', 'optim_paras',
                              'version', 'maxfun', 'num_paras', 'file_est')

    # Ensure that at least one free parameter. It is not enough to check this in the case of at
    # least one function evaluation due to the random sampling of optimizer options in
    # generate_optimizer_options() which requires at least one free parameter.
    if sum(optim_paras['paras_fixed']) == num_paras:
        raise UserError('Estimation requires at least one free parameter')

    # We need to make sure that the estimation dataset is actually present.
    if not os.path.exists(file_est):
        raise UserError('Estimation dataset does not exist')

    if maxfun > 0:
        assert optimizer_used in optimizer_options.keys()

        # We need to make sure that an optimizer that aligns with the requested optimization is
        # requested.
        if version == 'PYTHON':
            assert optimizer_used in OPT_EST_PYTH
        elif version == 'FORTRAN':
            assert optimizer_used in OPT_EST_FORT
        else:
            raise AssertionError

    # We need to make sure that all optimizers are fully defined for the FORTRAN interface. At
    # the same time, we do not want to require the user to specify only the optimizers that are
    # used. So, we sample a full set and replace the optimizers that are used with the user
    # specification.
    full_options = dict()
    for optimizer in OPTIMIZERS:
        full_options[optimizer] = \
            generate_optimizer_options(optimizer, optim_paras, num_paras)

    for optimizer in optimizer_options.keys():
        full_options[optimizer] = optimizer_options[optimizer]

    # Update the enlarged set of optimizer options.
    check_optimizer_options(full_options)

    respy_obj.unlock()
    respy_obj.set_attr('optimizer_options', full_options)
    respy_obj.lock()

    # Finishing
    return respy_obj


def check_optimizer_options(optimizer_options):
    """ This function makes sure that the optimizer options are all valid.
    """
    # POWELL's algorithms
    for optimizer in ['FORT-NEWUOA', 'FORT-BOBYQA']:
        maxfun = optimizer_options[optimizer]['maxfun']
        rhobeg = optimizer_options[optimizer]['rhobeg']
        rhoend = optimizer_options[optimizer]['rhoend']
        npt = optimizer_options[optimizer]['npt']

        for var in [maxfun, npt]:
            assert isinstance(var, int)
            assert (var > 0)
        for var in [rhobeg, rhoend]:
            assert (rhobeg > rhoend)
            assert isinstance(var, float)
            assert (var > 0)

    # FORT-BFGS
    maxiter = optimizer_options['FORT-BFGS']['maxiter']
    stpmx = optimizer_options['FORT-BFGS']['stpmx']
    gtol = optimizer_options['FORT-BFGS']['gtol']
    assert isinstance(maxiter, int)
    assert (maxiter > 0)
    for var in [stpmx, gtol]:
        assert isinstance(var, float)
        assert (var > 0)

    # SCIPY-BFGS
    maxiter = optimizer_options['SCIPY-BFGS']['maxiter']
    gtol = optimizer_options['SCIPY-BFGS']['gtol']
    eps = optimizer_options['SCIPY-BFGS']['eps']
    assert isinstance(maxiter, int)
    assert (maxiter > 0)
    for var in [eps, gtol]:
        assert isinstance(var, float)
        assert (var > 0)

    # SCIPY-LBFGSB
    maxiter = optimizer_options['SCIPY-LBFGSB']['maxiter']
    pgtol = optimizer_options['SCIPY-LBFGSB']['pgtol']
    factr = optimizer_options['SCIPY-LBFGSB']['factr']
    maxls = optimizer_options['SCIPY-LBFGSB']['maxls']
    eps = optimizer_options['SCIPY-LBFGSB']['eps']
    m = optimizer_options['SCIPY-LBFGSB']['m']

    for var in [pgtol, factr, eps]:
        assert isinstance(var, float)
        assert var > 0
    for var in [m, maxiter, maxls]:
        assert isinstance(var, int)
        assert (var >= 0)

    # SCIPY-POWELL
    maxiter = optimizer_options['SCIPY-POWELL']['maxiter']
    maxfun = optimizer_options['SCIPY-POWELL']['maxfun']
    xtol = optimizer_options['SCIPY-POWELL']['xtol']
    ftol = optimizer_options['SCIPY-POWELL']['ftol']
    assert isinstance(maxiter, int)
    assert (maxiter > 0)
    assert isinstance(maxfun, int)
    assert (maxfun > 0)
    assert isinstance(xtol, float)
    assert (xtol > 0)
    assert isinstance(ftol, float)
    assert (ftol > 0)



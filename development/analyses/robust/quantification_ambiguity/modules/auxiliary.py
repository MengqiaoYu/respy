""" This module contains some auxiliary functions helpful in the
quantification of ambiguity.
"""

# standard library
import numpy as np

def distribute_arguments(parser):
    """ Distribute command line arguments.
    """
    # Process command line arguments
    args = parser.parse_args()

    # Extract arguments
    is_recompile = args.is_recompile
    num_procs = args.num_procs
    is_debug = args.is_debug
    levels = args.levels
    spec = args.spec

    # Check arguments
    assert (isinstance(levels, list))
    assert (np.all(levels) >= 0.00)
    assert (is_recompile in [True, False])
    assert (is_debug in [True, False])
    assert (isinstance(num_procs, int))
    assert (num_procs > 0)
    assert (spec in ['one', 'two', 'three'])

    # Finishing
    return levels, is_recompile, is_debug, num_procs, spec
"""
New checks can be written in one of the sub modules of this package. 
Writing new checks in existing modules they will automatically be picked
up by the script. When adding a new sub module it is important the contents 
of the sub module into this one.

.. code-block:: python
    
    from .animation import *

All checks are sorted in order of occurrence in the source code. This can be 
used to make sure certain checks are after others.
"""
import sys
import inspect
from collections import OrderedDict

from .uv import *
from .scene import *
from .rigging import *
from .shaders import *
from .textures import *
from .geometry import *
from .skinning import *
from .modelling import *
from .animation import *
from .renderStats import *
from .renderLayers import *

from .. import collections
from ..utils.qa import QualityAssurance


def getChecks():
    """
    Get all checks available in this module. 

    :return: All available error checks
    :rtype: list
    """
    checks = []

    # get quality assurance checks.
    for name, obj in inspect.getmembers(sys.modules[__name__]):
        if (
            inspect.isclass(obj)
            and issubclass(obj, QualityAssurance)
            and obj.__name__ != QualityAssurance.__name__
        ):

            checks.append(obj())

    # sort checks based on location in source code.
    checks.sort(
        key=lambda x:
            inspect.getsource(
                inspect.getmodule(x)
            ).find(
                x.__class__.__name__
            )
    )

    return checks


def getChecksFromCollection(collection):
    """
    Get all check based on a collections. The collections are stored in the
    collection module, or custom collections made by the user are saved to
    disk.

    :param str collection:
    :return: Ordered dictionary of checks
    :rtype: OrderedDict
    """
    data = getChecksSplitByCategory()

    categories = getChecksCategories()
    categories = collections.getCollections().get(collection) or categories

    return OrderedDict(
        [
            (category, data.get(category))
            for category in categories
            if data.get(category)
        ]
    )


def getChecksSplitByCategory():
    """
    Get all of the checks and split them based on category as defined in the
    classes themselves.

    :return: All error checks split by category
    :rtype: dict
    """
    data = {}

    for check in getChecks():
        for category in check.categories:
            if category not in data.keys():
                data[category] = []

            data[category].append(check)

    return data


def getChecksCategories():
    """
    Get a list of all the categories used.

    :return: Category list
    :rtype: list
    """
    return getChecksSplitByCategory().keys()
"""			
Quality assurance framework for Maya. Focused on many parts of a production 
pipeline, collections are created for animators, modelers, riggers and 
look-dev. 

.. figure:: /_images/qualityAssuranceExample.png
   :align: center

Installation
============
* Extract the content of the .rar file anywhere on disk.
* Drag the qualityAssurance.mel file in Maya to permanently install the script.

Usage
=====
A button on the MiscTools shelf will be created that will allow easy access to
the ui, this way the user doesn't need to worry about any of the code. If user
wishes to not use the shelf button the following commands can be used.

Display UI

.. code-block:: python

    import qualityAssurance.ui
    qualityAssurance.ui.show("rigging")
    
The show function takes in a collection argument, if you work within one of 
the specialties you can simply call the show function with the collection 
you want to see by default. To see all available collections run the following 
code.

.. code-block:: python

    import qualityAssurance.collections
    print qualityAssurance.collections.getCollectionsCategories()

Adding Quality Assurance Checks
===============================

The quality assurance framework is setup so new quality assurance checks can
easily be added.

Location
--------
All quality assurance checks are located in the **checks** folder. New checks 
can be written in one of the sub modules of the **checks** folder. Writing 
new checks in existing modules will automatically be picked up by the script. 
When adding a new sub module it is important to import the contents of the 
sub module into the **__init__.py** file in the **checks** folder.

.. code-block:: python
    
    from .animation import *

All checks are sorted in order of occurrence in the source code. This can be 
used to make sure certain checks are after others.

Collections
-----------
New collections can be added in the **COLLECTIONS** variable. Since this 
**COLLECTIONS** variable is an OrderedDict, it will keep the order. A 
collection can be defined by who will be using it. Currently it is
divided by different specialties. Each specialty contains a list of 
categories that will be displayed. The category names link to the categories
defined in the quality assurance checks themselves. 

Sub Classing
------------
New quality assurance checks can be created by sub classing the 
:class:`qualityAssurance.utils.qa.QualityAssurance` base class. It is important
to extend the class with a **_find** and **_fix** function and update the meta 
data in the **__init__** function.

.. code-block:: python

    from ..utils import QualityAssurance, reference

    class TestCheck(QualityAssurance):
        def __init__(self):
            QualityAssurance.__init__(self)

            self._name = "Unused Animation"
            self._message = "{0} animation curve(s) are unused"
            self._categories = ["Animation"]
            self._selectable = True

        # ------------------------------------------------------------------------

        def _find(self):
            animCurves = self.ls(type="animCurve")
            animCurves = reference.removeReferenced(animCurves)

            for animCurve in animCurves:
                # check if the output plug is connected
                if cmds.listConnections("{0}.output".format(animCurve)):
                    continue

                # yield error
                yield animCurve

        def _fix(self, animCurve):
            cmds.delete(animCurve)
            
Meta Data
^^^^^^^^^
* **self._name:** Name of the quality assurance check
* **self._urgency:** Urgency level, 1=orange, 2=red.
* **self._message:** Format-able message when errors are found.
* **self._categories:** List of categories the quality assurance check should part of.
* **self._selectable:** Boolean value if the error list is selectable.

Find and Fix Function
^^^^^^^^^^^^^^^^^^^^^
* The **_find** function is a generator that yields errors as they get found. 
* The **_fix** function fixes one of these errors at a time. In the example above we could find multiple animation curves, but the fix only deletes one animation curve at a time.

Note
=====
Inspired by Martin Orlowski's **Quality GuAard**, I've decided to write my own 
quality assurance framework and make it freely available. The project is
available on `Git <https://github.com/robertjoosten/maya-quality-assurance>`_.
Free for anybody that wishes to contribute to this tool and add additional 
quality assurance checks. 
"""
__author__ = "Robert Joosten"
__version__ = "0.1.0"
__email__ = "rwm.joosten@gmail.com"

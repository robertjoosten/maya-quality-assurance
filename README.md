# rjQualityAssurance
<img align="right" src="https://github.com/robertjoosten/rjQualityAssurance/blob/master/ui/icons/rjQualityAssurance.png">
Quality assurance framework for Maya. Focused on many parts of a production pipeline, collections are created for animators, modelers, riggers and look-dev. 

<p align="center"><img src="https://github.com/robertjoosten/rjQualityAssurance/raw/master/README.png"></p>

## Installation
Copy the **rjQualityAssurance** folder to your Maya scripts directory:
> C:\Users\<USER>\Documents\maya\scripts

## Usage
Display UI:

```python
import rjQualityAssurance.ui
collection = "rigging"
rjQualityAssurance.ui.show(collection)  
```

## Adding Quality Assurance Checks
The quality assurance framework is setup so new quality assurance checks can easily be added.

### Location
All quality assurance checks live in the **rjQualityAssurance/checks** folder. New checks can be written in one of the sub modules in that folder. Writing new checks in existing modules they will automatically be picked up by the script. When adding a new sub module it is important the contents of the sub module into the following file: **rjQualityAssurance/checks/__init__.py**.

```python
from .animation import *
```

All checks are sorted in order of occurrence in the source code. This can be used to make sure certain checks are after others.

### Collections
New collections can be added in the COLLECTIONS variable. Since this COLLECTIONS variable is an OrderedDict, it will keep the order. A collection can be defined by who will be using it. Currently it is divided by different specialties. Each specialty contains a list of categories that will be displayed. The category names link to the categories defined in the quality assurance checks themselves. 

### Sub Classing
New quality assurance checks can be created by sub classing the **QualityAssurance** base class. It is important to extend the class with a **_find** and **_fix** function and update the meta data in the **__init__** function.

```python
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
```
            
#### Meta Data
* **self._name:** Name of the quality assurance check
* **self._urgency:** Urgency level, 1=orange, 2=red.
* **self._message:** Format-able message when errors are found.
* **self._categories:** List of categories the quality assurance check should part of.
* **self._selectable:** Boolean value if the error list is selectable.

#### Find and Fix Function
* The **_find** function is a generator that yields errors as they get found. 
* The **_fix** function fixes one of these errors at a time. In the example above we could find multiple animation curves, but the fix only deletes one animation curve at a time.

## Note
Inspired by Martin Orlowski Quality GuAard, I've decided to write my own quality assurance framework and make it freely available. The project is available on [Git](https://github.com/robertjoosten/rjQualityAssurance). Free for anybody that wishes to contribute to this tool and add additional quality assurance checks. 
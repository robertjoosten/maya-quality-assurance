from maya import cmds


class UndoContext(object):
    """
    This context will create a undo chunk of every commands that is ran within
    the context.

    .. code-block:: python
    
        with UndoContext:
            # code
    """
    def __enter__(self):
        cmds.undoInfo(openChunk=True)

    def __exit__(self, *exc_info):
        cmds.undoInfo(closeChunk=True)

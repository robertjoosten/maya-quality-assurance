def baseName(name):
    """
    This function will strip the namespaces and grouping information of a name.
    Useful when working with fullPaths but needing the base for naming.

    :param str name:
    :return: Base name of string
    :rtype: str
    """
    return name.split("|")[-1].split(":")[-1]


def rootName(name):
    """
    This function will strip the grouping information of a name.
    Useful when working with fullPaths but needing the base for naming.

    :param str name:
    :return: Root name of string
    :rtype: str
    """
    return name.split("|")[-1]


def namespace(name):
    """
    This function will return the namespace if any of the object

    :param str name:
    :returns: namespace
    :rtype: str/None
    """
    if name.find(":") != -1:
        return name.split("|")[-1].rsplit(":", 1)[0]


# ----------------------------------------------------------------------------


def asFlatList(input):
    """
    Convert the input to a flat list.

    :param input:
    :return: Flattened list
    :rtype: list
    """
    if type(input) != list:
        # return list with input as content
        return [input]

    elif type(input) == list and type(input[0]) == list:
        # if the first element of the list is also a list. loop over the lists
        # within the lists, and extend them into a new list making the return
        # value a combined list.
        content = []
        for i in input:
            content.extend(i)
        return content

    elif type(input) == list:
        # return input value
        return input

    # return empty list
    return []

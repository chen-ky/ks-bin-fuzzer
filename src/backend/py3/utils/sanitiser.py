import string


def sanitise_class_name(class_name: str) -> str:
    """
    Clean provided string to be used as class name. Will remove
    whitespace, punctuations (excluding `_`) and convert the name to 
    titlecase.

    :param class_name: String to sanitise
    :returns: Cleaned string with `_` appended (to prevent Python name
    collision)
    """
    result = class_name.title()
    to_remove_chars = string.punctuation + string.whitespace
    for c in to_remove_chars:
        result = result.replace(c, "")
    result += "_"
    return result


@staticmethod
def sanitise_fn_name(fn_name: str) -> str:
    """
    Clean provided string to be used as function name. Will remove
    whitespace, punctuations (excluding `_`) and convert the name to 
    lowercase.

    :param fn_name: String to sanitise
    :returns: Cleaned string with `_` appended (to prevent Python name
    collision)
    """
    result = fn_name.lower()
    to_remove_chars = string.punctuation.replace(
        "_", "") + string.whitespace
    for c in to_remove_chars:
        result = result.replace(c, "")
    result += "_"
    return result

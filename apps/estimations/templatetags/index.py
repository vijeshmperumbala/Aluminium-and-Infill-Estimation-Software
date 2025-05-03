from django import template
register = template.Library()

@register.filter
def index(indexable, i):
    """
    The function "index" returns the element at the specified index of a given indexable object.
    
    :param indexable: A sequence or collection that can be indexed, such as a list, tuple, or string
    :param i: The index of the element that we want to retrieve from the indexable object
    :return: The function `index` is returning the element of the `indexable` object at the index `i`.
    """
    return indexable[i]
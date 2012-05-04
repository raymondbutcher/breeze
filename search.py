import re

from bson.objectid import InvalidId
from pymongo.objectid import ObjectId


def combine_lookups(operator, *lookups):
    count = len(lookups)
    if count == 0:
        return {}
    elif count == 1:
        return lookups[0]
    else:
        return {operator: lookups}


def exact_match_any_field(phrase, *fields):
    """
    Creates a keyword OR lookup where the exact phrase must be in at least one
    of the specified fields.

    """

    regex = {
        '$regex': re.escape(phrase),
        '$options': 'i',
    }

    lookups = []
    for field in fields:
        lookups.append({field: regex})

    return combine_lookups('$or', *lookups)


def id_search(*object_ids, **kwargs):
    """Creates a lookup for any of the specified object IDs."""

    field = kwargs.get('field', '_id')
    lookups = []
    for object_id in object_ids:
        try:
            object_id = ObjectId(object_id)
        except InvalidId:
            pass
        lookups.append({
            field: object_id
        })
    return combine_lookups('$or', *lookups)


def match_all_words(phrase, *fields):
    """
    Creates a lookup in which all words in the phrase must be found,
    but they can be in any of the specified fields.

    """

    tokens = set(re.sub('  +', ' ', phrase.strip()).split(' '))
    lookups = [exact_match_any_field(token, *fields) for token in tokens if token]
    return combine_lookups('$and', *lookups)

import re


def _match_any_field(term, *fields):
    regex = {
        '$regex': re.escape(term),
        '$options': 'i',
    }
    search = []
    for field in fields:
        search.append({field: regex})
    return {
        '$or': search,
    }


def match_all_words(term, *fields):
    """
    Creates a basic keyword AND search where words can be in any of the
    specified fields.

    """

    tokens = set(re.sub('  +', ' ', term.strip()).split(' '))

    if not tokens:
        return {}

    if len(tokens) == 1:
        return _match_any_field(term, *fields)

    return {
        '$and': [_match_any_field(token, *fields) for token in tokens],
    }

import tornado.gen


def default_label(name):
    return name.capitalize().replace('_', ' ')


def is_engine(func):
    return func.func_code is engine_func_code
engine_func_code = tornado.gen.engine(object).func_code


def unique_items(items):
    seen = set()
    for item in items:
        if item not in seen:
            yield item
            seen.add(item)

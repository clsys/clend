from django.db import connections


def close_old_connections():
    for conn in connections.all():
        conn.close_if_unusable_or_obsolete()


def handle_db_connections(func):
    def func_wrapper():
        close_old_connections()
        result = func()
        close_old_connections()
        return result

    return func_wrapper

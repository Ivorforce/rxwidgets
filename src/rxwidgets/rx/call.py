import reactivex as rx
import reactivex.operators as rxo


def call_latest(*args, **kwargs):
    def map(fn):
        """
        Call the function with the specified args and kwargs.
        Each arg, including fn, must be an observable.
        """
        # Unzip
        kwargs_keys, kwargs_vals = zip(*kwargs.items()) if kwargs else (tuple(), tuple())
        combined_args = [fn, *kwargs_vals, *args]

        def caller(input: tuple):
            iterator = iter(input)

            fun = next(iterator)
            kwargs = dict(zip(kwargs_keys, iterator))

            return fun(*iterator, **kwargs)

        return rxo.map(caller)(rx.combine_latest(*combined_args))

    return map

from functools import wraps



def mostPriests(runs):
    def _outer_wrapper(wrapped_function):
        @wraps(wrapped_function)
        def _wrapper(*args, **kwargs):
            results = []
            for i in range(runs):
                results.append(wrapped_function(*args, **kwargs))

            biggestIndex = 0
            for i in range(1,runs):
                if len(results[i]) > len(results[biggestIndex]):
                    biggestIndex = i

            return results[biggestIndex]

        return _wrapper

    return _outer_wrapper
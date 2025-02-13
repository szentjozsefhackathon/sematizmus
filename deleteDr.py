from functools import wraps


def deleteDr(wrapped_function):
        @wraps(wrapped_function)
        def _wrapper(*args, **kwargs):
            results = wrapped_function(*args, **kwargs)
            drTitles = ["Dr.", "DR.", "dr.", "dR."]
            new_results = []

            for r in results:
                for drt in drTitles:
                    if drt in r["name"]:
                        r["name"] = r["name"].replace(drt, "")
                        r["doctor"] = True
                        break
                    else:
                        r["doctor"] = False
                r["name"] = r["name"].replace(", ", " ").replace("  ", " ").strip()
                r["name"] = (" ".join([t for t in r["name"].split() if t.istitle()])).strip()
                if r["name"] != "": # Van fantomra pelda
                    new_results.append(r)
                
            return new_results


        return _wrapper
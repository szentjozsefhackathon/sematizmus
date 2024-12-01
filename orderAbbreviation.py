from functools import wraps



def orderAbbreviation(wrapped_function):
        @wraps(wrapped_function)
        def _wrapper(*args, **kwargs):
            results = wrapped_function(*args, **kwargs)
            results = [r for r in results if not ("SJ" in r["name"] and not "SJP" in r["name"])]
            new_results = []
            orderAbbreviations = ["SJP", "OFM Conv.", "OSB", "OP", "SDS", "SVD", "FSCB", "OSPPE", "FSO", "SDB", "OCD", "OH", "TORG", "SMC", "OFM", "MI", "CM"]

            for r in results:
                if "O.Praem." in r["name"] or "O.Praem" in r["name"] or "OPraem" in r["name"]:
                    r["name"] = r["name"].replace("O.Praem.", "").replace("O.Praem", "").replace("OPraem", "")
                    r["orderAbbreviation"] = "OPraem"

                if "O.Cist." in r["name"] or "O. Cist" in r["name"] or "O.Cist" in r["name"]:
                    r["name"] = r["name"].replace("O.Cist.", "").replace("O. Cist", "").replace("O.Cist", "")
                    r["orderAbbreviation"] = "OCist"

                if "OFMCap" in r["name"] or "OFM Cap" in r["name"] or "OFM Cap." in r["name"]:
                    r["name"] = r["name"].replace("OFMCap", "").replace("OFM Cap.", "").replace("OFM Cap", "")
                    r["orderAbbreviation"] = "OFMCap"

                if ("SchP" in r["name"] or "SP" in r["name"] or "Sch. P" in r["name"] ) and not "OSPPE" in r["name"]:
                    r["name"] = r["name"].replace("SchP", "").replace("SP", "").replace("Sch. P", "")
                    r["orderAbbreviation"] = "SP"

                if "SChr." in r["name"]:
                    r["name"] = r["name"].replace("SChr.", "")
                    r["orderAbbreviation"] = "SChr"

                for oa in orderAbbreviations:
                    if oa in r["name"]:
                        r["name"] = r["name"].replace(oa, "")
                        r["orderAbbreviation"] = oa
                
                r["name"] = r["name"].strip()
                new_results.append(r)
                
            return new_results


        return _wrapper
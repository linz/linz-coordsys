#!/usr/bin/python3
import csv
import requests
import json
from collections import namedtuple
import math
import subprocess
import time
import os

CrsDef = namedtuple("CrsDef", "code type ordinates epoch")
ConversionDef = namedtuple("ConversionDef", "crsin crsout")
ConversionTest = namedtuple("ConversionTest", "id crdin crdout")
CrsDef.__str__ = lambda s: f"{s.code}:{s.type}:{s.ordinates}:{s.epoch}"
ConversionDef.__str__ = lambda s: f"{s.crsin}->{s.crsout}"

Testfile = "test_coords.csv"
CrsFields = ("crdsys", "cstype", "order")
OrdinateFields = ("ord1", "ord2", "ord3")
EpochField = "epoch"
IdField = "id"

CoordApiUrl = os.environ.get(
    "CONCORD_API_URL", "https://www.geodesy.linz.govt.nz/api/conversions/v1/convert-to"
)
ConcordExe = os.environ.get("CONCORD_PROGRAM", "/usr/bin/concord")

ApiCoordOrder = {
    "ENH": ("east", "north", "up"),
    "EN": ("east", "north"),
    "XYZ": ("geocentricX", "geocentricY", "geocentricZ"),
}

TestOrdinateScaleFactor = {
    "P": [1.0, 1.0, 1.0],
    "G": [100000.0, 100000.0, 1.0],
    "X": [1.0, 1.0, 1.0],
}

# Rounding to 4dp so add a little leeway for inclusion of multiple ordinates
DefaultTolerance = 0.0002


def main():
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument(
        "-f", "--test-file", default=Testfile, help="Input file of test coordinates"
    )
    parser.add_argument(
        "-c",
        "--concord",
        action="store_true",
        help="Use concord program instead of coordinate API",
    )

    parser.add_argument(
        "-t",
        "--tolerance",
        type=float,
        default=DefaultTolerance,
        help="Tolerance in output coordinate match",
    )
    parser.add_argument(
        "-p",
        "--list-all-tests",
        action="store_true",
        help="Includes ok conversions in results",
    )
    parser.add_argument("test_ids", nargs="*", help="Ids of specific tests to run")
    args = parser.parse_args()

    testids = args.test_ids
    debug = bool(testids)
    convfunc = concordConversion if args.concord else apiConversion

    convtests = loadTests(args.test_file, testids)
    diffmax = 0.0
    errors = []
    for conversion, tests in convtests.items():
        testerrors = []
        time0 = time.process_time()
        testdiff = 0.0
        try:
            testdiff, testerrors = runConversionTests(
                conversion,
                tests,
                debug=debug,
                convfunc=convfunc,
                tolerance=args.tolerance,
            )
            if testdiff > diffmax:
                diffmax = testdiff

        except Exception as ex:
            message = f"Error in {conversion}: {ex}"
            testerrors = [message]
            print(message)
        elapsed = time.process_time() - time0
        errors.extend(testerrors)
        if args.list_all_tests or len(testerrors) > 0:
            print(
                f"Conversion {conversion.crsin.code}->{conversion.crsout.code}({conversion.crsin.epoch}): diff {testdiff:.4f}: errors {len(testerrors)}/{len(tests)}: duration {elapsed:.2f}"
            )
    print(f"Maximum conversion coordinate difference: {diffmax:0.4f}")
    for error in errors:
        print(error)


def loadTests(testfile, testids=None):
    tests = {}
    with open(testfile) as csvh:
        csvr = csv.DictReader(csvh)
        for row in csvr:
            testid = row[IdField]
            if testids and testid not in testids:
                continue
            crsin = CrsDef(
                *(row[f"{csparam}_in"] for csparam in CrsFields), row[EpochField]
            )
            crsout = CrsDef(
                *(row[f"{csparam}_out"] for csparam in CrsFields), row[EpochField]
            )
            conversion = ConversionDef(crsin, crsout)
            if conversion not in tests:
                tests[conversion] = []
            tests[conversion].append(
                ConversionTest(
                    row[IdField],
                    [float(row[f"{ord}_in"]) for ord in OrdinateFields],
                    [float(row[f"{ord}_out"]) for ord in OrdinateFields],
                )
            )
    return tests


def crsCode(crsdef):
    code = crsdef.code
    if "/" not in code:
        nord = len(crsdef.ordinates)
        if crsdef.type == "P" and nord == 3:
            code = code + "/ELLIPSOIDAL"
        elif crsdef.type == "G" and nord == 2:
            code = code + "/NONE"
    return f"LINZ:{code}"


def apiConversion(conversion, incrds, debug=False):
    crsin = conversion.crsin
    crsout = conversion.crsout
    incrds = {
        "crs": crsCode(crsin),
        "coordinateOrder": ApiCoordOrder[crsin.ordinates],
        "coordinates": incrds,
    }
    if crsin.epoch:
        incrds["coordinateEpoch"] = float(crsin.epoch)
    ordout = crsout.ordinates
    params = {
        "crs": crsCode(crsout),
        "coordinateOrder": "/".join(ApiCoordOrder[ordout]),
    }
    if debug:
        print(f"Input coordinates:\n{json.dumps(incrds,indent=2)}")
        print(f"Parameters: {json.dumps(params)}")
    response = requests.post(CoordApiUrl, params=params, json=incrds)
    if response.status_code != 200:
        raise RuntimeError(f"{response.text}")
    outdata = response.json()
    if debug:
        print(f"Response:\n{json.dumps(outdata,indent=2)}")
    errmsg = ",".join(outdata.get("coordinateErrors", []))
    outcrds = outdata["coordinateList"]["coordinates"]
    errors = [errmsg if c is None else "" for c in outcrds]
    return outcrds, errors


def concordCrs(crsdef):
    if crsdef.type == "X":
        return crsdef.code
    return f"{crsdef.code}:{crsdef.ordinates}{':D' if crsdef.type == 'G' else ''}"


def concordConversion(conversion, incrds, debug=False):

    crsin = conversion.crsin
    crsout = conversion.crsout
    ncrd = len(crsin.ordinates)
    ndp = "9:4" if crsout.type == "G" else "4"
    command = [
        ConcordExe,
        f"-I{concordCrs(crsin)}",
        f"-O{concordCrs(crsout)}",
        f"-P{ndp}",
        "-",
        "-",
    ]
    if crsin.epoch:
        command.insert(4, f"-Y{crsin.epoch}")
    input = "".join([" ".join([str(c) for c in crd[:ncrd]]) + "\n" for crd in incrds])
    if debug:
        print(f"Concord command: {' '.join(command)}")
        print(f"Concord input:\n{input.strip()}")
    input = input.encode("utf8")
    result = subprocess.run(
        command, input=input, stdout=subprocess.PIPE, stderr=subprocess.PIPE
    )
    output = result.stdout.decode("utf8").strip()
    error = result.stderr.decode("utf8").strip()
    if debug:
        print(f"Concord output:\n{output}")
        if error:
            print(f"Concord error:\n{error}")
    if error:
        raise RuntimeError(error)
    ncrd = len(crsout.ordinates)
    outcrds = []
    crderrors = []
    for line in output.split("\n"):
        outcrd = None
        error = None
        if "***" in line:
            error = line
        else:
            try:
                outcrd = [float(c) for c in line.split()[:ncrd]]
                if ncrd == 2:
                    outcrd.append(0.0)
            except Exception as ex:
                error = f"Error reading output: {line}: {ex}"
        outcrds.append(outcrd)
        crderrors.append(error)
    return outcrds, crderrors


def runConversionTests(
    conversion, tests, debug=False, convfunc=apiConversion, tolerance=DefaultTolerance
):
    if debug:
        print(f"Testing conversion {conversion}")
    crsin = conversion.crsin
    crsout = conversion.crsout
    ids = [t.id for t in tests]
    incrds = [t.crdin for t in tests]
    outtest = [t.crdout for t in tests]
    factor = TestOrdinateScaleFactor[crsout.type]
    diffmax = 0.0
    try:
        outcrds, crderrors = convfunc(conversion, incrds, debug)
    except Exception as ex:
        error = f"Test {','.join(ids[:5])}: Exception in {conversion}: {ex}"
        return diffmax, [error]
    errors = []
    if debug:
        print(f"Expected:\n{json.dumps(outtest,indent=2)}")

    for id, crdout, crdtest, crderror in zip(ids, outcrds, outtest, crderrors):
        if crdout is None:
            errors.append(f"Test {id}: Failed to calculate: {crderror}")
            continue
        diff = [
            (crdtest[i] - crdout[i]) * factor[i] for i in range(len(crsout.ordinates))
        ]
        difflen = math.sqrt(sum((d * d for d in diff)))
        if difflen > diffmax:
            diffmax = difflen
        if difflen > tolerance:
            errors.append(
                f"Test {id}: {crsin.code} to {crsout.code}: Test difference {difflen:0.4f} > {tolerance}"
            )
    return diffmax, errors


if __name__ == "__main__":
    main()
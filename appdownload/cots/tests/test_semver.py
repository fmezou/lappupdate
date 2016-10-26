"""
This module defines a test suite for testing the semver module.
"""

import logging

import semver


__author__ = "Frederic MEZOU"
__version__ = "0.1.0"
__license__ = "GNU GENERAL PUBLIC LICENSE Version 3, 29 June 2007"


if __name__ == "__main__":
    logging.basicConfig(
        format="%(levelname)s - %(name)s [%(funcName)s] - %(message)s",
        level=logging.ERROR)
    logger = logging.getLogger(__name__)
    # Syntax test
    checked = True
    try:
        v = semver.SemVer("1.0.0")
        if v == 0:
            pass
        if v != 0:
            pass
        if v < 0:
            pass
        if v > 0:
            pass
    except TypeError as err:
        pass
    else:
        checked = False
        logger.error("..Operation must have an semver.SemVer object "
                     "as left operand")

    print("Syntax test {}verified".format("" if checked else "not "))

    # Rule #2 ------------------------------------------------------------------
    checked = True
    v = semver.SemVer("1.0.0")
    try:
        v = semver.SemVer("-1.0.0")
    except ValueError as err:
        pass
    else:
        checked = False
        logger.error("..Non-negative integers must be rejected")

    try:
        v = semver.SemVer("0.-1.0")
    except ValueError as err:
        pass
    else:
        checked = False
        logger.error("..Non-negative integers must be rejected")

    try:
        v = semver.SemVer("0.0.-1")
    except ValueError as err:
        pass
    else:
        checked = False
        logger.error("..Non-negative integers must be rejected")

    print("Rule #2 {}verified".format("" if checked else "not "))

    # Rule #4 ------------------------------------------------------------------
    checked = True
    v = semver.SemVer("0.1.0")
    if v.unstable:
        pass
    else:
        checked = False
        logger.error("..Major version zero (0.y.z) is for initial development.")

    print("Rule #4 {}verified".format("" if checked else "not "))

    # Rule #9 ------------------------------------------------------------------
    checked = True
    v1 = semver.SemVer("1.0.0-alpha.1")
    v2 = semver.SemVer("1.0.0")
    if v1.unstable:
        pass
    else:
        checked = False
        logger.error("..A pre-release version indicates that the version"
                     " is unstable.")

    cmp1 = v1 < v2
    cmp2 = v2 > v1
    if cmp1 and cmp2:
        pass
    else:
        checked = False
        logger.error("..Pre-release versions have a lower precedence than the "
                     "associated normal version.")

    print("Rule #9 {}verified".format("" if checked else "not "))

    # Rule #10 -----------------------------------------------------------------
    checked = True
    v1 = semver.SemVer("1.0.0-beta+exp.sha.5114f85")
    v2 = semver.SemVer("1.0.0-beta")
    cmp1 = v1 == v2
    cmp2 = v1 != v2
    if cmp1 and not cmp2:
        pass
    else:
        checked = False
        logger.error("..Two versions that differ only in the build metadata, "
                     "have the same precedence.")

    print("Rule #10 {}verified".format("" if checked else "not "))

    # Rule #11 -----------------------------------------------------------------
    checked = True
    v1 = semver.SemVer("1.0.0")
    v2 = semver.SemVer("2.0.0")
    v3 = semver.SemVer("2.1.0")
    v4 = semver.SemVer("2.1.1")
    cmp1 = v1 < v2 < v3 < v4
    cmp2 = v4 > v3 > v2 > v1
    if cmp1 and cmp2:
        pass
    else:
        checked = False
        logger.error("Precedence is determined by the first difference when"
                     " comparing each of these identifiers from left to right.")

    v1 = semver.SemVer("1.0.0-alpha")
    v2 = semver.SemVer("1.0.0-alpha.1")
    v3 = semver.SemVer("1.0.0-alpha.beta")
    v4 = semver.SemVer("1.0.0-beta")
    v5 = semver.SemVer("1.0.0-beta.2")
    v6 = semver.SemVer("1.0.0-beta.11")
    v7 = semver.SemVer("1.0.0-rc.1")
    v8 = semver.SemVer("1.0.0")
    cmp1 = v1 < v2 < v3 < v4 < v5 < v6 < v7 < v8
    cmp2 = v8 > v7 > v6 > v5 > v4 > v3 > v2 > v1
    if cmp1 and cmp2:
        pass
    else:
        checked = False
        logger.error("Precedence for two pre-release versions with the same "
                     "major, minor, and patch version MUST be determined by "
                     "comparing each dot separated identifier from left to "
                     "right until a difference is found.")

    print("Rule #11 {}verified".format("" if checked else "not "))

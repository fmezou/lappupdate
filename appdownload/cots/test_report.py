# Reserved for test
# This module is used as a script only for test.

import logging
import os

import core
import dummy


if __name__ == "__main__":
    logging.basicConfig(
        format="%(levelname)s - %(name)s [%(funcName)s] - %(message)s",
        level=logging.WARNING)
    logger = logging.getLogger(__name__)
    checked = True

    report = core.Report()
    handler = core.MailHandler("smtp.free.fr",
                               "frederic.mezou@free.fr",
                               "lappupdate.mezou@free.fr"
                               )
    report.add_handler(handler)
    prod = dummy.Product()
    attr = prod.dump()
    report.add_section(attr)
    for i in range(2):
        prod.name = "Dummy {}".format(i)
        attr = prod.dump()
        report.add_section(attr)

    attr["about"] = "The below product have been updated. Mise à jour de produit lénaïg"
    attr["title"] = "Product update - Mise à jour de produit"
    report.publish(attr)

    report = core.Report()
    handler = core.FileHandler("_report.html")
    report.add_handler(handler)
    prod = dummy.Product()
    attr = prod.dump()
    report.add_section(attr)
    for i in range(2):
        prod.name = "Dummy {}".format(i)
        attr = prod.dump()
        report.add_section(attr)

    attr["about"] = "The below product have been updated."
    attr["title"] = "Product update"
    report.publish(attr)

    report = core.Report(template="summary_tmpl.txt")
    handler = core.FileHandler("_report.txt")
    report.add_handler(handler)
    handler = core.StreamHandler()
    report.add_handler(handler)
    prod = dummy.Product()
    attr = prod.dump()
    report.add_section(attr)
    for i in range(2):
        prod.name = "Dummy {}".format(i)
        attr = prod.dump()
        report.add_section(attr)

    attr["about"] = "The below product have been updated."
    attr["title"] = "Product update"
    report.publish(attr)

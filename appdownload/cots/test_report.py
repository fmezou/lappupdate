# Reserved for test
# This module is used as a script only for test.

import logging

import report
import dummy


if __name__ == "__main__":
    logging.basicConfig(
        format="%(levelname)s - %(name)s [%(funcName)s] - %(message)s",
        level=logging.WARNING)
    logger = logging.getLogger(__name__)
    checked = True

    a_report = report.Report()
    a_handler = report.MailHandler("smtp.free.fr",
                                   "frederic.mezou@free.fr",
                                   "lappupdate.mezou@free.fr"
                                   )
    a_report.add_handler(a_handler)
    prod = dummy.Product()
    attr = prod.dump()
    a_report.add_section(attr)
    for i in range(2):
        prod.name = "Dummy {}".format(i)
        attr = prod.dump()
        a_report.add_section(attr)

    attr["about"] = "The below product have been updated. " \
                    "Mise à jour de produit lénaïg"
    attr["title"] = "Product update - Mise à jour de produit"
    a_report.publish(attr)

    a_report = report.Report()
    a_handler = report.FileHandler("_report.html")
    a_report.add_handler(a_handler)
    prod = dummy.Product()
    attr = prod.dump()
    a_report.add_section(attr)
    for i in range(2):
        prod.name = "Dummy {}".format(i)
        attr = prod.dump()
        a_report.add_section(attr)

    attr["about"] = "The below product have been updated."
    attr["title"] = "Product update"
    a_report.publish(attr)

    a_report = report.Report(template="summary_tmpl.txt")
    a_handler = report.FileHandler("_report.txt")
    a_report.add_handler(a_handler)
    a_handler = report.StreamHandler()
    a_report.add_handler(a_handler)
    prod = dummy.Product()
    attr = prod.dump()
    a_report.add_section(attr)
    for i in range(2):
        prod.name = "Dummy {}".format(i)
        attr = prod.dump()
        a_report.add_section(attr)

    attr["about"] = "The below product have been updated."
    attr["title"] = "Product update"
    a_report.publish(attr)

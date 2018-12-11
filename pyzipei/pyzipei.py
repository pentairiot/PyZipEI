from requests import get
from bs4 import BeautifulSoup
from traceback import format_exc as generate_traceback


openei = "https://openei.org/"
us_utility_db = "{}apps/USURDB/".format(openei)


class PyZipEIException(Exception):
    pass


def ei_from_zipcode(zipcode,
                    sector="Residential",
                    timeout=30,
                    log=lambda x: None):
    recognized_sectors = ['Residential', 'Commercial', 'Industrial', 'Transportation']
    if sector not in recognized_sectors:
        raise PyZipEIException("Sector {} not in Recognized Sectors, {}".format(sector, recognized_sectors))

    if zipcode in ei_from_zipcode.cache:
        log("{} found in cache".format(zipcode))
        return ei_from_zipcode.cache[zipcode]

    utility_info_id = "urdbUtilityInfoContent"

    # Request OpenEI with ZipCode
    zip_req_url = "{}?utilRateFindByZip={}".format(us_utility_db, zipcode)
    log("Requesting EI from {}".format(zip_req_url))
    zip_resp = get(zip_req_url, timeout=timeout)

    if not 200 <= zip_resp.status_code < 300:
        raise PyZipEIException("OpenEI Zipcode Request Failed")

    zip_page = BeautifulSoup(zip_resp.text, "html.parser")

    try:
        log("Attempting Rate Extraction via Provider Wiki Page")
        utility_info = zip_page.find_all(id=utility_info_id)[0]
        utilities = utility_info.find_all('a')
        hrefs = []
        for utility in utilities:
            hrefs.append(utility.get("href"))
        provider_wikis = set(hrefs)

        # Retrieve Utility Provider Wiki pages
        log("Retrieving {} wikis".format(len(provider_wikis)))
        for wiki in provider_wikis:
            wiki_url = "{}{}".format(openei, wiki)
            try:
                resp = get(wiki_url, timeout=timeout)

                # Extract Utility Rate from Wiki Page
                page = BeautifulSoup(resp.text, "lxml")
                summary_content = page.find_all(id="mw-content-text")[0]

                def rate_found(rate):
                    return 'Residential' in rate.keys()

                try:
                    rate_lines = summary_content.find_all("ul")[1].get_text()
                except IndexError:
                    raise PyZipEIException("Rates not found in {}".format(wiki_url))

                for line in rate_lines.split("\n"):
                    key, value = line.split(":")
                    key = key.strip()
                    if key == 'Residential':
                        value = value.strip()
                        value = float(value.split("/")[0][1:])
                        log("Recovered rate for {}: {}".format(zipcode, value))
                        ei_from_zipcode.cache[zipcode] = value
                        return value
            except Exception as e:
                log("Failed to process {}".format(wiki_url))
                log("{}\n".format(e))
    except Exception:
        log("Failed to look up rate through wiki page")

    log("Attempting Report Scan to find Residential Rate")
    try:
        rate_table = zip_page.findChild("table")
        for row in rate_table.findChildren("tr"):
            cells = row.findChildren("td")
            row_type = cells[2].text
            if row_type != "Residential":
                continue

            log("Residential Report Found")
            report_href = cells[-1].findChild("a").attrs["href"]
            break

        report_url = "{}{}".format(openei, report_href)
        report_resp = get(report_url, timeout=timeout)
        report_page = BeautifulSoup(report_resp.text, "html.parser")
        energy_table = report_page.find(id="energy_rate_strux_table")
        rates = []
        rows = energy_table.findAll("div", {"class": "strux_view_row tier_bottom"})
        for row in rows:
            cells = row.findChildren("div")
            rates.append(float(cells[-3].text))
        avg_rate = sum(rates) / len(rates)
        return avg_rate
    except Exception:
        log(generate_traceback())
        raise Exception("Failed to find rate")


ei_from_zipcode.cache = {}


if __name__ == "__main__":
    print("Use PyZipEI command line utility instead")
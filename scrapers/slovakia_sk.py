from typing import List

import requests
import xmltodict
from bs4 import BeautifulSoup

from scrapers.base_scraper import BaseScraper

from utils.constants import HEADERS
from utils.dynamo import write_to_dynamo
from utils.reception import Reception
from utils.utils import get_reception_points, get_website_content, normalize

SLOVAKIA_POINTS_URL = "https://www.minv.sk/?hranicne-priechody-1"

# WARNING: These checkpoints all contain `Chop` (refer to https://github.com/Ukraine-Relief-Efforts/scraper/issues/10)
# TODO: The placemarker bubble contents in the following two KML files are broken (at least on google maps)
# This file is "v1" and is structured differently from `HUNGARY_KML`.
# SLOVAKIA_KML = "https://www.google.com/maps/d/kml?forcekml=1&mid=10XSF6CAHYmRA7htR2j-7YxGNmHwLuf1m"
# This is "v2", so to say, and it's been structured with `HUNGARY_KML` in mind.
#SLOVAKIA_KML = "https://www.google.com/maps/d/kml?forcekml=1&mid=1-uXe38frly5Rd_yu2bLM5nU37_64DJZL"

# v3 - this time made with the online version of Google Earth.
SLOVAKIA_KML = "https://www.google.com/maps/d/kml?forcekml=1&mid=1umLgEK-j5BHcJAvRBZMFtWztNzhWwgoP"


###########################################################################
# Some functions for quick & dirty prototyping.
# These functions are not designed to be used for production code, so,
# removing them and anything that depends on them shouldn't be a problem.

def _save_points_website_working_copy(content: BeautifulSoup) -> None:
    with open("./.local.slovak_raw_site", "w") as f:
        f.write(str(content))


def _get_points_website_from_working_copy() -> BeautifulSoup:
    with open("./.local.slovak_raw_site", "r") as f:
        return BeautifulSoup(f.read(), "lxml")


def _print_to_file(message: str) -> None:
    with open("./.local.slovakia.out", "a") as f:
        f.write(str(message) + "\n")

###########################################################################


class SlovakiaScraper(BaseScraper):

    def scrape(self, event = ""):
        print("Scraping Slovakia (SK)")

        ###################################################################
        # This is not needed to operate the scraper and can be removed
        # at any time (just make sure you uncomment the
        # `content = get_website_content(...` line further below).

        """"Rag-tag way to cache a local copy of the website for development"""

        # Uncomment this to save a fresh copy to poke around in:
        # _save_points_website_working_copy(get_website_content(SLOVAKIA_POINTS_URL))

        # Uncomment this to get the website content from the working
        # copy file, given that you've run the
        # `_save_website_working_copy(...` line at least once:
        content = _get_points_website_from_working_copy()

        ###################################################################

        """Start with general border info"""

        # Uncomment this for production or live testing.
        # Comment it if you're using the above "rag-tag caching" method.
        # content = get_website_content(SLOVAKIA_POINTS_URL)

        general = self._get_general(content)

        """Get border crossing points"""

        reception_arr = self._get_reception_points()
        # TODO: Replace `""` with the proper URL, once it's clear which one that is.
        write_to_dynamo("slovakia-sk", event, general, reception_arr, "")

    def _get_general(self, content: BeautifulSoup) -> List[str]:
        # TODO: Implement.
        return [""]

    def _get_reception_points(self) -> List[Reception]:
        kml_str = requests.get(SLOVAKIA_KML, headers=HEADERS).content
        kml = xmltodict.parse(kml_str, dict_constructor=dict)

        # A modified copy of `get_reception_points` which, for now, works with
        # KML file "v3". There's still stuff missing, though (e.g. address).
        # What works: Using Mali Selmentsi as an example, lat & long seems to
        # work at least.
        reception_points: list[Reception] = []
        placemarks: List = kml["kml"]["Document"]["Folder"]["Placemark"]
        for placemark in placemarks:
            r = Reception()
            r.name = normalize(placemark["name"])
            coord = placemark["Point"]["coordinates"].split(',')
            r.lon = coord[0].strip()
            r.lat = coord[1].strip()
            reception_points.append(r)

        return reception_points

        # Neither the KML file "v1", "v2" nor "v3" are working with this so far.
        # return get_reception_points(
        #     kml=kml,
        #     # folder_name_whitelist=None,
        #     folder_name_whitelist=["Slovakia-Ukraine Border Checkpoints - Without cargo-only checkpoints"],
        #     style_urls_blacklist=[],
        # )

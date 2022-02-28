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

# TODO: The placemarker bubble contents in the following two KML files are broken (at least on google maps)
# This file is "v1" and is structured differently from `HUNGARY_KML`.
# SLOVAKIA_KML = "https://www.google.com/maps/d/kml?forcekml=1&mid=10XSF6CAHYmRA7htR2j-7YxGNmHwLuf1m"
# This is "v2", so to say, and it's been structured with `HUNGARY_KML` in mind.
#SLOVAKIA_KML = "https://www.google.com/maps/d/kml?forcekml=1&mid=1-uXe38frly5Rd_yu2bLM5nU37_64DJZL"

# v3 - this time made with the online version of Google Earth.
SLOVAKIA_KML = "https://www.google.com/maps/d/kml?forcekml=1&mid=1umLgEK-j5BHcJAvRBZMFtWztNzhWwgoP"


class SlovakiaScraper(BaseScraper):

    def scrape(self, event = ""):
        print("Scraping Slovakia (SK)")

        """Start with general border info"""

        content = get_website_content(SLOVAKIA_POINTS_URL)
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

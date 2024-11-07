#!/usr/bin/env python3
#
# Script written by Melissa van Beekveld and adapted by Gavin Salam 
# to extract seminars from InspireHEP and write them to an .ics file,
# for easy import to a calendar.
#
# Usage:
#   python3 inspire-seminars-to-ics.py "series name" ["series name"] -o output.ics
#
# Add the --all flag to get all seminars rather than just upcoming ones
# (currently limited to max 500)
#
# The script also has shortcuts for Oxford particle-theory seminars (--tpp --dalitz).
#
# It should be compatible with Python 3.5 and later

#from __future__ import annotations

from datetime import datetime
from io import TextIOWrapper

import requests
import argparse
import re



def format_datetime(timestring: str) -> str:
    # in Python>3.11, the following works, but it is not backwards compatible
    #time_as_datetime = datetime.fromisoformat(timestring)
    time_as_datetime = datetime.strptime(re.sub(r"\.0+","",timestring), "%Y-%m-%dT%H:%M:%S")
    return time_as_datetime.strftime("%Y%m%dT%H%M%SZ")

#def generate_summary(speaker_names: list[str], title: str) -> str:
def generate_summary(speaker_names, title):
    names = ", ".join(" ".join(speaker.split(', ')[::-1]) for speaker in speaker_names)
    return names + " \u2014 " + title

def write_hit_contents(hit, file: TextIOWrapper):
    seminar_id    = hit["id"]
    start_time    = hit["metadata"]["start_datetime"]
    end_time      = hit["metadata"]["end_datetime"]
    title         = hit["metadata"]["title"]["title"]
    speaker_names = [speaker["name"] for speaker in hit["metadata"]["speakers"]]
    categories    = [cat["term"] for cat in hit["metadata"]["inspire_categories"]]
    file.write("BEGIN:VEVENT\n")
    file.write("DTSTART:{}\n".format(format_datetime(start_time)))
    file.write("DTEND:{}\n".format(format_datetime(end_time)))
    file.write("UID:inspirehep-seminar-{}\n".format(seminar_id))
    file.write("SUMMARY:{}\n".format(generate_summary(speaker_names, title)))
    file.write("URL:https://inspirehep.net/seminars/{}\n".format(seminar_id))
    file.write("CATEGORIES:{}\n".format(",".join(categories)))
    file.write("END:VEVENT\n")


def write_ics_file(name_ics, hits):
    with open(name_ics, "w", encoding="utf-8") as file:
        file.write("BEGIN:VCALENDAR\n")
        file.write("VERSION:2.0\n")
        file.write("CALSCALE:GREGORIAN\n")
        file.write("PRODID:inspirehep/seminars\n")
        for hit in hits:
            write_hit_contents(hit, file)
        file.write("END:VCALENDAR\n")

if __name__ == "__main__":

    parser = argparse.ArgumentParser(description="Fetch seminars from INSPIRE and write them to an .ics file")
    parser.add_argument("--dalitz", action="store_true", help="Fetch Dalitz seminars")
    parser.add_argument("--tpp", action="store_true", help="Fetch TPP seminars")
    parser.add_argument("--output","-o", default="inspire.ics", type=str, help="Name of the output file")
    parser.add_argument("--all", action="store_true", help="get all seminars rather than just upcoming ones")
    parser.add_argument("--quiet", "-q", action="store_true", help="Suppress output")
    # any further argument not starting with a - should be treated as a seminar name, to go into an 
    # array of seminar names
    parser.add_argument("seminar_names", nargs="*", help="Names of the seminars to fetch")
    args = parser.parse_args()

    if args.dalitz: args.seminar_names.append("Oxford Dalitz Seminar in Fundamental Physics")
    if args.tpp:    args.seminar_names.append("Oxford Theoretical Particle Physics seminar")

    inspire_url = "https://inspirehep.net/api/seminars"

    # choice = input("Press 0 for Dalitz, 1 for TPP: ")    
    # if choice == "0":
    #     params    = {"start_date": "upcoming", "q": 'series.name:"Oxford Dalitz Seminar in Fundamental Physics"'}
    #     save_name = "INSPIRE-Seminars-Dalitz.ics"
    # else:
    #     params    = {"start_date": "upcoming", "q": 'series.name:"Oxford Theoretical Particle Physics seminar"'}
    #     save_name = "INSPIRE-Seminars-TPP.ics"

    hits = []
    for seminar_name in args.seminar_names:

        params    = {"start_date": "all" if args.all else "upcoming", 
                     'size': 500,
                     "q": 'series.name:"{}"'.format(seminar_name),
                     }
        response = requests.get(url=inspire_url, params=params)
        # print out the URL that was fetched, including the get parameters
        if not args.quiet: print("Fetched url = {}".format(response.url))

        results  = response.json()
        hits     += results["hits"]["hits"]

    write_ics_file(args.output, hits)
    if not args.quiet: print("Created {} with {} seminars".format(args.output, len(hits))) 

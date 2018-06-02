#!/usr/bin/env python
# coding=utf-8
"""Parser to retrieve bin collection dates from the Hertfordshire County Council website"""
import requests
from urllib.parse import urlparse, parse_qs
from bs4 import BeautifulSoup
import argparse


def __main__():
    parser = argparse.ArgumentParser(description='Find bin collection dates from Hertfordshire County Council\'s website')
    action = parser.add_mutually_exclusive_group(required=True)
    action.add_argument('--refuse',    help='Return next Refuse collection date',    action='store_true')
    action.add_argument('--recycling', help='Return next recycling collection date', action='store_true')
    action.add_argument('--organic',   help='Return next organics collection date',  action='store_true')
    parser.add_argument("houseNumber")
    parser.add_argument("postcode", help='N.B. Case sensitive and must include space.')

    args = parser.parse_args()

    details_html = get_details_html(args.houseNumber, args.postcode)
    html_data = parse_html(details_html)

    if args.refuse:
        print(get_refuse_date(html_data))
    elif args.recycling:
        print(get_recycling_date(html_data))
    elif args.organic:
        print(get_organic_date(html_data))


def get_details_html(house_number, postcode):
    """
    Collect the HTML data for a given house number and postcode
    :param house_number: House name or number
    :param postcode: Postcode. Case sensitive and must include space.
    :return:
    """
    session = requests.session()

    form_page_request = session.get("https://www.eastherts.gov.uk/calendars")

    form_page_url = urlparse(form_page_request.url)
    form_page_query_params = parse_qs(form_page_url.query)

    results_request = session.post("https://e-services.eastherts.gov.uk/eforms450/ufsajax?ebz="+form_page_query_params["ebz"][0], {
        "ebs": form_page_query_params["ebz"][0],
        "CTRL:15:_:A": house_number,
        "CTRL:14:_:A": postcode,
        "HID:inputs": "ICTRL:15:_:A,ICTRL:14:_:A,ACTRL:16:_,APAGE:E.h,APAGE:B.h,APAGE:N.h",
        "CTRL:16:_": "Search"
    })

    results_dict = None

    for control_dict in results_request.json()["updatedControls"]:
        if control_dict["identifier"] == "CTID-17-_-LAYOUT":
            results_dict = control_dict
            break

    if results_dict is None:
        raise ValueError("Could not find results identifier")

    return results_dict["html"]


def parse_html(html):
    """
Parse HTML data
    :param html:
    :return:
    """
    return BeautifulSoup(html, 'html.parser')


def get_refuse_date(html):
    """
Extract the next refuse collection date from parsed HTML
    :param html:
    :return:
    """
    return html.find("div", {"id": "CTID-19-_-A"}).text


def get_recycling_date(html):
    """
Extract the next recycling collection date from parsed HTML
    :param html:
    :return:
    """
    return html.find("div", {"id": "CTID-20-_-A"}).text


def get_organic_date(html):
    """
Extract the next organic collection date from parsed HTML
    :param html:
    :return:
    """
    return html.find("div", {"id": "CTID-41-_-A"}).text


if __name__ == "__main__":
    __main__()

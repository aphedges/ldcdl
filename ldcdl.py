#!/usr/bin/env python

# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

# Copyright 2016, Jonathan May

"""Get corpus from LDC: A small script by Jonathan May"""

import argparse
from getpass import getpass
from pathlib import Path
import re
import sys
from typing import Optional

from bs4 import BeautifulSoup as bs
import mechanize
import requests

LDC_CATALOG_URL = "https://catalog.ldc.upenn.edu/"
LDC_LOGIN_URL = LDC_CATALOG_URL + "login"
LDC_DL_URL = LDC_CATALOG_URL + "organization/downloads"


def download(corpus: str, outdir: Path, login: str, password: str) -> Optional[Path]:
    """Download an LDC corpus to the specified location.

    Args:
        corpus: Corpus ID.
        outdir: Output directory.
        login: LDC username.
        password: LDC password.

    Returns:
        Path to downloaded file if successful, None otherwise.
    """
    br = mechanize.Browser()
    br.set_handle_robots(False)
    br.open(LDC_LOGIN_URL)  # Sign in
    br.select_form(nr=0)
    br["spree_user[login]"] = login
    br["spree_user[password]"] = password
    br.submit()  # Logged in
    dlpage = br.open(LDC_DL_URL)
    dlpage = bs(dlpage.read(), 'html.parser')
    dlgroup = {'class': 'button download-counter-button'}

    targetstrs = dlpage.find(id='user-corpora-download-table').findAll(text=corpus)
    options = [x.fetchParents()[1] for x in targetstrs]
    labels = [[y for y in x.children][-2].text.strip().split('\n')[0].strip() for x in options]
    urls = [x.find(attrs=dlgroup).get('href') for x in options]

    if len(options) == 1:
        targeturl = urls[0]
        label = labels[0]
    elif len(options) == 0:
        sys.stderr.write(f"{corpus} not found\n")
        return None
    else:
        choices = [(str(i), x) for i, x in enumerate(labels)]
        result = None
        while result is None:
            choice_strs = '\n'.join(map(lambda x: f"{x[0]}={x[1]}", choices))
            resp = input(f"choose corpus:\n{choice_strs}\n >> ")
            if resp not in map(lambda x: x[0], choices):
                print("Please choose from the available labels")
            else:
                result = resp
        targeturl = urls[int(result)]
        label = labels[int(result)]
    fullurl = LDC_CATALOG_URL + targeturl
    print(f"Getting {label}")
    cookies = requests.cookies.RequestsCookieJar()
    for cookie in br.cookiejar:
        cookies.set_cookie(cookie)
    request = requests.get(fullurl, cookies=cookies, stream=True)

    # Parse file name from HTTP header
    content_disposition = request.headers["Content-Disposition"]
    match = re.match(r'^attachment; filename="(.*)"$', content_disposition)
    if match is None:
        raise RuntimeError(f"Cannot determine filename for download.")
    filename = match.group(1)

    destination = outdir / filename
    chunk_size = 1024 * 8
    with open(destination, "wb") as file:
        for chunk in request.iter_content(chunk_size=chunk_size):
            file.write(chunk)
    return destination


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__,
                                     formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument("--outdir", "-o", type=Path, required=True, help="Output directory.")
    parser.add_argument("--corpus", "-c", required=True, nargs='+',
                        help="Corpus name(s) (e.g. LDC99T42)")
    parser.add_argument("--login", "-l", required=True, help="LDC username.")
    args = parser.parse_args()

    if not args.outdir.is_dir():
        raise RuntimeError(f"`{args.outdir}` is not a valid directory.")

    password = getpass("password >> ")

    for corpus in args.corpus:
        result = download(corpus, args.outdir, args.login, password)
        if result is not None:
            print(f"Retrieved {corpus} to {result}")


if __name__ == '__main__':
    main()

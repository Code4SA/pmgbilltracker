from __future__ import print_function
import re
import time
from pmg_backend.models import Bill


def populate_entry(entry, data, bill_codes=None):
    # populate bill relations
    if bill_codes:
        for code in bill_codes:
            tmp_bill = Bill.query.filter(Bill.code==code).first()
            if tmp_bill:
                entry.bills.append(tmp_bill)
            else:
                # logger.info("Could not find related bill: " + code)
                pass
    # populate required fields
    entry.type = data['entry_type']
    entry.date = data['date']
    entry.title = data['title']
    # populate optional fields
    if data.get("description"):
        entry.description = data['description']
    if data.get("location"):
        entry.location = data['location']
    if data.get("url"):
        entry.url = data['url']
    if data.get("agent"):
        entry.agent = data['agent']
    return entry


def handler(obj):
    if hasattr(obj, 'isoformat'):
        return obj.isoformat()
    else:
        raise TypeError, 'Object of type %s with value of %s is not JSON serializable' % (type(obj), repr(obj))


class URLFetcher(object):

    def __init__(self, url, session):
        self.url = url
        self.session = session
        self.delay = 0.3

    @property
    def html(self):
        time.sleep(self.delay)  # avoid flooding the server with too many requests
        r = self.session.get(self.url)
        return r.content

    def follow_redirect(self):
        time.sleep(self.delay)
        r = self.session.get(self.url)
        return r.url


class FileFetcher(object):
    filename = "bill"

    @property
    def html(self):
        return open(FileFetcher.filename).read()


# RE-patterns for finding bill instances

# 1.    Match bills occurring within arbitrary text files. Disregard draft bills.
#       Require brackets/space around bill code.

re_bill_1 = re.compile("""
    (^|[\s\[])      # Opening bracket / space.
    (PMB|B)\s*      # prefix (ordinary or Private Member Bill)
    ([0-9]+)        # Bill number
    ([A-Z])*        # Bill version
    \s*-\s*
    ([0-9]{4})      # The year of introduction.
    ($|[\s\]])      # Closing bracket / space.
""", re.IGNORECASE | re.VERBOSE | re.MULTILINE)

# 2.    Match bills and draft bills, without requiring brackets / spaces around the bill code.
re_bill_2 = re.compile("""
    (PMB|B)\s*      # prefix (ordinary or Private Member Bill).
    ([0-9]+|X+)*    # Bill number
    ([A-Z])*        # Bill version
    \s*-\s*
    ([0-9]{4})      # The year of introduction.
""", re.IGNORECASE | re.VERBOSE)


def find_bills(text, include_versions=False):
    """
    Find the reference code for each bill mentioned in the given text.
    """

    matches = re_bill_1.findall(text)
    if not matches:
        return None

    out = {}
    for result in set(matches):
        bracket_1, prefix, number, version, year, bracket_2 = result
        prefix = prefix.upper()
        version = version.upper()
        code = prefix + number + "-" + year
        out[code] = [code,]
        if include_versions and version:
            version_id = prefix + number + (version if version else "") + "-" + year
            if not version_id in out[code]:
                out[code].append(version_id)

    if include_versions:
        return out
    else:
        return out.keys()


def analyze_bill_code(text):
    """
    Extract components of the information contained in a code that references a particular bill, eg. "[PMB15C - 2013]".
    """

    match = re_bill_2.match(text)
    if not match:
        return None

    prefix = match.group(1).upper()
    number = match.group(2)
    if number and "X" in number:
        number = None
    version = match.group(3)
    if version:
        version = version.upper()
    year = match.group(4)

    code = prefix + (number if number else "X") + "-" + year

    status = "Bill"
    if not number:
        status = "Draft"
    elif "as enacted" in text.lower():
        status = "Act"

    out = {
        'code': code,
        'type': prefix,
        'number': number,
        'status': status,
        'year': year,
        'version': version if version else None,
    }
    return out


if __name__ == "__main__":

    for text in [" B6C-2010 ", "B6F -2010", "B4 - 2010 - as enacted", "B - 2010", "PMB5-2013", "B78-2008 as enacted", "16 Oct 2013 - Marine Living Resources Amendment Bill [B30-2013]: Public hearings Day 2"]:
        print(text)
        print(find_bills(text, True))
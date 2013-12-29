import datetime
from pmg_backend.models import *
from pmg_backend import db
import simplejson


def add_entry(data, bill_codes):
    entry = Entry()
    for code in bill_codes:
        tmp_bill = Bill.query.filter(Bill.code==code).first()
        if tmp_bill:
            entry.bills.append(tmp_bill)
        else:
            print("Could not find related bill.")
            raise Exception
    entry.type = data['entry_type']
    entry.date = data['date']
    entry.title = data['title']
    if data.get("description"):
        entry.description = data['description']
    if data.get("location"):
        entry.location = data['location']
    if data.get("stage"):
        entry.stage = data['stage']
    if data.get("url"):
        entry.stage = data['url']

    return

def scrape_bills(DEBUG):
    from pmg import bills
    bill_dict, draft_list = bills.run_scraper(DEBUG)

    print str(len(bill_dict)) + " bills scraped"
    print str(len(draft_list)) + " draft bills scraped"

    # save scraped bills to database
    for bill_code, bill in bill_dict.iteritems():
        tmp = Bill.query.filter(Bill.code==bill_code).first()
        if tmp is None:
            tmp = Bill()
            tmp.code = bill_code
        tmp.name = bill['bill_name']
        if bill.get('introduced_by'):
            tmp.introduced_by = bill['introduced_by']
        tmp.year = bill['year']
        tmp.bill_type = bill['bill_type']
        db.session.add(tmp)
        db.session.commit()
        # save related bill versions
        for data in bill['versions']:
            data["entry_type"] = "bill_version"
            add_entry(data, [bill_code, ])

    # save scraped draft bills to database
    for draft in draft_list:
        tmp = Bill.query.filter(Bill.name==draft['bill_name']).filter(Bill.year==draft['year']).first()
        if tmp is None:
            tmp = Bill()
            tmp.name = draft['bill_name']
            tmp.year = draft['year']
        tmp.bill_type = draft['bill_type']
        if bill.get('introduced_by'):
            tmp.introduced_by = draft['introduced_by']
        db.session.add(tmp)
        db.session.commit()

    return


def scrape_hansards():

    return


def scrape_committees():

    return


if __name__ == "__main__":

    DEBUG = True

    db.drop_all()
    db.create_all()

    scrape_bills(DEBUG)

    db.session.commit()
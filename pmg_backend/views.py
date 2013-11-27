from flask import request, make_response, url_for, session, render_template
from pmg_backend import app
from models import *
from pmg_backend import db, logger
from serializers import BillSerializer

bill_serializer = BillSerializer()

@app.route('/')
def autodiscover():
    """
    Provide a landing page that documents the API endpoints that are available, and provides a link
    to the admin interface.
    """

    logger.debug("landing page called")

    return render_template('index.html')


@app.route('/bill/')
@app.route('/bill/year/<year>/')
def bill_list(year=None):

    logger.debug("Bill list endpoint called")
    if year:
        tmp = Bill.query.filter(Bill.year==int(year)).all()
        response = make_response(bill_serializer.serialize(tmp))
    else:
        tmp = Bill.query.order_by(Bill.year.desc()).all()
        response = make_response(bill_serializer.serialize(tmp))
    response.mimetype = "application/json"
    return response


@app.route('/bill/<bill_id>/')
def bill_detail(bill_id):

    logger.debug("Bill detail endpoint called")

    tmp = Bill.query.get_or_404(bill_id)
    response = make_response(bill_serializer.serialize(tmp, include_related=True))
    response.mimetype = "application/json"
    return response

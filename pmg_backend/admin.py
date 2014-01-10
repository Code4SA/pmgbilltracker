from pmg_backend import app
from flask.ext.admin import Admin, form, BaseView, expose
from flask.ext.admin.contrib.sqla import ModelView
from models import *
from flask.ext.admin.contrib.fileadmin import FileAdmin
from wtforms.fields import SelectField, TextAreaField


class BillView(ModelView):
    column_list = ('name', 'code', 'bill_type', 'status')
    column_searchable_list = ('code', 'name')
    page_size = 50
    form_excluded_columns = ('entries', )
    form_overrides = dict(bill_type=SelectField, status=SelectField, objective=TextAreaField)
    form_args = dict(
        # Pass the choices to the `SelectField`
        bill_type=dict(
            choices=[
                ("Section 75 (Ordinary Bills not affecting the provinces)", "Section 75 (Ordinary Bills not affecting the provinces)"),
                ("Section 76 (Ordinary Bills affecting the provinces)", "Section 76 (Ordinary Bills affecting the provinces)"),
                ("Other", "Other"),
            ]
        ),
        status=dict(
            choices=[
                (None, "Unknown"),
                ("na", "In progress - NA"),
                ("ncop", "In progress - NCOP"),
                ("assent", "Sent to the President"),
                ("enacted", "Enacted"),
                ("withdrawn", "Withdrawn")
            ]
        )
    )

entry_types = [
        "gazette",
        "memorandum",
        "greenpaper",
        "whitepaper",
        "draft",
        "bill",
        "pmg-meeting-report",
        "public-hearing-report",
        "committee-report",
        "hansard-minutes",
        "vote-count",
        "other",
        ]

entry_type_choices = []
for entry_type in entry_types:
    entry_type_choices.append((entry_type, entry_type))


class EntryView(ModelView):
    form_overrides = dict(type=SelectField, location=SelectField, notes=TextAreaField)
    form_args = dict(
        # Pass the choices to the `SelectField`
        type=dict(
            choices=entry_type_choices
        ),
        location=dict(
            choices=[
                (None, "Unknown"),
                (1, "National Assembly (NA)"),
                (2, "National Council of Provinces (NCOP)"),
                (3, "President's Office"),
            ]
        )
    )
    # TODO: paste raw url

admin = Admin(app, name='PMG Bill Tracker', base_template='admin/my_master.html')

admin.add_view(BillView(Bill, db.session, name="Bills"))
admin.add_view(EntryView(Entry, db.session, name="Entries"))

# views for CRUD admin
admin.add_view(ModelView(Agent, db.session, name="Agents"))

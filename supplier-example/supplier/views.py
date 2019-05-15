"""
Routes and views for the flask application.
"""

from datetime import datetime

from flask import render_template, jsonify, request

from supplier import app
from supplier.build_scr import build_scr
from supplier.callmhs import call_mhs


@app.route('/')
@app.route('/home')
def home():
    """Renders the home page."""
    return render_template(
        'index.html',
        title='Home Page',
        year=datetime.now().year,
    )


@app.route('/call_mhs')
def background_process():
    try:
        interaction_name = request.args.get('interaction_name', 0, type=str)
        asid = request.args.get('asid', 0, type=str)
        nhs_number = request.args.get('nhs_number', 0, type=str)
        human_readable = request.args.get('human_readable', 0, type=str)

        if interaction_name.lower() == 'gp_summary_upload':
            scr = build_scr(asid, nhs_number, human_readable)

            mhs_result = call_mhs(interaction_name, scr)
            return jsonify(result=mhs_result)
        else:
            return jsonify(result='Unknown MHS Adaptor Command')
    except Exception as e:
        return str(e)

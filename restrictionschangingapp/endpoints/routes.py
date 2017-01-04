from flask import Blueprint, request, render_template

BP = Blueprint('ldrrestrictionschanging', __name__, template_folder='templates')

@BP.route("/", methods=["GET", "POST"])
def select_an_object():
    """fill in please
    """
    return render_template("front.html")


@BP.route("/change/<str:objid>", methods=["GET", "POST"])
def make_a_change(objid):
    """fill in please
    """
    if request.method == "POST":
        # get record, load it into pypremis.lib.PremisRecord, get restrictions already present
        # iterate through current restrictions, flip active to False
        # create new restriction node; set active to True
        # append new restriction to restriction list
        # load new restriciton list with new restriction into PremisRecord
        # write premis record to path on-disk
        # return receipt page informing user that restriction has been changed
        return "not implemented yet"
    else:
        return render_template("changeform.hhtml", objectToChange=objid)

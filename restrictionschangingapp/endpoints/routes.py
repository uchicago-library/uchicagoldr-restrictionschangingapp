
from flask import Blueprint, redirect, request, render_template

from pypairtree.utils import identifier_to_path
from pypremis.lib import PremisRecord
from pypremis.nodes import RightsExtension
from uchicagoldrtoolsuite.bit_level.lib.misc.premisextensionnodes import Restriction,\
    RestrictedObjectIdentifier, RightsExtensionIdentifier

BP = Blueprint('ldrrestrictionschanging', __name__, template_folder='templates')

@BP.route("/", methods=["GET", "POST"])
def select_an_object():
    """fill in please
    """
    if request.method == "POST":
        form = request.form
        input_value = form.get("object-id").split("/")
        accessionid = input_value[0]
        objid = input_value[1]
        return redirect("/change/{}/{}".format(accessionid, objid))
    else:
        return render_template("front.html")

@BP.route("/change/<string:accessionid>/<string:objid>", methods=["GET", "POST"])
def make_a_change(accessionid, objid):
    """fill in please
    """
    current_restriction = "R-S"
    current_accession = accessionid
    current_object = "{}/{}".format(current_accession, objid)
    if request.method == "POST":
        form = request.form
        last_restriction = form.get("current-restriction")
        new_restriction = form.get("desired-restriction")
        restriction_comment = form.get("comment")
        rights_ext_id = RightsExtensionIdentifier("DOI", "foo")
        restricted_object = RestrictedObjectIdentifier("DOI", current_object)
        restrict = Restriction(new_restriction, True, restricted_object)
        rights_extension = RightsExtension()
        rights_extension.set_field("rightsExtensionIdentifier", rights_ext_id)
        rights_extension.set_field("restriction", restrict)
        print(rights_extension)
        return render_template("receipt.html", objectChanged=current_object,
                               restrictionComment=restriction_comment,
                               oldRestriction=last_restriction, newRestriction=new_restriction)
    else:
        return render_template("changeform.html", objectToChange=current_object,
                               currentRestriction=current_restriction)

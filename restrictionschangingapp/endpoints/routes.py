
from flask import Blueprint, redirect, request, render_template
from os.path import exists, join
from pypairtree.utils import identifier_to_path
from pypremis.lib import PremisRecord
from pypremis.nodes import Rights, RightsExtension
from uchicagoldrtoolsuite.bit_level.lib.misc.premisextensionnodes import Restriction,\
    RestrictedObjectIdentifier, RightsExtensionIdentifier

BP = Blueprint('ldrrestrictionschanging', __name__, template_folder='templates')

#identifier = "rqrh1jcd8r4w1/fdfc7dec773811e6b4d10025904dfbb0"

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
    from flask import current_app
    root_path = current_app.config.get("LIVEPREMIS_PATH")
    accession_path = str(identifier_to_path(accessionid))
    objid_path = str(identifier_to_path(objid))
    path_to = join(root_path[0], accession_path,
                   "arf/pairtree_root", objid_path, "arf", "premis.xml")
    current_restrictions = []
    if exists(path_to):
        precord = PremisRecord(frompath=path_to)
        for right in precord.get_rights_list():
            extensions = right.get_rightsExtension()
            for extension in extensions:
                restriction = extension.get_field("restriction")
                code = restriction[0].get_field("restrictionCode")
                active = restriction[0].get_field("active")
                print((code, active))
                if active[0] == "True":
                    current_restrictions.append(code[0])
    current_restriction = ','.join(current_restrictions)
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
        restrict.set_field("restrictionComment", restriction_comment.strip())
        rights_extension = RightsExtension()
        rights_extension.set_field("rightsExtensionIdentifier", rights_ext_id)
        rights_extension.set_field("restriction", restrict)
        new_rights_element = Rights(rightsExtension=rights_extension)
        precord.add_rights(new_rights_element)
        precord.write_to_file(path_to)
        return render_template("receipt.html", objectChanged=current_object,
                               restrictionComment=restriction_comment,
                               oldRestriction=last_restriction, newRestriction=new_restriction)
    else:
        return render_template("changeform.html", objectToChange=current_object,
                               currentRestriction=current_restriction)

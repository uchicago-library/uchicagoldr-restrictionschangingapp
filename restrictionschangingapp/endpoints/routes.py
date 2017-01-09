
from uuid import uuid4
from os.path import exists, join
from flask import Blueprint, redirect, request, render_template

from pypairtree.utils import identifier_to_path
from pypremis.lib import PremisRecord
from pypremis.nodes import Rights, RightsExtension
from uchicagoldrtoolsuite.bit_level.lib.misc.premisextensionnodes import Restriction,\
    RestrictedObjectIdentifier, RightsExtensionIdentifier


def make_new_rights_element(extension_id, restricted_object_id, restriction_code,
                            restriction_active, restriction_comment):
    rights_ext_id = RightsExtensionIdentifier("DOI", extension_id)
    restricted_object = RestrictedObjectIdentifier("DOI", restricted_object_id)
    restrict = Restriction(restriction_code, restriction_active, restricted_object)
    restrict.set_restrictionReason(restriction_comment.strip())
    rights_extension = RightsExtension()
    rights_extension.set_field("rightsExtensionIdentifier", rights_ext_id)
    rights_extension.set_field("restriction", restrict)
    new_rights_element = Rights(rightsExtension=rights_extension)
    return new_rights_element

BP = Blueprint('ldrrestrictionschanging', __name__, template_folder='templates')

#identifier = "rqrh1jcd8r4w1/fdfc7dec773811e6b4d10025904dfbb0"
#identifier2 = "rqrh1jcd8r4w1/fdfc60c876bd11e690300025904dfbb0"
#identifer3 = "85z3wb5404q05/f3b3225c96fd11e6a879ac87a336bfd3"
#identifier4 = "przfqp7h034j2/faa74688970211e6afccac87a336bfd3"

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
    print(path_to)
    if exists(path_to):
        precord = PremisRecord(frompath=path_to)
        current_rights = precord.get_rights_list()
        print(current_rights)
        for right in current_rights:
            extensions = right.get_rightsExtension()
            print(right)
            for extension in extensions:
                print(extension)
                restriction = extension.get_field("restriction")
                code = restriction[0].get_field("restrictionCode")
                active = restriction[0].get_field("active")
                active = active[0] if len(active) == 1 else None
                code = code[0] if len(code) == 1 else None
                if active == "True" and code is not None:
                    current_restrictions.append(code)
    current_restriction = ','.join(current_restrictions)
    current_accession = accessionid
    current_object = "{}/{}".format(current_accession, objid)
    if request.method == "POST":
        form = request.form
        last_restriction = form.get("current-restriction")
        new_restriction = form.get("desired-restriction")
        restriction_comment = form.get("comment")
        new_rights = make_new_rights_element(uuid4().hex, current_object,
                                             new_restriction, True, restriction_comment)
        precord = PremisRecord(frompath=path_to)
        old_rights = precord.get_rights_list()
        precord.rights_list = []
        precord.add_rights(new_rights)
        for right in old_rights:
            extensions = right.get_rightsExtension()
            for extension in extensions:
                extension_id = extension.get_field("rightsExtensionIdentifier")[0].\
                    get_field("rightsExtensionIdentifierValue")
                restriction = extension.get_field("restriction")[0]
                active = restriction.get_field("active")[0]
                restricted_object_id = restriction.get_field("restrictedObjectIdentifier")[0].\
                    get_field("restrictedObjectIdentifierValue")
                if active == "True":
                    active = "False"
                try:
                    comment = restriction.get_field("restrictionComment")
                except KeyError:
                    comment = None
                replacement_rights = make_new_rights_element(extension_id, restricted_object_id,
                                                             restriction, active, comment)
                precord.add_rights(replacement_rights)
        precord.write_to_file(path_to)
        return render_template("receipt.html", objectChanged=current_object,
                               restrictionComment=restriction_comment,
                               oldRestriction=last_restriction,
                               newRestriction=form.get("desired_restriction"))
    else:
        return render_template("changeform.html", objectToChange=current_object,
                               currentRestriction=current_restriction)

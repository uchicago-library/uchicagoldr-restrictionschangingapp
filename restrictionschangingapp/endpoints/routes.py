
from uuid import uuid4
from os.path import exists, join
from flask import Blueprint, redirect, request, render_template

from pypairtree.utils import identifier_to_path
from pypremis.lib import PremisRecord
from pypremis.nodes import Rights, RightsExtension
from uchicagoldrtoolsuite.bit_level.lib.misc.premisextensionnodes import Restriction,\
    RestrictedObjectIdentifier, RightsExtensionIdentifier


def make_new_rights_extension_element(extension_id, restricted_object_id, restriction_code,
                                      restriction_active, restriction_comment):
    """a function to generate a rightsExtension element with minimally required data points

    __Args__
    1. extension_id (str): the identifier for the rightsExtension element being created
    2. restricted_object_id (str): the identifier of the object that this rightsExtension describes
    3. restriction_code (str): a SPCL restriction code
    4. restriction_active (str): True or False, a statement about whether the
                                 restriction should be considered active or not
    5. restriction_comment (str): an optional string describing what this restriction is about
    """
    rights_ext_id = RightsExtensionIdentifier("DOI", extension_id)
    restricted_object = RestrictedObjectIdentifier("DOI", restricted_object_id)
    restrict = Restriction(restriction_code, restriction_active, restricted_object)
    if restriction_comment:
        restrict.set_restrictionReason(restriction_comment.strip())
    rights_extension = RightsExtension()
    rights_extension.set_field("rightsExtensionIdentifier", rights_ext_id)
    rights_extension.set_field("restriction", restrict)
    return rights_extension

BP = Blueprint('ldrrestrictionschanging', __name__, template_folder='templates')

@BP.route("/", methods=["GET", "POST"])
def select_an_object():
    """a method to return a form for entering an object to change restrictions of
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
    """a method to process a form to change the active restriction on a particular object
       and change existing restrictions to inactive

    __Args__
    1. accessionid (str): the identifier for a particular accession
    2. objid (str): the identifier for a particular object
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
        current_rights = precord.get_rights_list()
        for right in current_rights:
            extensions = right.get_rightsExtension()
            for extension in extensions:
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
        new_rights_info = make_new_rights_extension_element(uuid4().hex, current_object,
                                                            new_restriction, True,
                                                            restriction_comment)
        precord = PremisRecord(frompath=path_to)
        old_rights = precord.get_rights_list()
        precord.rights_list = []
        precord.add_rights(new_rights_info)
        all_rights = []
        for right in old_rights:
            extensions = right.get_rightsExtension()
            for extension in extensions:
                extension_id = extension.get_field("rightsExtensionIdentifier")[0].\
                    get_field("rightsExtensionIdentifierValue")
                restriction = extension.get_field("restriction")[0]
                code = restriction.get_field("restrictionCode")[0]
                active = restriction.get_field("active")[0]
                restricted_object_id = restriction.get_field("restrictedObjectIdentifier")[0].\
                    get_field("restrictedObjectIdentifierValue")
                if active == "True":
                    active = "False"
                try:
                    comment = restriction.get_field("restrictionComment")
                except KeyError:
                    comment = None
                replacement_rights = make_new_rights_extension_element(extension_id,
                                                                       restricted_object_id,
                                                                       code, active, comment)
                all_rights.append(replacement_rights)
        all_rights.append(new_rights_info)
        new_rights = Rights(rightsExtension=all_rights)
        precord.add_rights(new_rights)
        precord.write_to_file(path_to)
        return render_template("receipt.html", objectChanged=current_object,
                               restrictionComment=restriction_comment,
                               oldRestriction=last_restriction,
                               newRestriction=form.get("desired_restriction"))
    else:
        return render_template("changeform.html", objectToChange=current_object,
                               currentRestriction=current_restriction)

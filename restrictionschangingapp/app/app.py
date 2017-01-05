from configparser import ConfigParser
from flask import Flask

from ..endpoints.routes import BP

def retrieve_resource_string(resource_path, pkg_name=None):
    """
    retrieves the string contents of some package resource
    __Args__
    1. resource_path (str): The path to the resource in the package
    __KWArgs__
    * pkg_name (str): The name of a package. Defaults to the project name
    __Returns__
    * (str): the resource contents
    """
    from pkg_resources import Requirement, resource_string
    if pkg_name is None:
        pkg_name = __name__.split('.')[0]
    return resource_string(Requirement.parse(pkg_name), resource_path)

CONFIG_STR = retrieve_resource_string("config/config.ini").decode("utf-8")
PARSER = ConfigParser()
PARSER.read_string(CONFIG_STR)

APP = Flask(__name__)

for x in PARSER["CONFIG"]:
    v = PARSER["CONFIG"][x]
    APP.config[x.upper()] = v.split(',')

APP.register_blueprint(BP)

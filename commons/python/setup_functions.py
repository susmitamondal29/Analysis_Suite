#!/usr/bin/env python3
from xml.dom.minidom import parse

from .user import analysis_area

def get_analyses():
    xml_filename = (analysis_area/'Analyzer/src/classes_def.xml').resolve()
    if xml_filename.exists():
        xml_classes = parse(str(xml_filename))
        return [c.getAttribute("name") for c in xml_classes.getElementsByTagName('class')]
    else: # For on cluster where xml doesn't exists
        return None

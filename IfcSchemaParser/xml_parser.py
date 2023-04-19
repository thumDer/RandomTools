"""Script to export important data from xml schema
"""
from collections import defaultdict
import os
import io
import csv
import xml.etree.ElementTree as ET


def export_csv(filepath, data):
    with io.open(filepath, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f, dialect="excel", delimiter=";")
        for row in data:
            writer.writerow(row)


tree = ET.parse(os.path.join(os.path.dirname(__file__), 'IFC4x2.xsd'))
root = tree.getroot()

class_dict = {}

for child in root.findall("{http://www.w3.org/2001/XMLSchema}element"):
    parent = child.get("substitutionGroup")
    if not parent:
        continue
    name = child.get("name")
    class_dict[name] = {"parent": parent.replace("ifc:", "")}


for k, v in class_dict.items():
    breadcrumb = ""
    current = k
    while True:
        if not class_dict.get(current): break
        parent = class_dict.get(current).get("parent")
        if not parent:
            break
        breadcrumb = parent + f" > {breadcrumb}"
        current = parent
    class_dict[k]["breadcrumb"] = breadcrumb

interesting_classes = [k for k in class_dict if "IfcElement" in class_dict[k]['breadcrumb']]
# [print(f"{k}, {d[k]['parent']}, {d[k]['breadcrumb']}") for k in d if "IfcElement" in d[k]['breadcrumb']]

enum_dict = defaultdict(list)
for child in root.findall("{http://www.w3.org/2001/XMLSchema}simpleType"):
    enums = child[0].findall("{http://www.w3.org/2001/XMLSchema}enumeration")
    if not enums:
        continue
    for e in enums:
        enum_dict[child.get('name')].append(e.get('value'))
        # print(f"{child.get('name')}, {e.get('value')}")

all_enums = []
all_enum_dict = defaultdict(list)
idx = 0
for child in root.findall("{http://www.w3.org/2001/XMLSchema}complexType"):
    try:
        ext = child[0][0]
    except IndexError:
        continue
    if not ext:
        continue
    if child.get('name') not in interesting_classes:
        continue
    idx += 1
    attributes = ext.findall("{http://www.w3.org/2001/XMLSchema}attribute")
    for a in attributes:
        if a.get("name") == "PredefinedType":
            type_enum = a.get('type').replace('ifc:', '')
            enums = enum_dict.get(type_enum)
            for e in enums:
                all_enum_dict[e].append(child.get('name'))
                all_enums.append((e, type_enum, child.get('name')))
            # print(f"{idx}, {child.get('name')}, {type_enum}, {enum_dict.get(type_enum)}")


filepath = os.path.join(os.path.dirname(__file__), 'enums.csv')
data = []
idx = 0
for e in all_enums:
    # if e[0] == 'notdefined' or e[0] == 'userdefined':
    #     continue
    data.append(e)
    # print(idx, *e)
    idx += 1

export_csv(filepath, data)

filepath = os.path.join(os.path.dirname(__file__), 'all_enums.csv')
data = []
for k, v in all_enum_dict.items():
    data.append((k, str.join(", ", v)))
    # print(f"{k}: {v}")

export_csv(filepath, data)


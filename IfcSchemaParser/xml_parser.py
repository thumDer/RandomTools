import xml.etree.ElementTree as ET
tree = ET.parse('IFC4x2.xsd')
root = tree.getroot()

d = {}

for child in root.findall("{http://www.w3.org/2001/XMLSchema}element"):
    parent = child.get("substitutionGroup")
    if not parent:
        continue
    name = child.get("name")
    d[name] = {"parent": parent.replace("ifc:", "")}


for k in d:
    breadcrumb = ""
    current = k
    while True:
        if not d.get(current): break
        parent = d.get(current).get("parent")
        if not parent:
            break
        breadcrumb = parent + f" > {breadcrumb}"
        current = parent
    d[k]["breadcrumb"] = breadcrumb

[print(f"{k}, {d[k]['parent']}, {d[k]['breadcrumb']}") for k in d if "IfcElement" in d[k]['breadcrumb']]
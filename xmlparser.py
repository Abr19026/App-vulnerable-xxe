# Usando la minido
# import xml.dom.minidom as xmldom;
# documento = xmldom.parse("test.xml")
# print(documento.toprettyxml("utf-8"));

# import xml.etree.ElementTree as ET
# documento = ET.parse("test.xml")
# salida = ET.tostring(documento.getroot(),encoding="utf8").decode("utf-8");
# print(salida);

# python -m pip install lxml 
# parser mas avanzado que permite parsear entidades externas
from lxml import etree
documento = etree.parse("test.xml")
salida = etree.tostring(documento.getroot(),encoding="utf8").decode("utf-8");
print(salida);


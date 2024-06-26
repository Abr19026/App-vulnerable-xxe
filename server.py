from http.server import HTTPServer, BaseHTTPRequestHandler
# Es necesario instalar el paquete lxml
import lxml.etree as ET
import lxml.html as EHT 

prefijoDatos = "data/"
prefijo_htmls = "www/"
# necesario para que expanda entidades y lea desde la red
parser = ET.XMLParser(load_dtd=True, resolve_entities=True,no_network=False)

# Función para verificar las credenciales del usuario
def verificar_credenciales(usuario, contraseña):
    with open(f"{prefijoDatos}contrasenas.txt", "r") as file:
        for line in file:
            u, p = line.strip().split()
            if u == usuario and p == contraseña:
                return True
    return False

# Función para obtener los datos del perfil
def obtener_datos_perfil(Nombre):
    tree = ET.parse(f"{prefijoDatos}perfiles.xml", parser)
    root = tree.getroot()
    for perfil in root.findall('perfil'):
        if perfil.find('Nombre').text == Nombre:
            return perfil
    return None

# Función para actualizar los datos del perfil
def actualizar_datos_perfil(Nombre, datos_xml):
    tree = ET.parse(f"{prefijoDatos}perfiles.xml", parser)
    root = tree.getroot()
    for perfil in root.findall('perfil'):
        if perfil.find('Nombre').text == Nombre:
            root.remove(perfil)
            root.append(datos_xml)
            tree.write(f"{prefijoDatos}perfiles.xml")
            return True
    return False

def verificar_cookies(cookie:str):
    cookies = {}
    for cookiepair in cookie.split("; "):
        cookiename, value = cookiepair.split("=")
        cookies[cookiename] = value
    if(verificar_credenciales(cookies["username"], cookies["password"])):
        return obtener_datos_perfil(cookies["username"])
    return None

class ManejadorDePedidos(BaseHTTPRequestHandler):
    def do_GET(self):
        try:
            parsed_url = self.path.split('?')
            recurso = parsed_url[0]
            cookies = self.headers.get('Cookie')

            if recurso == '/' or recurso == '/login':
                # Si las cookies son válidas, redireccionar a la página de perfil
                if(cookies is not None and verificar_cookies(cookies)):
                    self.send_response(302)
                    self.send_header("Location", "/perfil")
                    self.end_headers()
                else:
                    # Si no, enviar la página de inicio de sesión
                    self.send_response(200)
                    self.send_header("Content-type", "text/html")
                    self.end_headers()
                    with open(f"{prefijo_htmls}login.html", "rb") as file:
                        self.wfile.write(file.read())

            elif recurso == '/perfil':
                # Si hay cookies válidas, enviar la página de perfil con los datos correspondientes
                if(cookies and (datos_perfil := verificar_cookies(cookies)) != None):
                    self.send_response(200)
                    self.send_header("Content-type", "text/html")
                    self.end_headers()
                    # obtiene datos del perfil
                    Nombre = datos_perfil.find("Nombre").text
                    Apellidos =datos_perfil.find("Apellidos").text
                    # obtiene plantilla de perfil
                    plantillaHTML = EHT.parse(f"{prefijo_htmls}perfil.html")
                    plantillaHTML.getroot().get_element_by_id("nombre").text = Nombre
                    plantillaHTML.getroot().get_element_by_id("apellidos").text = Apellidos
                    self.wfile.write(EHT.tostring(plantillaHTML))
                else:
                    # redirecciona a /login
                    self.send_response(302)
                    self.send_header("Location", "/login")
                    self.end_headers()
        except Exception as x:
            self.send_response(500)
            self.end_headers()
            self.wfile.write(bytes(str(x),"utf-8"))
            raise x

    def do_POST(self):
        try:
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length)
            cookies = self.headers.get('Cookie')

            # si el recurso es login
            if self.path == '/login':
                # Lee datos xml
                datos_xml = ET.fromstring(post_data, parser)

                # valida que exista usuario y contraseña
                usuario = datos_xml.find("username").text
                contraseña = datos_xml.find("password").text
                if(usuario is None or contraseña is None):
                    raise Exception("XML inválido");

                # si las credenciales son correctas establece cookies y manda éxito
                if verificar_credenciales(usuario, contraseña):
                    self.send_response(200)
                    #place Establece cookies
                    self.send_header('Set-Cookie', f"username={usuario}")
                    self.send_header('Set-Cookie', f"password={contraseña}")
                    # redirecciona a perfil
                    self.end_headers()
                # en otro caso Manda error de autorización
                else:
                    print(ET.tostring(datos_xml))
                    self.send_response(401)
                    self.end_headers()

            elif self.path == '/perfil':
                # Si hay cookies válidas, actualizar los datos del perfil
                if(usuario := verificar_cookies(cookies)):
                    # Lee datos xml
                    datos_xml = ET.fromstring(post_data, parser)
                    # Extrae usuario de la cookie
                    usuario_real = usuario.find("Nombre").text
                    # Valida exista Nombre y Apellidos
                    Nombre = datos_xml.find("Nombre").text
                    Apellidos = datos_xml.find("Apellidos").text
                    if(Nombre is None or Apellidos is None):
                        raise Exception("XML inválido");
                    # Valida Nombre de usuario no cambie (porque es el id)
                    if(Nombre != usuario_real):
                        self.send_response(400)
                        self.end_headers()
                    # actualiza datos del perfil
                    if actualizar_datos_perfil(usuario_real, datos_xml):
                        self.send_response(200)
                        self.end_headers()
                    else:
                        raise Exception("No se actualizaron los datos del perfil")
                # Si no, enviar un error de autorización
                else:
                    self.send_response(401)
                    self.end_headers()
        except Exception as x:
            self.send_response(500)
            self.end_headers()
            self.wfile.write(bytes(str(x),"utf-8"))
            raise x

if __name__ == '__main__':
    puerto = '', 8000
    httpd = HTTPServer(puerto, ManejadorDePedidos)
    print(f'Servidor corriendo en el puerto {puerto}...')
    httpd.serve_forever()
    httpd.server_close()
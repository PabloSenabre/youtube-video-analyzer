from google_auth_oauthlib.flow import Flow
from google.oauth2.credentials import Credentials

# Inicia el flujo de autorización
flow = Flow.from_client_secrets_file(
    'credentials.json',
    scopes=['https://www.googleapis.com/auth/drive.file'],
    redirect_uri='urn:ietf:wg:oauth:2.0:oob'
)

# Genera la URL de autorización
auth_url, _ = flow.authorization_url(prompt='consent')

print(f"Por favor, visita esta URL para autorizar la aplicación: {auth_url}")
print("Después de autorizar, se te mostrará un código. Copia ese código y pégalo aquí.")

# Espera a que el usuario introduzca el código de autorización
code = input("Introduce el código de autorización: ")

# Intercambia el código por credenciales
flow.fetch_token(code=code)

# Guarda las credenciales
credentials = flow.credentials
with open('token.json', 'w') as token:
    token.write(credentials.to_json())

print("Token guardado en 'token.json'")
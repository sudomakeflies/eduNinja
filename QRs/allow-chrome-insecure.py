import qrcode
import os

# URL para permitir certificados no válidos en localhost en Chrome
url = "chrome://flags/#allow-insecure-localhost"

# Generar el código QR
qr = qrcode.QRCode(
    version=1,
    error_correction=qrcode.constants.ERROR_CORRECT_L,
    box_size=10,
    border=4,
)
qr.add_data(url)
qr.make(fit=True)

# Crear una imagen del código QR
img = qr.make_image(fill='black', back_color='white')

# Guardar la imagen en el directorio actual
output_path = os.path.join(os.getcwd(), "allow_insecure_localhost_qr.png")
img.save(output_path)

output_path


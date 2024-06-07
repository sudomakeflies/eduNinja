import qrcode
import matplotlib.pyplot as plt

# Data to encode
data = "https://192.168.0.103:8000/api/"

# Creating an instance of QRCode
qr = qrcode.QRCode(
    version=1,
    error_correction=qrcode.constants.ERROR_CORRECT_L,
    box_size=10,
    border=4,
)

# Add data to the instance
qr.add_data(data)
qr.make(fit=True)

# Create an image
img = qr.make_image(fill='black', back_color='white')

# Save the image file
img_path = "/mnt/data/qr_code.png"
img.save(img_path)

# Display the QR code
plt.imshow(img, cmap='gray')
plt.axis('off')
plt.show()

img_path

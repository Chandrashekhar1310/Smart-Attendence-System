import qrcode

# Open the text file
with open("student.txt", "r") as file:
    # Read each line of the file
    lines = file.readlines()
    # Loop through each line
    for line in lines:
        # Generate a QR code for each line
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_L,
            box_size=10,
            border=4,
        )
        qr.add_data(line)
        qr.make(fit=True)
        img = qr.make_image(fill_color="black", back_color="white")
        # Save the QR code as an image file
        img.save("qr_code_{}.png".format(lines.index(line)))
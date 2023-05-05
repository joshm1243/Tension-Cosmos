from PIL import Image

def PLM_SA_SAMPLE(prompt):    
    filename = "./services/samples/outputs/" + prompt + "/2.png"
    image = Image.open(filename)

    resized_image = image.resize((50,50))

    pixel_values = list(resized_image.getdata())

    # Convert pixel values to hex codes
    hex_codes = [f"#{p[0]:02X}{p[1]:02X}{p[2]:02X}" for p in pixel_values]

    return hex_codes

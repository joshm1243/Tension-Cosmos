from PIL import Image
import json
import os
import shutil

def PLM_SA_RENDER(samples):

    ## Removing and renewing the renders directory if it exists
    if os.path.exists("./services/samples/renders"):
        shutil.rmtree("./services/samples/renders")
    os.mkdir("./services/samples/renders")

    for sample in samples:

        if "location" in sample:
            

            prompt = sample["location"] + "_" + sample["environment"] + "_" + sample["time_of_day"] + "_" + sample["emotion_1"] + "_" + sample["emotion_2"]
            directory_path = "./services/samples/renders/" + prompt

            if not os.path.exists(directory_path):
                os.mkdir(directory_path)

            grid = json.loads(sample["grid"])
            image = Image.new("RGB", (10,10))

            for x in range(10):
                for y in range(10):

                    red = int(grid[y][x][1:3],16)
                    green = int(grid[y][x][3:5],16)
                    blue = int(grid[y][x][5:7],16)


                    image.putpixel((x,y),(red,green,blue))

                    resized_image = image.resize((128,128), resample=Image.NEAREST)

            filename = directory_path + "/" + str(sample["sample_id"])
            resized_image.save(filename + ".png","PNG")
            file = open(filename + ".txt","w")
            file.write(prompt)
            file.close()

        else:
            print("Not")



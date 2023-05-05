

def PLM_SC_BLOCK(tagged_script):

    blocks = []

    ## Finding First Location
    initial_location = "place"
    for line in tagged_script:
        location_instances = line["elements"]["location"]
        if len(location_instances) > 0:
            initial_location = location_instances[0]["location"]
            break

    ## Finding First Environment
    initial_environment = "inside"
    for line in tagged_script:
        environment_instances = line["elements"]["environment"]
        if len(environment_instances) > 0:
            initial_environment = environment_instances[0]["environment"]
            break
    
    ## Finding First Time Of Day
    initial_time_of_day = "day"
    for line in tagged_script:
        time_of_day_instances = line["elements"]["time_of_day"]
        if len(time_of_day_instances) > 0:
            initial_time_of_day = time_of_day_instances[0]["time_of_day"]
            break
    
    ## Finding First Emotions
    initial_emotions = ["contentment"]
    for line in tagged_script:
        emotion_instances = line["elements"]["emotion"]
        if len(emotion_instances) > 0:
            initial_emotions = emotion_instances[0]["emotions"]
            break
    
    ## Creating the first block
    blocks.append({
        "line_number" : 0,
        "location" : initial_location,
        "environment" : initial_environment,
        "time_of_day" : initial_time_of_day,
        "emotions" : initial_emotions
    })

    for line_number, line in enumerate(tagged_script):

        ## Skipping over the first line due to already finding the initial elements
        if line_number == 0:
            continue
        else:

            block = {"line_number" : line_number}

            ## Creating a new location block
            location_instances = line["elements"]["location"]
            if len(location_instances) > 0:
                block["location"] = location_instances[0]["location"]
            else:
                block["location"] = blocks[-1]["location"]

            ## Creating a new environment block
            environment_instances = line["elements"]["environment"]
            if len(environment_instances) > 0:
                block["environment"] = environment_instances[0]["environment"]
            else:
                block["environment"] = blocks[-1]["environment"]

            ## Creating a new time_of_day block
            time_of_day_instances = line["elements"]["time_of_day"]
            if len(time_of_day_instances) > 0:
                block["time_of_day"] = time_of_day_instances[0]["time_of_day"]
            else:
                block["time_of_day"] = blocks[-1]["time_of_day"]

            ## Creating a new emotions block
            emotion_instances = line["elements"]["emotion"]
            if len(emotion_instances) > 0:
                block["emotions"] = emotion_instances[0]["emotions"]
            else:
                block["emotions"] = blocks[-1]["emotions"]

            blocks.append(block)

    
    block_number = 1
    while block_number < len(blocks):

        if blocks[block_number]["location"] == blocks[block_number - 1]["location"] and blocks[block_number]["environment"] == blocks[block_number - 1]["environment"]:
            if blocks[block_number]["time_of_day"] == blocks[block_number - 1]["time_of_day"] and blocks[block_number]["emotions"] == blocks[block_number - 1]["emotions"]:
                blocks.pop(block_number)
            else:
                block_number += 1
        else:
            block_number += 1

    blocked_script = []

    for block_number, block in enumerate(blocks):

        ## Calculating the start line for the block
        starting_line = block["line_number"]

        ## Calculating the end line for the block 
        if block_number == len(blocks) - 1:
            ending_line = len(tagged_script) - 1
        else:
            ending_line = blocks[block_number + 1]["line_number"] - 1
        
        blocked_script.append({
            "block_id" : block_number,
            "lines" : tagged_script[starting_line:ending_line + 1],
            "prompt_elements" : {
                "location" : block["location"],
                "environment" : block["environment"],
                "time_of_day" : block["time_of_day"],
                "emotions" : block["emotions"]
            }
        })
    
    return {"blocks" : blocked_script}

   

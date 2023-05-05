def PLM_SC_CLEAN(script_contents):
    script_contents = script_contents.replace("\\r","\n")
    script_contents = script_contents.replace("\\n","\n")
    script_contents = script_contents.replace("\\","")
    script_contents = script_contents.replace('"','')
    script_contents = script_contents.split("\n")

    ## Creating an object for each line and numbering
    raw_script = []

    line_number = 0
    for line_text in script_contents:
        if line_text != "":
            raw_script.append({
                "line_id" : line_number,
                "line_number" : line_number + 1,
                "text" : line_text
            })
            line_number += 1

    return raw_script
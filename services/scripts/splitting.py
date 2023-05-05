def PLM_SC_SPLIT_LOC(tagged_script):

    ## Split based on location
    script = []
    section = []
    for tagged_line in tagged_script:
        if tagged_line["tag"] == "location":
            script.append(section)
            section = []
        section.append(tagged_line)
    return script
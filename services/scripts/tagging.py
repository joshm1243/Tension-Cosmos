import pickle
model = pickle.load(open("./../../plm_script_line_type.pkl","rb"))

def PLM_SC_TAG(lines):

    lines_text = [line["text"] for line in lines]
    predicted_tags = model.predict(lines_text)

    for line, tag in zip(lines, predicted_tags):
        
        if tag == "location":
            line["type_code"] = "LOC"
            line["type_tag"] = "Location"
        elif tag == "dialogue":
            line["type_code"] = "DLG"
            line["type_tag"] = "Dialogue"
        elif tag == "action":
            line["type_code"] = "ATN"
            line["type_tag"] = "Action"
        elif tag == "lighting":
            line["type_code"] = "LGH"
            line["type_tag"] = "Lighting"
        elif tag == "change":
            line["type_code"] = "CNG"
            line["type_tag"] = "Change"
        elif tag == "title":
            line["type_code"] = "TTL"
            line["type_tag"] = "Title"
        elif tag == "character":
            line["type_code"] = "CHR"
            line["type_tag"] = "Character"
        elif tag == "act":
            line["type_code"] = "ACT"
            line["type_tag"] = "Act"
        elif tag == "scene":
            line["type_code"] = "SCE"
            line["type_tag"] = "Scene"
        else:
            line["type_code"] = "END"
            line["type_tag"] = "End"

    return lines
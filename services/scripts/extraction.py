import re
import TensionCorpus as TCPS
import nltk
import empath

def PLM_SC_EXT_PREPARE(tagged_script):

    for line in tagged_script:
        line["elements"] = {}
     

    return tagged_script

def PLM_SC_EXT_CREATE_TRACK(tagged_script):

    element_precedence = ["location","environment","time_of_day","emotion","character"]

    for line in tagged_script:
        
        track_instances = []

        instances = []
        for element_type in element_precedence:
            instances.extend(line["elements"][element_type])

        for instance in instances:
            overlaps = False
            for track_instance in track_instances:

                if instance["start_position"] <= track_instance["end_position"]:
                    if track_instance["start_position"] <= instance["end_position"]:
                        overlaps = True
                        break
            
            if not overlaps:
                track_instances.append(instance)
        
        ## Piecing together the parts of the script along with the text
        ## Firstly sorting the instances by their start positions
        track_instances.sort(key=lambda instance: instance["start_position"])

        line["track"] = []

        next_starting_position = 0
        for track_instance in track_instances:

            if track_instance["start_position"] > 0:
                ## Adding the section of text before the track instance
                line["track"].append({
                    "type" : ".",
                    "start_position" : next_starting_position,
                    "end_position" : track_instance["start_position"] - 1,
                    "text" : line["text"][next_starting_position:track_instance["start_position"]],
                })

            ## Adding the current section of text during the track instance
            track_instance["text"] = line["text"][track_instance["start_position"]:track_instance["end_position"] + 1]
            line["track"].append(track_instance)

            ## Setting the next instance to start at the end of the current one
            next_starting_position = track_instance["end_position"] + 1

        line["track"].append({
            "start_position" : next_starting_position,
            "end_position" : len(line["text"]) - 1,
            "text" : line["text"][next_starting_position:len(line["text"])],
            "type" : "."
        })            

    return tagged_script


def PLM_SC_EXT_CHARACTER(tagged_script):

    for line in tagged_script:
        line["elements"]["character"] = []

    ## 
    pattern = re.compile("(^|\s)(" + "|".join([name.lower() + "(:?|,?|\.?|\)|\!|\??)" for name in TCPS.names]) + ")(?=(\s|$))",re.IGNORECASE)
    allowed_type_codes = ["LOC","DLG","ATN","LGH","CHR","CNG"]

    ## Create a list of all the lines which should be checked for character names
    character_lines = [line for line in tagged_script if line["type_code"] in allowed_type_codes]

    ## For each of the lines that should be checked for characters, search for names against the Name Corpus
    names = []
    for line in character_lines:
        matches = pattern.finditer(line["text"])
        for match in matches:
            names.append(match.group().strip())

    ## Finding out the most common formatting in the group of names found
    ## For example, if most names are formatted 'NAME:' or 'NAME.' all other names can be removed

    ## Defining a list of suffixes the solution recognises
    suffix_codes = {":": "COLON", ")": "BRACKET", ".": "FULL_STOP", ",": "COMMA", "!": "EXCLAMATION_MARK", "?": "QUESTION_MARK"}
    character_format_codes = []

    for name in names:

        ## A formatting code will be created for each name
        ## Firstly, adding the case code of the name
        format_code = "LOWER" if name.islower() else "UPPER" if name.isupper() else "TITLE"
        format_code += "_"

        ## Next, adding the suffix code at the end of the name
        ## A name without a suffix will have 'EMPTY' placed in the suffix column
        if name[-1] not in suffix_codes:
            format_code += "EMPTY"
        else:
            format_code += suffix_codes[name[-1]]

        character_format_codes.append({
            "name" : name,
            "format_code" : format_code
        })

    ## If there is at least one found name
    if len(names) > 0:

        ## Each name will now have a format code such as 'UPPER_EMPTY' or 'TITLE_COLON'
        ## The solution then works out the most popular method of displaying names
        ## Creating a list containing just the format codes
        format_codes = [character_format_code["format_code"] for character_format_code in character_format_codes]
        most_common_format_code = max(set(format_codes),key=format_codes.count)

        ## Names is now a new empty list, and will contain the predicted names that adhere to common formatting
        names = []

        ## For each of the potential character names, remove the ones that don't adhere to the most common formatting
        for character_format_code in character_format_codes:
            name = character_format_code["name"].lower()
            format_code = character_format_code["format_code"]

            ## If the character name has a suffix on the end, remove it
            ## If the character name has a space at the start, remove it
            if format_code == most_common_format_code:

                if name[-1] in suffix_codes:
                    name = name[0:-1]
                if name[0] == " ":
                    name = name[1:]

                names.append(name)
        
        ## Make a list containing the unique character names in the script
        names = list(set(names))

        ## A pattern that matches a predicted name, followed by a specific suffix
        ## The pattern ensures that names are standalone words rather than a part of another word
        pattern = re.compile("(^|\s)(" + "|".join([name.lower() + "(:?|,?|\.?|\)|\!|\??)" for name in names]) + ")(?=(\s|$))",re.IGNORECASE)

        for line in character_lines:
        
            matches = pattern.finditer(line["text"])

            ## For each of the found names in the line
            for match in matches:
                name = match.group().lower()

                start_position = match.start()
                end_position = match.end()

                ## Removing the starting space, or the ending suffix if the matched name has one
                if name[-1] in suffix_codes:
                    name = name[0:-1]
                    end_position -= 1
                if name[0] == " ":
                    name = name[1:]
                    start_position += 1

                ## Adding the character instance to the elements array
                line["elements"]["character"].append({
                    "type" : "character",
                    "start_position" : start_position,
                    "end_position" : end_position - 1,
                    "character_name" : name.title(),
                    "character_id" : names.index(name)
                })

    return tagged_script

def PLM_SC_EXT_LOCATION(tagged_script):

    for line in tagged_script:
        line["elements"]["location"] = []

    allowed_type_codes = ["LOC","DLG","ATN","CNG"]

    ## Create a list of all the location lines which should be checked for locations
    location_lines = [line for line in tagged_script if line["type_code"] in allowed_type_codes]



    ## For each line which should be checked for location
    for line in location_lines:

        ## A list for each of the found locations in the line
        locations = []

        
        ## If the line has been tagged as location, each word will be checked against the hypernym tree
        if line["type_code"] == "LOC":

            pass
    
        
        else:

            ## Tagging each word with a Part Of Speech (POS) tag
            tokens = nltk.word_tokenize(line["text"])
            tagged_words = nltk.pos_tag(tokens)

            ## Defining a grammar which can be used to pick out a location after a preposition
            grammar = r"""
                LOCATION: {(<VBD><TO><DT|PRP\$><NN>+)|(<VBP><IN><JJ>*<NN>+)|(<IN><DT|PRP\$><JJ>*<NN>+)}
            """

            ## Creating a syntax tree to find the 'LOCATION' grammar within the line
            semantic_tree = nltk.RegexpParser(grammar).parse(tagged_words)

            for subtree in semantic_tree.subtrees():

                ## If a 'LOCATION' has been found in the line
                if subtree.label() == "LOCATION":
                    leaves = subtree.leaves()

                    ## The leaves will also contain the preposition before the location nouns
                    ## Therefore, the nouns are extracted from the sentence and are joined with an underscore
                    nouns = [word[0] for word in leaves if word[1] == "NN"]
                    joined_nouns = "_".join(nouns)
                    nouns = " ".join(nouns)

                    locations.append({
                        "joined_nouns" : joined_nouns,
                        "nouns" : nouns
                    })
        
        
        ## Creating a list of higher-level synsets, each which contain words relating to location
        location_synset_names = ["aquifer.n.01","beach.n.01","cave.n.01","cliff.n.01","lakefront.n.01","oceanfront.n.01","ridge.n.03","ridge.n.04","shore.n.01","spring.n.03","volcanic_crater.n.01","water.n.01","body_of_water.n.01","landscape.n.01","ice.n.02","moon.n.02","wall.n.02","web.n.01","minor_planet.n.01","planet.n.01","planet.n.03","quasar.n.01","satellite.n.03","star.n.01","star.n.03","meteorite.n.01","comet.n.01","nature.n.03","airfield.n.01","arboretum.n.01","athletic_facility.n.01","backroom.n.01","cafeteria_facility.n.01","course.n.09","depository.n.01","drive-in.n.01","forum.n.02","menagerie.n.02","military_installation.n.01","range.n.05","recreational_facility.n.01","source.n.04","station.n.01","facility.n.01","facility.n.04","conveyance.n.03","elevator.n.01","base.n.14","earth.n.04","home.n.03","jungle.n.01","outer_space.n.01","path.n.04","aerospace.n.01","air.n.02","atmosphere.n.03","black_hole.n.01","deep_space.n.01","eden.n.01","hell.n.01","arena.n.02","disaster_area.n.01","neighborhood.n.04","no_man's_land.n.01","resort_area.n.01","retreat.n.01","shrubbery.n.01","space.n.03","domain.n.02","field.n.03","field.n.11","geographical_area.n.01","cavity.n.02","enclosure.n.03","expanse.n.03","hole.n.04","void.n.02","airdock.n.01","altar.n.02","arcade.n.02","arch.n.04","balcony.n.01","balcony.n.02","bridge.n.01","building.n.01","building_complex.n.01","defensive_structure.n.01","door.n.04","establishment.n.04","fountain.n.01","honeycomb.n.01","housing.n.01","hull.n.06","memorial.n.03","mound.n.04","platform.n.04","porch.n.01","prefab.n.01","public_works.n.01","shelter.n.01","stadium.n.01","superstructure.n.01","wind_tunnel.n.01","beachfront.n.01","cape.n.01","coastal_plain.n.01","forest.n.02","peninsula.n.01","wonderland.n.01","aisle.n.03","auditorium.n.01","baggage_claim.n.01","box.n.07","breakfast_area.n.01","bullpen.n.01","chancel.n.01","court.n.10","dining_area.n.01","enclosure.n.01","nave.n.01","orchestra_pit.n.01","patio.n.01","pit.n.06","pit.n.07","press_gallery.n.01","quad.n.04","room.n.01","storage_space.n.01","lane.n.01","passage.n.03","path.n.02","road.n.01","stairway.n.01","watercourse.n.03"]
        location_synsets = [nltk.corpus.wordnet.synset(synset_name) for synset_name in location_synset_names]

        corpus_locations = []

        ## For each of the current predicted locations
        for location in locations:

            found_location = False

            ## Get a list of synsets where the current location is included
            synsets = nltk.corpus.wordnet.synsets(location["joined_nouns"])
            for synset in synsets:
                
                ## For each of these synsets, check if it stems from a higher-level synset relating to location
                for hypernym_path in synset.hypernym_paths():

                    ## If any of the hypernym synsets in the path belong to a location synset, add the noun to the list of known locations
                    if any(hypernym_synset in location_synsets for hypernym_synset in hypernym_path):
                        corpus_locations.append(location["nouns"])
                        found_location = True
                        break
                
                if found_location:
                    break
        
        ## Find the locations within the current line

        start_positions = []

        for location in corpus_locations:

            search_begin_position = line["text"].find(location)
            while search_begin_position in start_positions:
                search_begin_position = line["text"].find(location) + 1

            start_position = line["text"].find(location,search_begin_position)
            end_position = start_position + len(location) - 1

            start_positions.append(start_position)

            line["elements"]["location"].append({
                "type" : "location",
                "start_position" : start_position,
                "end_position" : end_position,
                "location" : location 
            })

    return tagged_script

def PLM_SC_EXT_EMOTION(tagged_script):

    for line in tagged_script:
        line["elements"]["emotion"] = []

    allowed_type_codes = ["DLG","ATN"]

    ## Create a list of all the atmosphere lines which should be checked for atmosphere
    emotion_lines = [line for line in tagged_script if line["type_code"] in allowed_type_codes]

    for line in emotion_lines:

        empath_instance = empath.Empath()

        emotions_to_check = ["hate","cheerfulness","agression","envy","anticipation","nervousness","weakness","horror","suffering","ridicule","optimism","fear","celebration","violence","neglect","love","sympathy","politeness","disgust","rage","warmth","fun","emotional","joy","affection","shame","anger","disappointment","pain","timidity","achievement","contentment"]

        match_start_position = 0
        for word in line["text"].split(" "):

            word_emotions = empath_instance.analyze(word, normalize=True)

            if word_emotions is not None:

                felt_emotions = {}
                for emotion in word_emotions:
                    if emotion in emotions_to_check:
                        if word_emotions[emotion] == 1:
                            felt_emotions[emotion] = word_emotions[emotion]
            
                if len(felt_emotions) > 0:
                    emotions = []
                    for emotion in felt_emotions:
                        emotions.append(emotion)
                    
                        
                    start_position = line["text"].find(word,match_start_position)
                    end_position = start_position + len(word) - 1
                    match_start_position = end_position + 1

                    line["elements"]["emotion"].append({
                        "start_position" : start_position,
                        "end_position" : end_position,
                        "emotions" : emotions,
                        "type" : "emotion"
                    })
        

    return tagged_script

def PLM_SC_EXT_TOD(tagged_script):

    for line in tagged_script:
        line["elements"]["time_of_day"] = []

    allowed_type_codes = ["LOC"]

    ## Create a list of all the atmosphere lines which should be checked for atmosphere
    tod_lines = [line for line in tagged_script if line["type_code"] in allowed_type_codes]

    pattern = re.compile("(^|\s)(" + "|".join([tod + "(:?|\.?)" for tod in TCPS.times_of_day]) + ")(?=(\s|$))",re.IGNORECASE)

    for line in tod_lines:

        matches = pattern.finditer(line["text"])

        ## For each of the found names in the line
        for match in matches:
            tod = match.group().lower()
            start_position = match.start()
            end_position = match.end()

            if tod[-1] in [":","."]:
                tod = tod[0:-1]
                end_position -= 1
            if tod[0] == " ":
                tod = tod[1:]
                start_position += 1

            line["elements"]["time_of_day"].append({
                "start_position" : start_position,
                "end_position" : end_position - 1,
                "time_of_day" : tod,
                "type" : "time_of_day"
            })

    return tagged_script         


def PLM_SC_EXT_ENVIRONMENT(tagged_script):

    for line in tagged_script:
        line["elements"]["environment"] = []

    allowed_type_codes = ["LOC"]

    ## Create a list of all the atmosphere lines which should be checked for atmosphere
    environment_lines = [line for line in tagged_script if line["type_code"] in allowed_type_codes]

    inside_pattern = re.compile("(^|\s)(" + "|".join([tod + "(:?|\.?)" for tod in TCPS.inside_prefixes]) + ")(?=(\s|$))",re.IGNORECASE)
    outside_pattern = re.compile("(^|\s)(" + "|".join([tod + "(:?|\.?)" for tod in TCPS.outside_prefixes]) + ")(?=(\s|$))",re.IGNORECASE)

    for line in environment_lines:

        inside_matches = inside_pattern.finditer(line["text"])
        outside_matches = outside_pattern.finditer(line["text"])

        for match in outside_matches:
            matched_text = match.group().lower()
            start_position = match.start()
            end_position = match.end()

            if matched_text[-1] in [":","."]:
                matched_text = matched_text[0:-1]
                end_position -= 1
            if matched_text[0] == " ":
                matched_text = matched_text[1:]
                start_position += 1
 
            line["elements"]["environment"].append({
                "start_position" : start_position,
                "end_position" : end_position - 1,
                "environment" : "outside",
                "matched_text" : matched_text,
                "type" : "environment"
            })

        for match in inside_matches:
            matched_text = match.group().lower()
            start_position = match.start()
            end_position = match.end()

            if matched_text[-1] in [":","."]:
                matched_text = matched_text[0:-1]
                end_position -= 1
            if matched_text[0] == " ":
                matched_text = matched_text[1:]
                start_position += 1
 
            line["elements"]["environment"].append({
                "start_position" : start_position,
                "end_position" : end_position - 1,
                "environment" : "inside",
                "matched_text" : matched_text,
                "type" : "environment"
            })

    return tagged_script         



    

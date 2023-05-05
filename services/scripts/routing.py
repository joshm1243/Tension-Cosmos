## The Tension Prompt Routing System (TPRS)

from services.samples.generate import PLM_SA_GENERATE

def PLM_SC_ROUTE_BLOCKS(blocked_script):

    script_blocks = blocked_script["blocks"]
    for script_block in script_blocks:
        print(script_block["prompt_elements"])

    return blocked_script
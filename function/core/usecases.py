import re
from string import Template

def get_dashboard_id_from_url(url: str) -> str:
    """
    Retrieves a dashboard ID from a Looker dashboard URL

    Args:
        url (str): Looker URL to retrieve Dashboard ID from

    Returns:
        Str: Dashboard ID that it retrieved
    """

    pattern = r"dashboards\/(.*)\?"

    results = re.findall(pattern, url)
    return results[0]

def load_prompt_from_string(txt_string):
    """
    Loads a prompt from a string into a Template

    Args:
        txt_string (str): Text string to load in
    
    Return:
        Template: Template string it created
    """
    return Template(txt_string)

def generate_prompts_from_queries(looker, queries, prompt_template) -> list:
    """
    Generated prompts from the results of each query.

    Args:
        looker (Looker): Looker object to call for data
        queries (List[Dict]): List of queries to run
        prompt_template (Template): Template for the prompts to take on.

    Return:
        List(str): Returns list of strings containing the prompts
    """
    prompts = []
    for query in queries:
        tile_data = looker.run_inline_query(query)
        title = tile_data.split(",")[0]

        prompt_template_vars = {
            "description": query.get("description", ""),
            "title": title,
            "note": query.get("note", ""),
            "fields": ",".join(query.get("fields", [])),
            "tile_data": tile_data
        }
        prompt = load_prompt_from_string(prompt_template).substitute(**prompt_template_vars)
        prompts.append(prompt)
    return prompts


def convert_dict_to_text(dict_input: dict, key_order: list = None) -> str:
    """Converts a dictionary to a text format

    Args:
        dict_input (dict): 
            The dictionary to convert.
        key_order (list, optional): 
            The order of the keys to process. Defaults to None.
    """
    keys_to_process = key_order if key_order else dict_input.keys()

    formatted_str = ""
    for key in keys_to_process:
        # For the next steps paragraph, we would like to make it into a more overviewable list
        if key == "next_steps":
            formatted_str += f"{key.replace('_', ' ').title()}:\n"
            # Split into bullet points if multiple sentences
            steps = dict_input[key].split(". ")
            formatted_str += "\n".join(f"- {step.strip()}" for step in steps if step.strip())
            continue
        formatted_str += f"{dict_input[key]}\n\n"

    return formatted_str






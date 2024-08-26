import json

def load_workflow(workflow_path):
    """
    Loads a workflow from a JSON file.

    Args:
        workflow_path (str): The path to the JSON file containing the workflow.

    Returns:
        str or None: The JSON string representation of the workflow if the file is valid, otherwise None.
    """
    try:
        with open(workflow_path, 'r') as file:
            workflow = json.load(file)
            return json.dumps(workflow)
    except FileNotFoundError:
        print(f"The file {workflow_path} was not found.")
        return None
    except json.JSONDecodeError:
        print(f"The file {workflow_path} contains invalid JSON.")
        return None
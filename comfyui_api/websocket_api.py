import json
import urllib.request
import urllib.parse
from requests_toolbelt import MultipartEncoder


def upload_image(input_path, name, server_address, image_type="input", overwrite=False):
    """
     Uploads an image to ComfyUI using multipart/form-data encoding.

     Args:
       input_path (str): The file system path to the image file to be uploaded.
       name (str): The name under which the image will be saved on ComfyUI.
       server_address (str): The address of running ComfyUI where the image will be uploaded, excluding the protocol prefix.
       image_type (str, optional): The type/category of the image being uploaded. Defaults to "input". Other options are "output" and "temp".
       overwrite (bool, optional): Flag indicating whether an existing file with the same name should be overwritten.
                                     Defaults to False.

     Returns:
       The ComfyUI response to the upload request.
     """
    with open(input_path, 'rb') as f:
        data = MultipartEncoder(
            fields={
                'image': (name, f, 'image/png'),
                'type': image_type,
                'overwrite': str(overwrite).lower()
            }
        )
        headers = {'Content-Type': data.content_type}
        request = urllib.request.Request("http://{}/upload/image".format(server_address), data=data.to_string(), headers=headers)
        with urllib.request.urlopen(request) as response:
            return response.read()

def queue_prompt(prompt, client_id, server_address):
    """
      Sends a prompt to a ComfyUI to place it into the workflow queue

      Args:
        prompt (str): The text prompt to be sent to running ComfyUI for processing.
        client_id (str): The identifier for the client sending the request, used by the server to track or manage the request.
        server_address (str): The address of running ComfyUI where the prompt is to be sent, excluding the protocol prefix.

      Returns:
        dict: A dictionary parsed from the JSON response from running ComfyUI, containing the result of processing the prompt.
      """
    p = {"prompt": prompt, "client_id": client_id}
    headers = {"Content-Type": "application/json"}
    data = json.dumps(p).encode('utf-8')
    req = urllib.request.Request("http://{}/prompt".format(server_address), data=data, headers=headers)
    return json.loads(urllib.request.urlopen(req).read())

def interrupt_prompt(server_address):
    """
      Sends an interrupt signal to a currently running ComfyUI prompt

      Args:
        server_address (str): The address of running ComfyUI where the interrupt signal is to be sent, excluding the protocol prefix.

      Returns:
        dict: A dictionary parsed from the JSON response from running ComfyUI, containing the result of the interrupt signal.
      """
    req = urllib.request.Request("http://{}/interrupt".format(server_address), data={})
    return json.loads(urllib.request.urlopen(req).read())


def get_image(filename, subfolder, folder_type, server_address):
    """
      Retrieves an image from ComfyUI

      Args:
        filename (str): The name of the image file to retrieve.
        subfolder (str): The subfolder within the folder_type where the image is located.
        folder_type (str): The type/category of the folder where the image is located. Options are "input" and "output".
        server_address (str): The address of running ComfyUI from which to retrieve the image, excluding the protocol prefix.

      Returns:
        bytes: The content of the HTTP response, which should be the requested image file.
    """
    data = {"filename": filename, "subfolder": subfolder, "type": folder_type}
    url_values = urllib.parse.urlencode(data)
    with urllib.request.urlopen("http://{}/view?{}".format(server_address, url_values)) as response:
        return response.read()


def get_history(prompt_id, server_address):
    """
      Retrieves the history of a specific prompt from ComfyUI

      Args:
        prompt_id (str): The identifier of the prompt to retrieve history for.
        server_address (str): The address of running ComfyUI from which to retrieve the history, excluding the protocol prefix.

      Returns:
        dict: A dictionary parsed from the JSON response from running ComfyUI, containing the history of the specified prompt.
      """
    with urllib.request.urlopen("http://{}/history/{}".format(server_address, prompt_id)) as response:
        return json.loads(response.read())

def get_node_info_by_class(node_class, server_address):
    """
      Retrieves the information about a specific node class from ComfyUI

      Args:
        node_class (str): The class of the node to retrieve information for.
        server_address (str): The address of running ComfyUI from which to retrieve the node information, excluding the protocol prefix.

      Returns:
        dict: A dictionary parsed from the JSON response from running ComfyUI, containing the information about the specified node class.
      """
    with urllib.request.urlopen("http://{}/object_info/{}".format(server_address, node_class)) as response:
        return json.loads(response.read())


def clear_comfy_cache(server_address, unload_models=False, free_memory=False):
    """
    Clears the ComfyUI cache, optionally unloading models and freeing memory.

    Args:
        server_address (str): The address of running ComfyUI
        unload_models (bool, optional): Whether to unload models from ComfyUI. Defaults to False.
        free_memory (bool, optional): Whether to free memory used by ComfyUI. Defaults to False.

    Returns:
        bytes: The content of the HTTP response, which should be the result of clearing the ComfyUI cache.
    """
    clear_data = {
        "unload_models": unload_models,
        "free_memory": free_memory
    }
    data = json.dumps(clear_data).encode('utf-8')
    with urllib.request.urlopen("http://{}/free".format(server_address), data=data) as response:
        return response.read()
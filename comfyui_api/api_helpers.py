import json
import io
import os

from PIL import Image
from comfyui_api.websocket_api import queue_prompt, get_history, upload_image ,get_image, clear_comfy_cache
from comfyui_api.open_websocket import open_websocket_connection


def track_progress(prompt, ws, prompt_id):
    """
    Tracks the progress of a task execution by listening to websocket messages.

    Args:
        prompt (str): A dictionary containing the task nodes.
        ws (object): The websocket client object.
        prompt_id (str): The ID of the prompt being executed.

    Returns:
        None
    """
    node_ids = list(prompt.keys())
    finished_nodes = []

    while True:
        out = ws.recv()
        if isinstance(out, str):
            message = json.loads(out)
            if message['type'] == 'progress':
                data = message['data']
                current_step = data['value']
                print('In K-Sampler -> Step: ', current_step, ' of: ', data['max'])
            if message['type'] == 'execution_cached':
                data = message['data']
                for itm in data['nodes']:
                    if itm not in finished_nodes:
                        finished_nodes.append(itm)
                        print('Progress: ', len(finished_nodes), '/', len(node_ids), ' Tasks done')
            if message['type'] == 'executing':
                data = message['data']
                if data['node'] not in finished_nodes:
                    finished_nodes.append(data['node'])
                    print('Progress: ', len(finished_nodes), '/', len(node_ids), ' Tasks done')

                if data['node'] is None and data['prompt_id'] == prompt_id:
                    break  # Execution is done
        else:
            continue  # previews are binary data
    return


def get_images(prompt_id, server_address, allow_preview = False):
    """
    Retrieves the output images for a given prompt ID and server address.

    Args:
        prompt_id (str): The ID of the prompt for which to retrieve images.
        server_address (str): The address of the server hosting the images.
        allow_preview (bool, optional): Whether to include preview images. Defaults to False.

    Returns:
        list: A list of dictionaries, where each dictionary contains information about an output image.
    """
    output_images = []

    history = get_history(prompt_id, server_address)[prompt_id]
    for node_id in history['outputs']:
        node_output = history['outputs'][node_id]
        output_data = {}
        if 'images' in node_output:
            for image in node_output['images']:
                if allow_preview and image['type'] == 'temp':
                    preview_data = get_image(image['filename'], image['subfolder'], image['type'], server_address)
                    output_data['image_data'] = preview_data
                if image['type'] == 'output':
                    image_data = get_image(image['filename'], image['subfolder'], image['type'], server_address)
                    output_data['image_data'] = image_data
        output_data['file_name'] = image['filename']
        output_data['type'] = image['type']
        output_images.append(output_data)

    return output_images


def save_image(images, output_path, save_previews):
    """
    Saves a list of images to the specified output path.

    Args:
        images (list): A list of dictionaries, where each dictionary contains information about an image.
        output_path (str): The path to the directory where the images should be saved.
        save_previews (bool): Whether to save preview images or not.

    Returns:
        None
    """
    for item in images:
        directory = os.path.join(output_path, 'temp/') if item['type'] == 'temp' and save_previews else output_path
        os.makedirs(directory, exist_ok=True)
        try:
            image = Image.open(io.BytesIO(item['image_data']))
            image.save(os.path.join(directory, item['file_name']))
        except Exception as e:
            print(f"Failed to save image {item['file_name']}: {e}")


def generate_image_by_prompt(prompt, output_path, save_previews=False):
    """
    Generates an image based on a given prompt and saves it to the specified output path.

    Args:
        prompt (str): A dictionary containing the task nodes for generating the image.
        output_path (str): The path to the directory where the generated image(s) should be saved.
        save_previews (bool, optional): Whether to save preview images or not. Defaults to False.

    Returns:
        None
    """
    try:
        ws, server_address, client_id = open_websocket_connection()
        prompt_id = queue_prompt(prompt, client_id, server_address)['prompt_id']
        track_progress(prompt, ws, prompt_id)
        images = get_images(prompt_id, server_address, save_previews)
        save_image(images, output_path, save_previews)
        return images
    finally:
        ws.close()

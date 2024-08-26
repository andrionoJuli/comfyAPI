import json

from comfyui_api.api_helpers import generate_image_by_prompt


def prompt_to_image(workflow, img_prompt, save_previews=False):
  """
  Generates an image from a given text prompt using a specified workflow.

  Args:
      workflow (str): The JSON string representation of the workflow to be used.
      img_prompt (str): The text prompt to generate the image from.
      save_previews (bool, optional): Whether to save preview images during the generation process. Defaults to False.

  Returns:
      None
  """
  prompt = json.loads(workflow)
  prompt.get('6')['inputs']['text'] = img_prompt

  image = generate_image_by_prompt(prompt, './output/', save_previews)
  return image

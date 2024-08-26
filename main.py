import logging
import io
import uvicorn

from fastapi import FastAPI, HTTPException, Form
from typing import Annotated
from fastapi.responses import StreamingResponse
from utils.actions.prompt_to_image import prompt_to_image
from utils.actions.load_workflow import load_workflow


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI()


@app.post("/generate_image")
async def generate_image(prompt: Annotated[str, Form()]):
    try:
        # Generate image from prompt
        logger.info("Generating image from prompt: %s", prompt)
        workflow = load_workflow('./workflows/flux_dev_api.json')
        images = prompt_to_image(workflow, prompt, save_previews=True)
        for image in images:
            image_file = io.BytesIO(image['image_data'])
            image_file.seek(0)
            logger.info("Image generated successfully")
            return StreamingResponse(image_file, media_type="image/png")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

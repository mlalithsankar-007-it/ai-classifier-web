from fastapi import FastAPI, UploadFile, File, Request

from fastapi.responses import (
    HTMLResponse,
    StreamingResponse
)

from fastapi.templating import Jinja2Templates

from typing import List

import os
import uuid
import shutil

from app.predict import classify_and_organize

app = FastAPI()

templates = Jinja2Templates(
    directory="app/templates"
)


@app.get("/", response_class=HTMLResponse)
async def home(request: Request):

    return templates.TemplateResponse(
        request=request,
        name="index.html"
    )


@app.post("/upload")
async def upload_images(
    files: List[UploadFile] = File(...)
):

    session_id = str(uuid.uuid4())

    base_dir = f"/tmp/{session_id}"

    upload_dir = os.path.join(
        base_dir,
        "uploads"
    )

    output_dir = os.path.join(
        base_dir,
        "classified"
    )

    os.makedirs(
        upload_dir,
        exist_ok=True
    )

    saved_files = []

    for file in files:

        file_path = os.path.join(
            upload_dir,
            file.filename
        )

        with open(file_path, "wb") as buffer:

            shutil.copyfileobj(
                file.file,
                buffer
            )

        saved_files.append(file_path)

    classify_and_organize(
        saved_files,
        output_dir
    )

    zip_path = shutil.make_archive(
        output_dir,
        'zip',
        output_dir
    )

    zip_file = open(
        zip_path,
        "rb"
    )

    return StreamingResponse(
        zip_file,
        media_type="application/zip",
        headers={
            "Content-Disposition":
            "attachment; filename=classified_images.zip"
        }
    )
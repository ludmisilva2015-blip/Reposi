from __future__ import annotations

import io
import zipfile
from pathlib import PurePosixPath

from fastapi import FastAPI, File, HTTPException, UploadFile

app = FastAPI(
    title="Catroid APK Converter API",
    version="0.1.0",
    description="Initial API for receiving and validating Catrobat .catrobat projects.",
)

MAX_FILE_SIZE = 50 * 1024 * 1024  # 50 MiB


def validate_catrobat_package(data: bytes) -> dict:
    """Validate a .catrobat ZIP package without extracting it to disk."""
    if not data:
        raise HTTPException(status_code=400, detail="O arquivo está vazio.")

    if len(data) > MAX_FILE_SIZE:
        raise HTTPException(
            status_code=413,
            detail="O arquivo excede o limite de 50 MiB.",
        )

    if not zipfile.is_zipfile(io.BytesIO(data)):
        raise HTTPException(
            status_code=400,
            detail="O arquivo não é um pacote ZIP .catrobat válido.",
        )

    with zipfile.ZipFile(io.BytesIO(data)) as package:
        entries = package.infolist()
        if not entries:
            raise HTTPException(status_code=400, detail="O pacote não contém arquivos.")

        for entry in entries:
            path = PurePosixPath(entry.filename)
            if path.is_absolute() or ".." in path.parts:
                raise HTTPException(
                    status_code=400,
                    detail="O pacote contém um caminho inseguro.",
                )

        names = {entry.filename for entry in entries}
        project_files = [
            name
            for name in names
            if name.lower().endswith((".xml", ".catrobat", ".json"))
        ]

        return {
            "valid_zip": True,
            "file_count": len(entries),
            "contains_project_file": bool(project_files),
            "project_files": sorted(project_files)[:20],
        }


@app.get("/health")
def health() -> dict:
    return {"status": "ok", "service": "catroid-apk-converter"}


@app.post("/analyze")
async def analyze_project(file: UploadFile = File(...)) -> dict:
    filename = file.filename or ""
    if not filename.lower().endswith(".catrobat"):
        raise HTTPException(
            status_code=400,
            detail="Envie um arquivo com extensão .catrobat.",
        )

    data = await file.read()
    analysis = validate_catrobat_package(data)

    return {
        "filename": filename,
        "size_bytes": len(data),
        "analysis": analysis,
        "next_step": "Integração com o mecanismo de compilação do Catroid.",
    }

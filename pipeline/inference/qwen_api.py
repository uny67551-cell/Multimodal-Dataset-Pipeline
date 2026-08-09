"""API-based Qwen2.5-VL backend (OpenAI-compatible)."""

from __future__ import annotations

import base64  # tansform data into base64 format so that it can be sent over the network
import mimetypes # guess the MIME type of a file (jpg, pdf......), parse the file name and return the corresponding tag, similar to Pathlib
import os
from pathlib import Path

import requests # send HTTP requests, connect python to internet
from loguru import logger

from pipeline.core.config import InferenceConfig
from pipeline.core.exceptions import InferenceError
from pipeline.inference.base import VLMBackend
from pipeline.inference.parser import parse_structured_response
from pipeline.inference.prompts import build_structured_prompt
from pipeline.models.inference_record import InferenceRecord


class QwenAPIVLM(VLMBackend):
    """Call a remote OpenAI-compatible VLM API."""

    def __init__(self, config: InferenceConfig):
        self.config = config
        self.api_key = os.getenv(config.api_key_env, "").strip()
        if not self.api_key:
            raise InferenceError(
                f"Environment variable {config.api_key_env} is not set. "
                "Set your API key before using backend=api."
            )
        if not config.api_base:
            raise InferenceError(
                "inference.api_base is empty. "
                "Set it in configs/default.yaml for backend=api."
            )

    @property
    def name(self) -> str:
        return "api"

    def _encode_image(self, image_path: Path) -> tuple[str, str]:
        mime, _ = mimetypes.guess_type(str(image_path))
        if mime is None:
            mime = "image/jpeg" # defensive programming when the file with no suffix or wrong suffix
        data = base64.b64encode(image_path.read_bytes()).decode("utf-8")
        return mime, data

    def infer(self, image_path: Path, image_id: str) -> InferenceRecord:
        image_path = Path(image_path)
        inferred_at = InferenceRecord.utc_now()

        if not image_path.exists():
            return InferenceRecord(
                image_id=image_id,
                image_path=image_path,
                status="failed",
                inferred_at=inferred_at,
                backend=self.name,
                error_message="Image not found",
            )

        try:
            mime, b64 = self._encode_image(image_path)
            prompt = build_structured_prompt()
            url = self.config.api_base.rstrip("/") + "/chat/completions" # rstrip: remove the trailing slash /

            payload = { # json format
                "model": self.config.model_name,
                "messages": [
                    {
                        "role": "user",
                        "content": [
                            {
                                "type": "image_url",
                                "image_url": {
                                    "url": f"data:{mime};base64,{b64}",
                                },
                            },
                            {"type": "text", "text": prompt},
                        ],
                    }
                ],
                "max_tokens": self.config.max_new_tokens,
            }
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json",
            }

            response = requests.post(
                url,
                headers=headers,
                json=payload,
                timeout=self.config.api_timeout, # wait for the response until when cancel the request
            )

            if not response.ok:
                # Include response body to debug 404/401 model or auth issues.
                detail = response.text[:500]
                raise RuntimeError(
                    f"{response.status_code} {response.reason} for url: {url}. "
                    f"model={self.config.model_name!r}. body={detail}"
                )

            data = response.json()
            output_text = data["choices"][0]["message"]["content"]

            caption, tags, objects = parse_structured_response(output_text)
            logger.info("API VLM inferred: {}", image_path.name)

            return InferenceRecord(
                image_id=image_id,
                image_path=image_path,
                status="success",
                inferred_at=inferred_at,
                caption=caption,
                tags=tags,
                objects=objects,
                backend=self.name,
            )
        except Exception as exc:
            logger.warning("API inference failed for {}: {}", image_path, exc)
            return InferenceRecord(
                image_id=image_id,
                image_path=image_path,
                status="failed",
                inferred_at=inferred_at,
                backend=self.name,
                error_message=str(exc),
            )

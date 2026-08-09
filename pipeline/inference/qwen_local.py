"""Local Qwen2.5-VL backend with optional 4-bit quantization."""

from __future__ import annotations
from pathlib import Path
from loguru import logger
from pipeline.core.config import InferenceConfig
from pipeline.core.exceptions import InferenceError
from pipeline.inference.base import VLMBackend
from pipeline.inference.parser import parse_structured_response
from pipeline.inference.prompts import build_structured_prompt
from pipeline.models.inference_record import InferenceRecord


class QwenLocalVLM(VLMBackend):
    """Run Qwen2.5-VL locally via transformers."""

    def __init__(self, config: InferenceConfig):
        self.config = config
        self._model = None
        self._processor = None
        self._load_model()

    @property
    def name(self) -> str:
        return "local"

    def _load_model(self) -> None:
        """Load model and processor once."""
        try:
            import torch
            from transformers import AutoProcessor, BitsAndBytesConfig, Qwen2_5_VLForConditionalGeneration
        except ImportError as exc: # ImportErorrr is a built-in class exception
            raise InferenceError(
                "Local backend requires: torch, transformers, bitsandbytes, accelerate, qwen-vl-utils. "
                f"Import error: {exc}"
            ) from exc

        model_name = self.config.model_name
        logger.info("Loading local VLM: {} (4bit={})", model_name, self.config.load_in_4bit)

        try:
            self._processor = AutoProcessor.from_pretrained(model_name) # if not exsit, download on Huggingface

            if self.config.load_in_4bit:
                quant_config = BitsAndBytesConfig(
                    load_in_4bit=True,
                    bnb_4bit_compute_dtype=torch.float16,
                    bnb_4bit_use_double_quant=True,
                    bnb_4bit_quant_type="nf4",
                )
                self._model = Qwen2_5_VLForConditionalGeneration.from_pretrained(
                    model_name,
                    quantization_config=quant_config,
                    device_map="auto",
                )
            else:
                self._model = Qwen2_5_VLForConditionalGeneration.from_pretrained(
                    model_name,
                    torch_dtype=torch.float16, # higher precision for better performance
                    device_map="auto",
                )

            self._model.eval()
            logger.info("Local VLM loaded successfully")

        except Exception as exc: # Exception is a built-in class exception
            raise InferenceError(
                f"Failed to load local model '{model_name}'. "
                f"If this is a VRAM/OOM issue on 4GB GPU, switch to backend=api. "
                f"Details: {exc}"
            ) from exc

    def infer(self, image_path: Path, image_id: str) -> InferenceRecord:
        image_path = Path(image_path)
        inferred_at = InferenceRecord.utc_now()

        if not image_path.exists():
            return InferenceRecord( # input values
                image_id=image_id,
                image_path=image_path,
                status="failed",
                inferred_at=inferred_at,
                backend=self.name,
                error_message="Image not found",
            )

        try:
            from qwen_vl_utils import process_vision_info

            prompt = build_structured_prompt() # build the prompt for the model, such as "Describe the image in detail"
            messages = [ # format
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "image",
                            "image": str(image_path.resolve()),
                            # Limit pixels to reduce VRAM usage on 4GB GPUs.
                            "max_pixels": self.config.max_pixels,
                        },
                        {"type": "text", "text": prompt},
                    ],
                }
            ]

            text = self._processor.apply_chat_template(
                messages,
                tokenize=False,
                add_generation_prompt=True, # add the prompt "Answer in the following format: CAPTION: ... TAGS: a, b, c OBJECTS: x, y"
            )

            image_inputs, video_inputs = process_vision_info(messages) # process the vision info, such as the image and video
            inputs = self._processor( # type：BatchEncoding
                text=[text], # transform text to list of strings
                images=image_inputs,
                videos=video_inputs,
                padding=True,
                return_tensors="pt", # pytorch tensor
            )
            inputs = inputs.to(self._model.device) # move the inputs to the device

            generated = self._model.generate(  # prompt and answer 
                **inputs,  # key: value → key=value
                max_new_tokens=self.config.max_new_tokens,
            )
            trimmed = [
                out_ids[len(in_ids) :]
                for in_ids, out_ids in zip(inputs.input_ids, generated) # zip: combine inputs and generated, tuple: (input_ids, generated)
            ]
            output_text = self._processor.batch_decode(
                trimmed,
                skip_special_tokens=True,
                clean_up_tokenization_spaces=False,
            )[0] # try test

            caption, tags, objects = parse_structured_response(output_text)
            logger.info("Local VLM inferred: {}", image_path.name)

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
            logger.warning("Local inference failed for {}: {}", image_path, exc)
            return InferenceRecord(
                image_id=image_id,
                image_path=image_path,
                status="failed",
                inferred_at=inferred_at,
                backend=self.name,
                error_message=str(exc),
            )
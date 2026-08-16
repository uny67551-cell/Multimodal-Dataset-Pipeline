"""Prompt templates for VLM inference."""


CAPTION_PROMPT = (
    "Describe this image in one clear English sentence. "
    "Focus on the main subject, scene, and notable details."
)

TAGS_PROMPT = (
    "List 3 to 8 short tags for this image. "
    "Return only a comma-separated list, no explanation."
)

OBJECTS_PROMPT = (
    "List the main visible objects in this image. "
    "Return only a comma-separated list of object names."
)

def build_structured_prompt() -> str:
    """
    Build a single prompt that asks for caption, tags, and objects.
    Used by local/API backends that prefer one model call per image.
    """
    return (
        "Analyze this image and respond in exactly the following format:\n"
        "CAPTION: <one English sentence>\n"
        "TAGS: <comma-separated tags>\n"
        "OBJECTS: <comma-separated object names>\n"
        "Do not add any other text."
    )

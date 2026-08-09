""" Custom exceptions for the pipeline."""

class PipelineError(Exception): #Exception is a built-in class in Python that represents an error.
    """base exception for the pipeline errors."""

class IngestionError(PipelineError): #IngestionError is a subclass of PipelineError.
    """Raised when ingestion setup fails, e.g. input directory not found."""

class InferenceError(PipelineError):
    """Raised when VLM inference setup or execution fails."""

class MetadataError(PipelineError):
    """Raised when metadata merge/export setup fails."""

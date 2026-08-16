""" Custom exceptions for the pipeline."""

class PipelineError(Exception):
    """base exception for the pipeline errors."""

class IngestionError(PipelineError):
    """Raised when ingestion setup fails, e.g. input directory not found."""

class InferenceError(PipelineError):
    """Raised when VLM inference setup or execution fails."""

class MetadataError(PipelineError):
    """Raised when metadata merge/export setup fails."""

class QCError(PipelineError):
    """Raised when quality-control setup fails."""

class ExportError(PipelineError):
    """Raised when dataset export setup fails."""
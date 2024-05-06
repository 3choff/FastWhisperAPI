import os
try:
    import torch
except ImportError:
    torch = None
from faster_whisper import WhisperModel
from fastapi.security import HTTPBearer
# Determine device based on availability
if torch is not None:
    device = "cpu" if os.getenv("FORCE_CPU", "false").lower() == "true" else ("cuda" if torch.cuda.is_available() else "cpu")
else:
    device = "cpu"
# Determine the compute type based on the device
compute_type = "float16" if device == "cuda" else "int8"

# Preload the base model
model = WhisperModel("base", device=device, compute_type=compute_type)
security = HTTPBearer()
MAX_THREADS = 6

SUPPORTED_LANGUAGES = (
    "af", "am", "ar", "as", "az", "ba", "be", "bg", "bn", "bo", "br", "bs", "ca", "cs", "cy", "da", "de", "el", "en", "es", "et", "eu", "fa", "fi", "fo", "fr", "gl", "gu", "ha", "haw", "he", "hi", "hr", "ht", "hu", "hy", "id", "is", "it", "ja", "jw", "ka", "kk", "km", "kn", "ko", "la", "lb", "ln", "lo", "lt", "lv", "mg", "mi", "mk", "ml", "mn", "mr", "ms", "mt", "my", "ne", "nl", "nn", "no", "oc", "pa", "pl", "ps", "pt", "ro", "ru", "sa", "sd", "si", "sk", "sl", "sn", "so", "sq", "sr", "su", "sv", "sw", "ta", "te", "tg", "th", "tk", "tl", "tr", "tt", "uk", "ur", "uz", "vi", "yi", "yo", "zh", "yue",
)
SUPPORTED_MODELS = ("tiny.en", "tiny", "base.en", "base", "small.en", "small", "medium.en", "medium", "large-v1", "large-v2", "large-v3", "large", "distil-large-v2", "distil-medium.en", "distil-small.en", "distil-large-v3")

SUPPORTED_EXTENSIONS = ("mp3", "mp4", "mpeg", "mpga", "m4a", "wav", "webm", "opus", "flac", "ogg")

SUPPORTED_RESPONSE_FORMATS = ("text", "verbose_json")

SUPPORTED_TIMESTAMP_GRANULARITIES = ("segment", "word")
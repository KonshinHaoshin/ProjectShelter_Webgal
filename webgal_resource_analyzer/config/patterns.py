"""Regex patterns for parsing WebGAL commands."""

from models.models import ResourceType

# Resource patterns - capture the filename (without extension)
BGM_PATTERN = r'bgm:([^\s\-\;]+)'
BG_PATTERN = r'changeBg:([^\s\-\;]+)'
FIGURE_PATTERN = r'changeFigure:([^\s\-\;\[\}]+)'
EFFECT_PATTERN = r'playEffect:([^\s\-\;]+)'
ANIMATION_PATTERN = r'setAnimation:([^\s\-\;\[\}]+)'
VOCAL_PATTERN = r'vocal/语音:([^\s\-\;]+)'

# Map commands to resource types and their directories
RESOURCE_TYPE_MAP = {
    'bgm:': (ResourceType.BGM, 'bgm'),
    'changeBg:': (ResourceType.BACKGROUND, 'background'),
    'changeFigure:': (ResourceType.FIGURE, 'figure'),
    'playEffect:': (ResourceType.VOCAL, 'vocal'),
    'setAnimation:': (ResourceType.ANIMATION, 'animation'),
    'vocal/语音:': (ResourceType.VOCAL, 'vocal'),
}

# Extension mappings for resource types
IMAGE_EXTENSIONS = {'.png', '.jpg', '.jpeg', '.webp', '.gif', '.bmp'}
AUDIO_EXTENSIONS = {'.mp3', '.wav', '.ogg', '.flac', '.aac'}
VIDEO_EXTENSIONS = {'.mp4', '.webm', '.avi', '.mov'}
JSON_EXTENSIONS = {'.json'}
ANIMATION_EXTENSIONS = {'.json'}

# All supported resource extensions
SUPPORTED_EXTENSIONS = (
    IMAGE_EXTENSIONS | AUDIO_EXTENSIONS | VIDEO_EXTENSIONS | ANIMATION_EXTENSIONS
)
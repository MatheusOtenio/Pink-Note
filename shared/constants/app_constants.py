"""Application-wide constants."""

# Application information
APP_NAME = "NotePad"
APP_VERSION = "1.0.0"
APP_DESCRIPTION = "A simple note-taking application"

# Database constants
DEFAULT_DB_FILENAME = "notepad.db"

# Default folder names
DEFAULT_FOLDER_NAME = "Geral"  # General

# File types
FILE_TYPE_IMAGE = "image"
FILE_TYPE_DOCUMENT = "document"
FILE_TYPE_SPREADSHEET = "spreadsheet"
FILE_TYPE_PRESENTATION = "presentation"
FILE_TYPE_OTHER = "other"

# Supported file extensions
SUPPORTED_IMAGE_EXTENSIONS = [".jpg", ".jpeg", ".png", ".gif", ".bmp"]
SUPPORTED_DOCUMENT_EXTENSIONS = [".pdf", ".doc", ".docx", ".txt", ".rtf"]
SUPPORTED_SPREADSHEET_EXTENSIONS = [".xls", ".xlsx", ".csv"]
SUPPORTED_PRESENTATION_EXTENSIONS = [".ppt", ".pptx"]
SUPPORTED_ATTACHMENT_EXTENSIONS = [".pdf", ".doc", ".docx", ".txt", ".rtf", ".jpg", ".jpeg", ".png"]
SUPPORTED_FILE_EXTENSIONS = (
    SUPPORTED_IMAGE_EXTENSIONS +
    SUPPORTED_DOCUMENT_EXTENSIONS +
    SUPPORTED_SPREADSHEET_EXTENSIONS +
    SUPPORTED_PRESENTATION_EXTENSIONS
)

# UI constants
DEFAULT_WINDOW_WIDTH = 1024
DEFAULT_WINDOW_HEIGHT = 768
DEFAULT_FONT_SIZE = 12
DEFAULT_FONT_FAMILY = "Arial"

# Theme constants
THEME_LIGHT = "light"
THEME_DARK = "dark"
DEFAULT_THEME = THEME_LIGHT

# Date formats
DATE_FORMAT_DISPLAY = "%d/%m/%Y"  # DD/MM/YYYY
DATETIME_FORMAT_DISPLAY = "%d/%m/%Y %H:%M"  # DD/MM/YYYY HH:MM
DATE_FORMAT_ISO = "%Y-%m-%d"  # YYYY-MM-DD (ISO format)
DATETIME_FORMAT_ISO = "%Y-%m-%dT%H:%M:%S"  # ISO format with time

# Error messages
ERROR_DB_CONNECTION = "Erro ao conectar ao banco de dados"
ERROR_FILE_NOT_FOUND = "Arquivo não encontrado"
ERROR_FOLDER_NOT_FOUND = "Pasta não encontrada"
ERROR_NOTE_NOT_FOUND = "Nota não encontrada"
ERROR_EVENT_NOT_FOUND = "Evento não encontrado"
ERROR_ATTACHMENT_NOT_FOUND = "Anexo não encontrado"
ERROR_INVALID_DATE = "Data inválida"
ERROR_INVALID_INPUT = "Entrada inválida"

# Success messages
SUCCESS_NOTE_CREATED = "Nota criada com sucesso"
SUCCESS_NOTE_UPDATED = "Nota atualizada com sucesso"
SUCCESS_NOTE_DELETED = "Nota excluída com sucesso"
SUCCESS_FOLDER_CREATED = "Pasta criada com sucesso"
SUCCESS_FOLDER_UPDATED = "Pasta atualizada com sucesso"
SUCCESS_FOLDER_DELETED = "Pasta excluída com sucesso"
SUCCESS_EVENT_CREATED = "Evento criado com sucesso"
SUCCESS_EVENT_UPDATED = "Evento atualizado com sucesso"
SUCCESS_EVENT_DELETED = "Evento excluído com sucesso"
SUCCESS_ATTACHMENT_ADDED = "Anexo adicionado com sucesso"
SUCCESS_ATTACHMENT_DELETED = "Anexo excluído com sucesso"
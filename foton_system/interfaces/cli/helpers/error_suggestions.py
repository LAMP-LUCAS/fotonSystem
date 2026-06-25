import sqlite3

ERROR_SUGGESTIONS = {
    FileNotFoundError: "Verifique se o arquivo existe ou se o caminho em settings.json esta correto.",
    PermissionError: "Feche o Excel e tente novamente.",
    sqlite3.OperationalError: "Base aberta em outro programa. Feche o arquivo e tente novamente.",
}


def get_error_suggestion(error: Exception) -> str:
    for exc_type, suggestion in ERROR_SUGGESTIONS.items():
        if isinstance(error, exc_type):
            return suggestion
    return "Ocorreu um erro inesperado. Tente novamente."


def format_error_with_suggestion(error: Exception) -> str:
    suggestion = get_error_suggestion(error)
    return f"{error}\nSugestao: {suggestion}"

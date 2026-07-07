def parse_command(text: str) -> dict:
    text = text.strip().lower()

    if text == 'q':
        return {'action': 'exit'}
    elif text == 'h':
        return {'action': 'help'}
    elif text == '00':
        return {'action': 'home'}
    elif text == 'g':
        return {'action': 'global_search'}
    elif text.isdigit():
        return {'action': 'numeric', 'value': int(text)}
    else:
        return {'action': 'search', 'term': text}

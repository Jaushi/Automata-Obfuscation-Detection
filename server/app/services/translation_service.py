from typing import Union


def _join(tokens: list[str]) -> str:
    """
    Join tokens with proper spacing rules.
    Rules:
    - No space before closing punctuation: ! ? . , ; :
    - No space after opening punctuation: ( [ { " '
    - Normal space between all other tokens
    
    Args:
        tokens: List of tokens to join
    Examples:
        ["hello", ",", "world", "!"] → "hello, world!"
        ["(", "test", ")"] → "(test)"
    """
    if not tokens:
        return ""
    
    result = ""
    opening = {'(', '[', '{', '"', "'"}
    closing = {')', ']', '}', '"', "'", '.', ',', '!', '?', ';', ':'}
    
    for i, token in enumerate(tokens):
        # First token: no space
        if i == 0:
            result += token
            continue
        
        prev_token = tokens[i-1]
        
        # No space before closing punctuation
        if token in closing:
            result += token
        # No space after opening punctuation
        elif prev_token in opening:
            result += token
        # Normal space for everything else
        else:
            result += " " + token
    
    return result.strip()


def translate_to_clean_text(input_data: Union[str, list[str]]) -> str:
    """
    Convert deobfuscated tokens/text into properly formatted clean text.
    
    This is the FINAL OUTPUT. Call this after deobfuscation.
    
    Args:
        input_data: Either a string (will be tokenized) or list of tokens
        
    Returns:
        Properly formatted final text
        
    Examples:
        "hello world" → "hello world"
        ["hello", "world"] → "hello world"
        ["hello", ",", "world", "!"] → "hello, world!"
    """
    # Handle both string and token list inputs
    if isinstance(input_data, str):
        tokens = input_data.split() if input_data.strip() else []
    else:
        tokens = input_data
    
    return _join(tokens)
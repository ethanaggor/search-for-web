def search_for_letters(phrase:str, letters:str='aeiou') -> set:
    """Return a set of the letters found in 'phrase'."""
    return sorted(set(letters).intersection(set(phrase)))

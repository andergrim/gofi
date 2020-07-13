
def ldistance(string, token):
    # Calculate the Levenshtein distance between string, token
    if len(string) < len(token):
        return ldistance(token, string)
    if len(token) == 0:
        return len(string)
    previous_row = range(len(token) + 1)
    for i, c_string in enumerate(string):
        current_row = [i + 1]
        for j, c_token in enumerate(token):
            insertions = previous_row[j + 1] + 1
            deletions = current_row[j] + 1
            substitutions = previous_row[j] + (c_string != c_token)
            current_row.append(min(insertions, deletions, substitutions))
        previous_row = current_row
    return previous_row[-1]


def lratio(string, token):
    # Calculate the similarity ratio of string, token based on their
    # Levenshtein distance
    distance = ldistance(string, token)
    ratio = ((len(string) + len(token)) - distance) / (len(string) + len(token))
    return ratio


def parsebool(tags):
    if '|' in tags and '&' not in tags:
        l=tags.split('|')
        return ('or',l)
    elif '&' in tags and '|' not in tags:
        l=tags.split('&')
        return ('and',l)
    else:
        return ('or',[tags])

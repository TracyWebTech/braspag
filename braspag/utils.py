
def spaceless(xml_str):
    return ''.join(line.strip() for line in xml_str.split('\n') if line.strip())

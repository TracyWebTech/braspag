import string

def spaceless(xml_str):
    return ''.join(line.strip() for line in xml_str.split('\n') if line.strip())

def is_valid_guid(guid):
    VALID_CHARS = string.hexdigits + '-'
    VALID_PARTS_LEN = [8, 4, 4, 4, 12]

    if not isinstance(guid, basestring):
        guid = unicode(guid)

    if not all(c in VALID_CHARS for c in guid):
        return False

    guid_parts_len = [len(part) for part in guid.split('-')]
    if guid_parts_len != VALID_PARTS_LEN:
        return False

    return True

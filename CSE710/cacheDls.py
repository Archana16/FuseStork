import time
import contactDls

def add_mount_Response(cache, mountResponse, mount):
    cache.add(mount, mountResponse)
    fileList = mountResponse.get("files")
    for f in fileList:
        _val = contactDls.json_to_dict(f)
        _key = _val.get("name")
        cache.add(_key, _val)

class Cache:

    def __init__(self, funct, maxsize=1024):
        self.org_function = funct
        self.maxsize = maxsize
        self.mapping = {}

    def get_cache(self, *args):
        mapping = self.mapping
        key = args[0]
        value = mapping.get(key)
        if value is not None:
            value = self.update_cache(key, value)
            return value

        value = self.org_function(key)
        mapping[str(key)] = value
        fileList = value.get("files")
        if fileList is not None:
            for f in fileList:
                _val = contactDls.json_to_dict(f)
                _key = _val.get("name")
                _key = key+"/"+_key
                mapping[str(_key)] = _val
        return value

    def update_cache(self, keyStr, value):
        mapping = self.mapping
        if value['dir'] and value['files'] is None:
            update = self.org_function(keyStr)
            value['files'] = update['files']
            mapping[keyStr] = value
        else:
            print("")

        return value
        
    def add(self, *args):
        mapping = self.mapping
	key = args[0]
        value = args[1]
        mapping[key] = value
        return

def tmp(key):
    if type(key) != type(str()):

	    return key.upper()



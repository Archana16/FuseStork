import os, sys, errno
import re
import requests


def json_to_dict(obJson):
    py_dict = {}
    attr_list = ['file','size','perm','name','time','dir','files']
    for attr in attr_list:
        value = obJson.get(attr)
        py_dict[attr] = value
    
    if py_dict.get("perm") is None:
        py_dict["perm"] = "777"
    else:
        py_dict["perm"] = py_dict["perm"]

    py_dict["perm"] = py_dict["perm"]#Convert to octal number

    return py_dict

class ContactDls:
    def __init__(self, dlsUrl, path):
        self.dls = dlsUrl
        self.mountPath = os.path.join(path)

    def __remote_path__(self, _path):
        _path = re.sub(self.mountPath, "", _path, 1)
        _path = "ftp://ftp.mozilla.org/"+_path
        return _path


    def get_Response(self, path):
	try:
            path = self.__remote_path__(path)
            payload = {"uri":path}
            http_Response = requests.get(self.dls, params=payload,cookies=dict(email="asuregao@buffalo.edu",password="iamthebest"))
            return json_to_dict(http_Response.json())
        except requests.exceptions.Timeout:
	    print "Unable to connect server"



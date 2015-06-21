from __future__ import with_statement
from sys import argv, exit
import time
from fuse import FUSE, FuseOSError, Operations, fuse_get_context
import cacheDls, contactDls
import os,stat
import errno
import shutil
import requests
import json

class Passthrough(Operations):
    def __init__(self, root):
        self.root = os.path.join(root)
        self.curpath = self.root
        dlsUrl = "https://storkcloud.org/api/stork/ls"
        self.dls = contactDls.ContactDls(dlsUrl, self.root)
        self.cache = cacheDls.Cache(self.dls.get_Response)
        self.__mount__()

    def __mount__(self):
        path = os.path.join(self.root, "")
	mountResponse = self.dls.get_Response(path)	
	cacheDls.add_mount_Response(self.cache, mountResponse, path)

    def _convert_to_stat(self, Response):
        st = dict()
        if Response['dir']:
            st['st_mode'] = stat.S_IFDIR
            st['st_nlink'] = 1
        else:
            st['st_mode'] = stat.S_IFREG
            
        st['st_mode'] = (st['st_mode'] | 777)#Response['perm'])
        st['st_ctime'] = st['st_mtime'] = st['st_atime'] = time.time()
        return st 

    # Helpers
    # =======

    def _full_path(self, partial):
        if partial == "/":
            partial = ""
        elif partial.startswith("/"):
            partial = partial[1:]
        path = os.path.join(self.root, partial)
        return path

    # Filesystem methods
    # ==================
    def getattr(self, path, fh=None):
        path = self._full_path(path)
        result = self.cache.get_cache(path)
        dlsUrl = "https://storkcloud.org/api/stork/get"
	xPath = path.split("dls")[1]
        _path = "ftp://ftp.mozilla.org/"+xPath
	payload = {"uri":_path}

	test = "README"
	if not result['dir']:
		firstPart = """curl -b \"email=asuregao@buffalo.edu;password=iamthebest\" https://storkcloud.org/api/stork/get?uri=ftp://ftp.mozilla.org"""
		firstPart = firstPart+xPath
     		x = """curl -b \"email=asuregao@buffalo.edu;password=iamthebest\" https://storkcloud.org/api/stork/get?uri=ftp://ftp.mozilla.org/README"""
		os.system(firstPart)
        st = self._convert_to_stat(result)

        return st

    def readdir(self, path, fh):
        path = self._full_path(path)
        result = self.cache.get_cache(path)
        if not result['dir']:
            raise FuseOSError(errno.EBADF)
        dirents = ['.', '..']
        fileList = result.get('files')
        for f in fileList:
            fileName = f.get('name')
            dirents.append(fileName)
        return dirents

	def open(self, path, flags):
        	full_path = self._full_path(path)
	        return os.open(full_path, flags)

        def read(self, path, length, offset, fh):
	     	os.lseek(fh, offset, os.SEEK_SET)
        	return os.read(fh, length)	

	def create(self, path, mode, fi=None):

        	full_path = self._full_path(path)
	        return os.open(full_path, os.O_WRONLY | os.O_CREAT, mode)

        def read(self, path, length, offset, fh):

    	        os.lseek(fh, offset, os.SEEK_SET)
	        return os.read(fh, length)

        def write(self, path, buf, offset, fh):
  		os.lseek(fh, offset, os.SEEK_SET)
	        return os.write(fh, buf)

	def truncate(self, path, length, fh=None):
	        full_path = self._full_path(path)
        	with open(full_path, 'r+') as f:
	            f.truncate(length)

	def flush(self, path, fh):
        	return os.fsync(fh)

    	def release(self, path, fh):
        	return os.close(fh)

    	def fsync(self, path, fdatasync, fh):
        	return self.flush(path, fh)

def main(mountpoint, root):
    FUSE(Passthrough(root), mountpoint, foreground=True)

if __name__ == '__main__':
    print "--- FuseDLS FileSystem started ----"
    mountpoint = "/home/skaran/CSE710/fuse_mount/dls"
    dir = mountpoint
    if os.path.exists(dir):
    	shutil.rmtree(dir)
    os.makedirs(dir)    
    main(mountpoint,mountpoint)	

import pymongo, sys, traceback
from docx import Document
import zipfile
import glob
import subprocess

sys.path.insert(0, '/opt/git/Spider/src/')

from data import conf

class ks5u_rmwm:

    def __init__(self):
        pass

    def remove_wm(self):

        print 'hello'
        doc = 'test.doc'
        document = Document(doc)
        print document
        # with zipfile.ZipFile('test.doc') as wf:
        #     xml_info = zf.read('word/document.xml')
        #
        # print xml_info

        subprocess.call(['soffice', '--headless', '--convert-to', 'docx', doc])




if __name__ == "__main__":
    ks5u = ks5u_rmwm()
    ks5u.remove_wm()

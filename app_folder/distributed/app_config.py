import os
basedir = os.path.abspath(os.path.dirname(__file__))


class Config(object):
    CHROME_PATH = os.path.join(basedir, 'chromedriver.exe')

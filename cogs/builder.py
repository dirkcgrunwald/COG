# -*- coding: utf-8 -*-

# Andy Sayler
# Summer 2014
# Univerity of Colorado


import abc


class Builder(object):

    __metaclass__ = abc.ABCMeta

    def __init__(self, env, tst, run):
        self.env = env
        self.tst = tst
        self.run = run

    def _format_msg(self, msg):
        return "{:s}: {:s}".format(str(self.run), msg)

    @abc.abstractmethod
    def build(self):

        # Set Vars
        ret = -1
        out = "Dummy Builder build()"

        # Return
        return ret, out


from socket import *
import sys

class InvalidCommandError(Exception):
    def __init__(self, cmd):
        self._cmd = cmd
    def __repr__(self):
        return self._cmd

class CommandProxy(object):
    HOST = '192.168.0.111'
    PORT = 8889
    CMDS = [
            'ADEnable',
            'ADInit',
            'getAD',
            'setIOPorts',
            'getDigiInput',
            'setMode',
            'setRotaSpeed',
            'setPos',
            'getPos',
            'action',
            ]
    
    def __init__(self):
        self.sock = socket(AF_INET, SOCK_STREAM)
        self.sock.connect(self.HOST, self.PORT)
        self._funcs = {funcName:self._make_func(fn) for fn in self.CMDS}

    def __getattr__(self, name):
        if name in self._funcs:
            return self._funcs[name]
        else:
            raise InvalidCommandError(name)

    def _make_func(self, funcName):
        def func(*args):
            cmd = ' '.join([funcName] + args) + '\n'
            self.sock.send(cmd)
            result = self.sock.recv(2048)
            if result == -1:
                raise InvalidCommandError(cmd)
        return func

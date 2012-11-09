# -*- encoding: utf-8 -*-

class BraspagException(Exception):
    """
    Custom exception
    """
    pass


class BraspagHttpResponseException(BraspagException):
    """
    Status code Exception
    """
    def __init__(self,code,msg):
        self.code = code
        self.msg = msg

    def __str__(self):
        return "[{}] {}".format(self.code,self.msg)




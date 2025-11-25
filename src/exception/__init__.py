from src.logger import logging
import sys

def exception_ext (error: Exception , error_details: sys) -> str :
    """
    this module takes exception and extract file name
    and loc of error and return it by logging
    """
    _,_,er = error_details.exc_info()

    error_file = er.tb_frame.f_code.co_filename
    line_no = er.tb_lineno

    error_meassage = f"error at file {error_file} on line {line_no} - massage {error}"
    logging.error(error_meassage)

    return error_meassage

class myexception (Exception):
    """
    this class is inhertiated class of Exception class 
    in python
    this calls function and returns string of formatted msg
    """
    def __init__(self,error: Exception, error_details: sys):
        """
        this function accepts argument through object 
        and call exception_ext function
        """
        self.error = error
        self.error_details = error_details

        self.exception = exception_ext(self.error,self.error_details)
        super().__init__(self.exception)
    
    def __str__(self):
        """
        Docstring for __str__
        
        :param self: Description
        """
        return self.exception
from src.exception import myexception
import sys
try:
    x=1/0
except Exception as e:
    myexception(e,sys)

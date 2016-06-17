#/usr/bin/python3

from modules.pastafari.libraries.task import Task

class MakeTask(Task):
    
    def __init__(self, server, task_id=0):
        
        super().__init__(server, task_id)
        
        #Here put the files to upload an execute
    
    def form(self, t):
        
        #Here load the form for it task
        
        return "MySQL password: <input type=\"text\" name=\"mysql_password\"/>"
    

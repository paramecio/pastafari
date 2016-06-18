#/usr/bin/python3

from modules.pastafari.libraries.task import ArgsTask

class MakeTask(ArgsTask):
    
    def __init__(self):
        
        super().__init__()
        
        self.files=[['modules/pastafari/scripts/servers/databases/mariadb/install_mariadb.py', 0o700]]
        
        # Format first array element is command with the interpreter, the task is agnostic, the files in os directory. The commands are setted with 750 permission.
        # First element is the file, next elements are the arguments
        
        self.commands_to_execute=[['modules/pastafari/scripts/servers/databases/mariadb/install_mariadb.py', '']];
        
        #THe files to delete
        
        self.delete_files=[]
        
        self.delete_directories=['modules/pastafari/scripts/servers/databases/mariadb']
    
    def form(self, t):
        
        #Here load the form for it task
        
        return "MySQL password: <input type=\"text\" name=\"mysql_password\"/>"
    
    def insert_task(self, post):
        
        pass

#/usr/bin/python3

from modules.pastafari.libraries.task import ArgsTask
from modules.pastafari.models.tasks import Task

class MakeTask(ArgsTask):
    
    def __init__(self, conn):
        
        super().__init__(conn)
        
        self.files=[['modules/pastafari/scripts/servers/databases/mariadb/${os_server}/install_mariadb.py', 0o700]]
        
        # Format first array element is command with the interpreter, the task is agnostic, the files in os directory. The commands are setted with 750 permission.
        # First element is the file, next elements are the arguments
        
        #self.commands_to_execute=[['modules/pastafari/scripts/servers/databases/mysql/install_mariadb.py', '']];
        
        #THe files to delete
        
        self.delete_files=[]
        
        self.delete_directories=['modules/pastafari/scripts/servers/databases/mariadb']
        
        self.task=Task(conn)
        
        self.one_time=True
    
    def form(self, t):
        
        #Here load the form for it task
        
        return "The MySQL password used by all servers: <input type=\"text\" name=\"mysql_password\"/>"
    
    def insert_task(self, post):
        
        self.task.create_forms()
        """
        self.register(corefields.CharField('name_task'), True)
        self.register(corefields.CharField('description_task'), True)
        self.register(ArrayField('files', ArrayField('', corefields.CharField(''))))
        self.register(ArrayField('commands_to_execute', ArrayField('', corefields.CharField(''))))
        self.register(ArrayField('delete_files', corefields.CharField('')))
        self.register(ArrayField('delete_directories', corefields.CharField('')))
        self.register(corefields.BooleanField('error'))
        self.register(corefields.BooleanField('status'))
        self.register(corefields.CharField('url_return'))
        self.register(IpField('server'))
        self.register(corefields.TextField('where_sql_server'))
        self.register(corefields.IntegerField('num_servers'))
        """
        
        if 'mysql_password' in post:
        
            self.commands_to_execute=[['modules/pastafari/scripts/servers/databases/mariadb/install_mariadb.py', '--password=%s' % post['mysql_password']]]
            
            if self.task.insert({'name_task': 'Mariadb Install server', 'description_task': 'Install a mariadb/Mysql server in your selected hosts', 'files': self.files, 'commands_to_execute': self.commands_to_execute, 'delete_files': self.delete_files, 'delete_directories': self.delete_directories}):
                
                return self.task.insert_id()
                
        return False
            
        
        

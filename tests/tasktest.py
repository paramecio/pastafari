#!/usr/bin/python3 

from modules.pastafari.libraries.task import Task
from settings import config
import unittest, os

class TestTask(unittest.TestCase):
    
    
    def test_task(self):
        # You need have defined config.server_test variable
        
        task=Task(config.server_test)
        
        file_path='modules/pastafari/tests/scripts/alive.sh'
        
        task.files=[[file_path, 0o750]]
        
        task.commands_to_execute=[[file_path, '']]
        
        task.delete_files=[file_path]
        
        task.delete_directories=['modules/pastafari/tests']
        
        self.assertTrue(task.exec())

        

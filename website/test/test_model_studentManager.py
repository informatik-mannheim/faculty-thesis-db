from django.test import TestCase

from website.models import *


class StudentManagerTests(TestCase):
    databases = {'default', 'faculty'}

    def setUp(self):
        self.student = Student(id=123456, first_name="Peter", last_name="Petermann", program="IB")
            
    def test_student_doesnt_exists(self):
        student_found = StudentManager().find(123456)
        self.assertEqual(student_found, None)

    def test_find_student_in_faculty(self):
    	self.student.save(using='faculty')
    	student_found = StudentManager().find(123456)
    	
    	self.assertEqual(student_found, self.student)

    def test_find_student_in_default(self):
    	self.student.save(using='faculty')
    	self.student.save(using='default')
    	student_found = StudentManager().find(123456)
    	
    	self.assertEqual(student_found, self.student)
    	
    def test_update_student_information(self):
        student_now_master = Student(id=123456, first_name="Peter", last_name="nichtpetermann", program="IM")
        student_now_master.save(using='faculty')
        self.student.save(using='default')
        student_found = StudentManager().find(123456)
        
        self.assertEqual(student_found.id, student_now_master.id)
        self.assertEqual(student_found.last_name, student_now_master.last_name)
        self.assertEqual(student_found.program, student_now_master.program)

import os
import unittest
import json
from flask_sqlalchemy import SQLAlchemy
from flask import abort
from flaskr import create_app
from models import setup_db, Question, Category


class TriviaTestCase(unittest.TestCase):
    """ This class represents the trivia test case """

    def  setUp(self):
        """Define test variables and initialize app. """
        self.app = create_app()
        self.client = self.app.test_client
        self.database_name = "trivia"
        self.database_path ='postgresql://postgres:abdo@localhost:5432/trivia'
        #"postgresql://{}:{}@{}/{}".format(localhost:5432', database_name)
        setup_db(self.app, self.database_path)
        self.new_question={"question":"The number of continents of the world?",
                           "answer":"7",
                           "difficulty":1,
                           "category":3
                           }

        # binds the app to the current context
        with self.app.app_context():
            self.db = SQLAlchemy()
            self.db.init_app(self.app)
            # create all tables
            self.db.create_all()
           
    
    def  tearDown(self):
        """Executed after reach test """
        pass


    #TODO
    #Write at least one test for each test for successful operation and for expected errors.

    def  test_get_all_categories_success(self):
        res = self.client().get('/categories')
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'],True)
        self.assertTrue(data['total_categories'])
        self.assertTrue(len(data['categories']))
        
    def  test_get_all_categories_fail(self):
        res = self.client().get('/categories/100')
        data = json.loads(res.data)
        self.assertEqual(res.status_code,404)
        self.assertEqual(data['success'],False)
        self.assertEqual(data['message'],'resource not found')

    def  test_get_all_questions_success(self):
        res = self.client().get(f'/questions')
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'],True)
        self.assertTrue(data['total_questions'])
        self.assertTrue(len(data['questions']))
        
        
    def  test_get_all_questions_fail(self):
        res = self.client().get(f'/questions/100')
        data = json.loads(res.data)
        self.assertEqual(res.status_code,405)
        self.assertEqual(data['success'],False)
        self.assertEqual(data['message'],'method not allowed')

    def  test_sent_requesting_beyond_valid_page(self):
        page= 1000
        res = self.client().get(f'/questions?page={page}')
        data = json.loads(res.data)
        self.assertEqual(res.status_code,404)
        self.assertEqual(data['success'],False)
        self.assertEqual(data['message'],'resource not found')
        
        
    def  test_delete_questions(self):
        question=Question.query.order_by(Question.id).first()
        res = self.client().delete(f'/questions/{question.id}')
        data = json.loads(res.data)
        self.assertEqual(res.status_code,200)
        self.assertEqual(data['success'],True)
        self.assertEqual(data['deleted'],question.id)
        
    def  test_delete_questions_dose_not_exist(self):
        question=Question.query.order_by(Question.id.desc()).first()
        res = self.client().delete(f'/questions/{question.id+5}')
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 404)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], 'resource not found')

    def  test_add_question_success(self):
        res = self.client().post('/questions',
                                 data=json.dumps(self.new_question),
                                 content_type='application/json')
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'],True)
        self.assertTrue(data['question'])
        self.assertTrue(len(data['question']))

    def  test_add_question_unprocessable(self):
        temp_question=self.new_question.copy()
        temp_question['question']=''
        res = self.client().post('/questions',json=temp_question)
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 406)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], 'not acceptable')


    def  test_get_questions_by_category(self):
        category=3
        res = self.client().get(f'/categories/{category}/questions')
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertTrue(data['questions'])
        self.assertTrue(data['total_questions'])

    def  test_get_questions_by_category_fail(self):
        category=Category.query.order_by(Category.id.desc()).first()
        category_id = category.id+5
        res = self.client().get(f'/categories/{category_id}/questions')
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 404)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], 'resource not found')


    def test_search(self):
        res = self.client().post('/questions', json={'searchTerm': 'title'},
                                 content_type='application/json')
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 200)
        self.assertIsInstance(data['questions'], list)

    def test_search_fail(self):
        res = self.client().post('/questions/100', json={},content_type='application/json')
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 405)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], 'method not allowed')

    def  test_get_quiz_questions(self):
        request_data = {
            'previous_questions': [1, 2, 3, 4],
            'quiz_category': {'id': 3, 'type': 'Geography'}
        }
        res = self.client().post('/quizzes', data=json.dumps(request_data),
                                 content_type='application/json')
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 200)
        if data.get('question', None):
            self.assertNotIn(data['question']['id'],
                             request_data['previous_questions'])

    def  test_get_quiz_questions_fail(self):
        res = self.client().post('/quizzes', data=json.dumps({}),
                                 content_type='application/json')
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 404)
        self.assertEqual(data['success'], False)
    


# Make the tests conveniently executable
if __name__ == "__main__":
    unittest.main()
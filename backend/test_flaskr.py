import unittest
import json
from flask_sqlalchemy import SQLAlchemy

from flaskr import create_app
from models import setup_db, Question, Category


class TriviaTestCase(unittest.TestCase):
    """This class represents the trivia test case"""

    def setUp(self):
        """Define test variables and initialize app."""
        self.app = create_app()
        self.client = self.app.test_client
        self.database_name = "trivia_test"
        self.database_path = "postgresql://{}/{}".format(
            'localhost:5432', self.database_name)
        setup_db(self.app, self.database_path)

        # binds the app to the current context
        with self.app.app_context():
            self.db = SQLAlchemy()
            self.db.init_app(self.app)
            # create all tables
            self.db.create_all()

    def tearDown(self):
        """Executed after reach test"""
        pass

    """
    TODO
    Write at least one test for each test for successful operation and for expected errors.
    """

    def test_get_all_categories(self):
        res = self.client().get('/categories')
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 200)
        self.assertTrue(data['categories'])
        self.assertTrue(len(data['categories']))

    def test_404_get_non_existing_categories(self):
        res = self.client().get('/categories/99999')
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 404)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], 'Resource not found')

    def test_get_all_questions(self):
        res = self.client().get('/questions')
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 200)
        self.assertTrue(data['questions'])
        self.assertTrue(data['total_questions'])
        self.assertTrue(data['categories'])
        self.assertEqual(data['currentCategory'], None)

    def test_404_get_all_questions_exceeding_max_page(self):
        res = self.client().get('/quesions?page=999')
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 404)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], 'Resource not found')

    def test_delete_question(self):
        res = self.client().delete('/questions/2')
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 200)
        self.assertTrue(data['success'])
        self.assertTrue(data['deleted_id'])

    def test_404_delete_question_by_wrong_id(self):
        res = self.client().delete('/questions/999')
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 404)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], 'Resource not found')

    def test_create_question(self):
        test_question = {
            'question': 'Test question',
            'answer': 'Test answer',
            'difficulty': 5,
            'category': 2,
        }
        res = self.client().post('/questions', json=test_question)
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 200)
        self.assertTrue(data['question'])
        self.assertTrue(data['success'])

    def test_422_create_question_invalid(self):
        test_question = {
            'question': 'Test question',
            'difficulty': 5,
            'category': 2,
        }

        res = self.client().post('/questions', json=test_question)
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 422)
        self.assertFalse(data['success'])
        self.assertEqual(data['message'], 'Unprocessable request')

    def test_get_question_by_category(self):
        res = self.client().get('/categories/2/questions')
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 200)
        self.assertTrue(data['success'])
        self.assertTrue(data['questions'])
        self.assertTrue(data['totalQuestions'])
        self.assertTrue(data['currentCategory'])

    def test_404_get_question_by_non_existing_category(self):
        pass

    def test_search_question(self):
        search_query = {
            'searchTerm': 'World Cup'
        }

        search_term = "%{}%".format(search_query['searchTerm'])

        questions = Question.query.filter(
            Question.question.like(search_term)).all()
        pass

    def test_404_search_not_found(self):
        search_query = {
            'searchTerm': ''
        }

        res = self.client().post('/questions/search', json=search_query)
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 404)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], 'Resource not found')

    def test_422_search_invalid(self):
        search_query = {}

        res = self.client().post('/questions', json=search_query)
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 422)
        self.assertFalse(data['success'])
        self.assertEqual(data['message'], 'Unprocessable request')

    def test_play_quiz(self):
        quiz_query = {
            'previous_questions': [],
            'quiz_category': {
                'type': 'click',
                'id': 0
            }
        }

        res = self.client().post('/quizzes', json=quiz_query)
        data = json.loads(res.data)

        self.assertEquals(res.status_code, 200)
        self.assertTrue(data['success'])
        self.assertTrue(len(data['question']))

    def test_422_unprocessable_quiz(self):
        quiz_query = {
            'previous_questions': [],
        }

        res = self.client().post('/quizzes', json=quiz_query)
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 422)
        self.assertFalse(data['success'])
        self.assertEqual(data['message'], 'Unprocessable request')

        # Make the tests conveniently executable
if __name__ == "__main__":
    unittest.main()

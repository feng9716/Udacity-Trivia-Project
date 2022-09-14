from crypt import methods
import os
import sys
import traceback
from unicodedata import category
from flask import Flask, request, abort, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
import json
from models import setup_db, Question, Category
import random

QUESTIONS_PER_PAGE = 10


def questions_paginate(request, questions):
    page_num = request.args.get('page', 1, type=int)
    start = (page_num - 1) * QUESTIONS_PER_PAGE
    end = start + QUESTIONS_PER_PAGE

    return questions[start:end]


def create_app(test_config=None):
    # create and configure the app
    app = Flask(__name__)
    setup_db(app)
    db = SQLAlchemy(app)

    """
    Set up CORS. Allow '*' for origins. Delete the sample route after completing the TODOs
    """
    CORS(app, resources={r"/*": {"origins": "*"}})

    """
     Use the after_request decorator to set Access-Control-Allow
    """
    @app.after_request
    def after_request(response):
        response.headers.add('Access-Control-Allow-Headers',
                             'Content-Type, Aurthorization')
        response.headers.add('Access-Control-Allow-Headers',
                             'GET,POST,PATCH,DELETE,OPTIONS')
        return response

    """
    Create an endpoint to handle GET requests
    for all available categories.
    """
    @app.route('/categories')
    def get_categories():
        try:
            categories = Category.query.all()

            # 404 when no categories
            if len(categories) == 0 or categories == False:
                abort(404)

            formatted_categories = [cat.format() for cat in categories]

            return jsonify({
                'categories': {cate['id']: cate['type'] for cate in formatted_categories}
            })

        except:
            abort(422)
    """
    Create an endpoint to handle GET requests for questions,
    including pagination (every 10 questions).
    This endpoint should return a list of questions,
    number of total questions, current category, categories.

    TEST: At this point, when you start the application
    you should see questions and categories generated,
    ten questions per page and pagination at the bottom of the screen for three pages.
    Clicking on the page numbers should update the questions.
    """
    @app.route('/questions', methods=['GET'])
    def get_question():
        # Get Categories
        categories = Category.query.order_by(Category.type).all()
        # Get questions and paginate them
        questions = Question.query.order_by(Question.id).all()
        formatted_questions = [question.format() for question in questions]
        question_cur_page = questions_paginate(request, formatted_questions)

        if len(question_cur_page) == 0 or question_cur_page is None:
            abort(404)

        return jsonify({
            'success': True,
            'questions': question_cur_page,
            'total_questions': len(formatted_questions),
            'categories': {category.id: category.type for category in categories},
            'currentCategory': None})

    """
    Create an endpoint to DELETE question using a question ID.

    TEST: When you click the trash icon next to a question, the question will be removed.
    This removal will persist in the database and when you refresh the page.
    """
    @app.route('/questions/<int:questionId>', methods=['Delete'])
    def delete_question(questionId):
        question = Question.query.filter(
            Question.id == questionId).one_or_none()

        if question is None:
            abort(404)
        else:
            try:
                question.delete()
                return jsonify({
                    'success': True,
                    'deleted_id': question.id
                })
            except:
                abort(422)

    """
    Create an endpoint to POST a new question,
    which will require the question and answer text,
    category, and difficulty score.

    TEST: When you submit a question on the "Add" tab,
    the form will clear and the question will appear at the end of the last page
    of the questions list in the "List" tab.
    """
    @app.route('/questions', methods=['POST'])
    def create_question():
        request_body = request.get_json()
        question = request_body.get('question')
        answer = request_body.get('answer')
        difficulty = request_body.get('difficulty')
        category = request_body.get('category')

        if not (question is not None and answer is not None and difficulty is not None and category is not None):
            abort(422)

        new_question = Question(question, answer, category, difficulty)
        Question.insert(new_question)
        return jsonify({
            'success': True,
            'question': new_question.format()
        })
    """
    Create a POST endpoint to get questions based on a search term.
    It should return any questions for whom the search term
    is a substring of the question.

    TEST: Search by any phrase. The questions list will update to include
    only question that include that string within their question.
    Try using the word "title" to start.
    """
    @app.route('/questions/search', methods=['POST'])
    def search_questions():
        try:
            request_body = request.get_json()

            search_term = request_body.get('searchTerm', None)

            if search_term:
                search_term = f'%{search_term}%'
                questions = Question.query.filter(
                    Question.question.ilike(search_term)).all()
                questions = questions_paginate(request, questions)

            return jsonify({
                'success': True,
                'questions': [q.format() for q in questions],
                'totalQuestions': len(questions),
                'currentCategory': None
            })

        except Exception:
            traceback.print_exc()
            abort(404)

    """
    Create a GET endpoint to get questions based on category.

    TEST: In the "List" tab / main screen, clicking on one of the
    categories in the left column will cause only questions of that
    category to be shown.
    """
    @app.route('/categories/<int:categoryId>/questions')
    def questions_by_category(categoryId):
        category = Category.query.filter(
            Category.id == categoryId).one_or_none()
        if (category is None):
            abort(404)
        else:
            questions = Question.query.filter(
                Question.category == categoryId).all()

            questions = [question.format() for question in questions]
            questions = questions_paginate(request, questions)

            if questions == False or len(questions) == 0:
                abort(404)

            return jsonify({
                'success': True,
                'questions': questions,
                'totalQuestions': len(questions),
                'currentCategory': categoryId})
    """
    @TODO:
    Create a POST endpoint to get questions to play the quiz.
    This endpoint should take category and previous question parameters
    and return a random questions within the given category,
    if provided, and that is not one of the previous questions.

    TEST: In the "Play" tab, after a user selects "All" or a category,
    one question at a time is displayed, the user is allowed to answer
    and shown whether they were correct or not.
    """
    @app.route('/quizzes', methods=['POST'])
    def play_quiz():
        try:
            request_body = request.get_json()
            previous_questions = request_body.get('previous_questions')
            quiz_category = request_body.get('quiz_category')

            if not ('previous_questions' in request_body and 'quiz_category' in request_body):
                abort(422)

            print(request_body)
            # print(quiz_category)
            category_type = quiz_category['type']

            if (category_type == 'click'):
                questions = Question.query.filter(
                    Question.id.notin_(previous_questions)).all()
            else:
                questions = Question.query.filter(Question.id.notin_(previous_questions)).filter(
                    Question.category == quiz_category['id']).all()

            if (len(questions) == 0):
                question = None
            else:
                index = random.randint(0, len(questions)-1)
                question = questions[index].format()

            # print(request_body)
            return jsonify({
                'success': True,
                'question': question
            })
        except:
            abort(422)
    """
    Create error handlers for all expected errors
    including 404 and 422.
    """
    @app.errorhandler(404)
    def page_not_found(e):

        return jsonify({
            "success": False,
            "error": 404,
            "message": "Resource not found"
        }), 404

    @app.errorhandler(422)
    def unprocessable(e):
        return jsonify({
            'success': False,
            'error': 422,
            'message': 'Unprocessable request'
        }), 422

    return app

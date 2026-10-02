# database.py

import sqlite3
import json
import os
from datetime import datetime


# ============================================================
# DATABASE CONFIGURATION
# ============================================================

DATA_FOLDER = "data"
DATABASE_PATH = os.path.join(DATA_FOLDER, "interview.db")


def get_connection():
    """
    Creates and returns a SQLite database connection.
    """

    os.makedirs(DATA_FOLDER, exist_ok=True)

    connection = sqlite3.connect(DATABASE_PATH)
    connection.row_factory = sqlite3.Row

    # Enable foreign key support
    connection.execute("PRAGMA foreign_keys = ON")

    return connection


# ============================================================
# INITIALIZE DATABASE
# ============================================================

def initialize_database():
    """
    Creates all required database tables.
    """

    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS interviews (
            id INTEGER PRIMARY KEY AUTOINCREMENT,

            candidate_name TEXT NOT NULL,
            role TEXT NOT NULL,
            skills TEXT NOT NULL,
            experience TEXT NOT NULL,
            difficulty TEXT NOT NULL,
            interview_type TEXT NOT NULL,
            number_of_questions INTEGER NOT NULL,

            total_score REAL DEFAULT 0,
            maximum_score REAL DEFAULT 0,
            percentage REAL DEFAULT 0,

            status TEXT DEFAULT 'IN_PROGRESS',

            created_at TEXT NOT NULL
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS questions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,

            interview_id INTEGER NOT NULL,

            question_number INTEGER NOT NULL,
            question_text TEXT NOT NULL,

            rubric TEXT,

            candidate_answer TEXT,

            score REAL DEFAULT 0,
            max_score REAL DEFAULT 10,

            evaluation TEXT,

            FOREIGN KEY (interview_id)
                REFERENCES interviews(id)
                ON DELETE CASCADE
        )
    """)

    connection.commit()
    connection.close()


# ============================================================
# CREATE INTERVIEW
# ============================================================

def create_interview(
    candidate_name,
    role,
    skills,
    experience,
    difficulty,
    interview_type,
    number_of_questions
):
    """
    Creates a new interview and returns its database ID.
    """

    connection = get_connection()
    cursor = connection.cursor()

    created_at = datetime.now().isoformat(
        timespec="seconds"
    )

    cursor.execute(
        """
        INSERT INTO interviews (
            candidate_name,
            role,
            skills,
            experience,
            difficulty,
            interview_type,
            number_of_questions,
            created_at
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (
            candidate_name,
            role,
            skills,
            experience,
            difficulty,
            interview_type,
            number_of_questions,
            created_at
        )
    )

    interview_id = cursor.lastrowid

    connection.commit()
    connection.close()

    return interview_id


# ============================================================
# SAVE QUESTION
# ============================================================

def save_question(
    interview_id,
    question_number,
    question_text,
    rubric
):
    """
    Saves a generated question and its rubric.
    """

    connection = get_connection()
    cursor = connection.cursor()

    rubric_json = json.dumps(rubric)

    cursor.execute(
        """
        INSERT INTO questions (
            interview_id,
            question_number,
            question_text,
            rubric
        )
        VALUES (?, ?, ?, ?)
        """,
        (
            interview_id,
            question_number,
            question_text,
            rubric_json
        )
    )

    question_id = cursor.lastrowid

    connection.commit()
    connection.close()

    return question_id


# ============================================================
# GET INTERVIEW
# ============================================================

def get_interview(interview_id):
    """
    Returns one interview.
    """

    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute(
        """
        SELECT *
        FROM interviews
        WHERE id = ?
        """,
        (interview_id,)
    )

    row = cursor.fetchone()

    connection.close()

    if row:
        return dict(row)

    return None


# ============================================================
# GET QUESTIONS
# ============================================================

def get_interview_questions(interview_id):
    """
    Returns all questions belonging to an interview.
    """

    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute(
        """
        SELECT *
        FROM questions
        WHERE interview_id = ?
        ORDER BY question_number
        """,
        (interview_id,)
    )

    rows = cursor.fetchall()

    connection.close()

    questions = []

    for row in rows:

        question = dict(row)

        if question["rubric"]:

            try:
                question["rubric"] = json.loads(
                    question["rubric"]
                )

            except json.JSONDecodeError:
                question["rubric"] = {}

        else:
            question["rubric"] = {}

        if question["evaluation"]:

            try:
                question["evaluation"] = json.loads(
                    question["evaluation"]
                )

            except json.JSONDecodeError:
                question["evaluation"] = {}

        else:
            question["evaluation"] = None

        questions.append(question)

    return questions


# ============================================================
# GET SINGLE QUESTION
# ============================================================

def get_question(question_id):
    """
    Returns one question by database ID.
    """

    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute(
        """
        SELECT *
        FROM questions
        WHERE id = ?
        """,
        (question_id,)
    )

    row = cursor.fetchone()

    connection.close()

    if not row:
        return None

    question = dict(row)

    if question["rubric"]:

        try:
            question["rubric"] = json.loads(
                question["rubric"]
            )

        except json.JSONDecodeError:
            question["rubric"] = {}

    else:
        question["rubric"] = {}

    if question["evaluation"]:

        try:
            question["evaluation"] = json.loads(
                question["evaluation"]
            )

        except json.JSONDecodeError:
            question["evaluation"] = {}

    else:
        question["evaluation"] = None

    return question


# ============================================================
# SAVE ANSWER AND EVALUATION
# ============================================================

def save_evaluation(
    question_id,
    candidate_answer,
    evaluation
):
    """
    Saves candidate answer and its LLM evaluation.
    """

    connection = get_connection()
    cursor = connection.cursor()

    evaluation_json = json.dumps(evaluation)

    score = float(
        evaluation.get(
            "score",
            0
        )
    )

    max_score = float(
        evaluation.get(
            "max_score",
            10
        )
    )

    cursor.execute(
        """
        UPDATE questions

        SET
            candidate_answer = ?,
            score = ?,
            max_score = ?,
            evaluation = ?

        WHERE id = ?
        """,
        (
            candidate_answer,
            score,
            max_score,
            evaluation_json,
            question_id
        )
    )

    connection.commit()
    connection.close()


# ============================================================
# COMPLETE INTERVIEW
# ============================================================

def complete_interview(interview_id):
    """
    Calculates the overall interview result.
    """

    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute(
        """
        SELECT
            SUM(score) AS total_score,
            SUM(max_score) AS maximum_score

        FROM questions

        WHERE interview_id = ?
        """,
        (interview_id,)
    )

    result = cursor.fetchone()

    total_score = float(
        result["total_score"] or 0
    )

    maximum_score = float(
        result["maximum_score"] or 0
    )

    if maximum_score > 0:

        percentage = (
            total_score / maximum_score
        ) * 100

    else:

        percentage = 0

    cursor.execute(
        """
        UPDATE interviews

        SET
            total_score = ?,
            maximum_score = ?,
            percentage = ?,
            status = 'COMPLETED'

        WHERE id = ?
        """,
        (
            total_score,
            maximum_score,
            percentage,
            interview_id
        )
    )

    connection.commit()
    connection.close()

    return {
        "total_score": round(
            total_score,
            2
        ),

        "maximum_score": round(
            maximum_score,
            2
        ),

        "percentage": round(
            percentage,
            2
        )
    }


# ============================================================
# INTERVIEW HISTORY
# ============================================================

def get_interview_history():
    """
    Returns all previous interviews.
    """

    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute(
        """
        SELECT *
        FROM interviews
        ORDER BY id DESC
        """
    )

    rows = cursor.fetchall()

    connection.close()

    return [
        dict(row)
        for row in rows
    ]
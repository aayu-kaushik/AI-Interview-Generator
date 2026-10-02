# services.py

import json

from llm import generate_llm_response

from prompts import (
    create_question_prompt,
    create_rubric_prompt,
    create_evaluation_prompt
)

from database import (
    create_interview,
    save_question,
    get_interview,
    get_interview_questions,
    save_evaluation,
    complete_interview
)

from utils import (
    clean_json_response,
    parse_questions,
    validate_rubric,
    validate_evaluation,
    get_performance_label
)


# ============================================================
# GENERATE QUESTIONS
# ============================================================

def generate_questions(
    role,
    skills,
    experience,
    difficulty,
    interview_type,
    number_of_questions
):
    """
    Generates interview questions using the LLM.
    """

    prompt = create_question_prompt(
        role=role,
        skills=skills,
        experience=experience,
        difficulty=difficulty,
        interview_type=interview_type,
        number_of_questions=number_of_questions
    )

    response = generate_llm_response(
        prompt
    )

    if not response:
        return []

    questions = parse_questions(
        response
    )

    return questions[
        :number_of_questions
    ]


# ============================================================
# GENERATE RUBRIC
# ============================================================

def generate_rubric(
    question,
    role,
    difficulty
):
    """
    Generates and validates an evaluation rubric.
    """

    prompt = create_rubric_prompt(
        question=question,
        role=role,
        difficulty=difficulty
    )

    response = generate_llm_response(
        prompt
    )

    if not response:
        return None

    rubric = clean_json_response(
        response
    )

    if not rubric:
        return None

    if not validate_rubric(
        rubric
    ):
        return None

    return rubric


# ============================================================
# CREATE FULL INTERVIEW
# ============================================================

def create_ai_interview(
    candidate_name,
    role,
    skills,
    experience,
    difficulty,
    interview_type,
    number_of_questions
):
    """
    Creates an interview, generates questions,
    generates rubrics and stores everything.
    """

    interview_id = create_interview(
        candidate_name=candidate_name,
        role=role,
        skills=skills,
        experience=experience,
        difficulty=difficulty,
        interview_type=interview_type,
        number_of_questions=number_of_questions
    )

    questions = generate_questions(
        role=role,
        skills=skills,
        experience=experience,
        difficulty=difficulty,
        interview_type=interview_type,
        number_of_questions=number_of_questions
    )

    if not questions:

        return {
            "success": False,
            "message": "Question generation failed.",
            "interview_id": interview_id
        }

    saved_questions = 0

    for index, question in enumerate(
        questions,
        start=1
    ):

        rubric = generate_rubric(
            question=question,
            role=role,
            difficulty=difficulty
        )

        if not rubric:
            continue

        save_question(
            interview_id=interview_id,
            question_number=index,
            question_text=question,
            rubric=rubric
        )

        saved_questions += 1

    if saved_questions == 0:

        return {
            "success": False,
            "message": (
                "Questions were generated, but "
                "rubric generation failed."
            ),
            "interview_id": interview_id
        }

    return {
        "success": True,
        "message": "Interview created successfully.",
        "interview_id": interview_id,
        "questions_created": saved_questions
    }


# ============================================================
# EVALUATE ONE ANSWER
# ============================================================

def evaluate_answer(
    interview_id,
    question_id,
    candidate_answer
):
    """
    Evaluates one candidate answer using
    the stored rubric.
    """

    interview = get_interview(
        interview_id
    )

    if not interview:

        return {
            "success": False,
            "message": "Interview not found."
        }

    questions = get_interview_questions(
        interview_id
    )

    selected_question = None

    for question in questions:

        if question["id"] == question_id:

            selected_question = question
            break

    if not selected_question:

        return {
            "success": False,
            "message": "Question not found."
        }

    if not candidate_answer.strip():

        candidate_answer = (
            "Candidate did not provide an answer."
        )

    prompt = create_evaluation_prompt(
        question=selected_question[
            "question_text"
        ],
        candidate_answer=candidate_answer,
        rubric=json.dumps(
            selected_question["rubric"]
        ),
        role=interview["role"],
        difficulty=interview["difficulty"]
    )

    response = generate_llm_response(
        prompt
    )

    if not response:

        return {
            "success": False,
            "message": "LLM evaluation failed."
        }

    evaluation = clean_json_response(
        response
    )

    if not evaluation:

        return {
            "success": False,
            "message": (
                "Could not process LLM evaluation."
            )
        }

    if not validate_evaluation(
        evaluation
    ):

        return {
            "success": False,
            "message": (
                "LLM returned an invalid evaluation."
            )
        }

    save_evaluation(
        question_id=question_id,
        candidate_answer=candidate_answer,
        evaluation=evaluation
    )

    return {
        "success": True,
        "evaluation": evaluation
    }


# ============================================================
# FINALIZE INTERVIEW
# ============================================================

def finalize_interview(
    interview_id
):
    """
    Calculates the final score and returns
    complete interview information.
    """

    result = complete_interview(
        interview_id
    )

    interview = get_interview(
        interview_id
    )

    questions = get_interview_questions(
        interview_id
    )

    performance = get_performance_label(
        result["percentage"]
    )

    return {
        "interview": interview,
        "questions": questions,
        "result": result,
        "performance": performance
    }


# ============================================================
# LOAD INTERVIEW
# ============================================================

def load_interview(
    interview_id
):
    """
    Returns interview details and questions.
    Useful for the frontend.
    """

    interview = get_interview(
        interview_id
    )

    if not interview:

        return None

    questions = get_interview_questions(
        interview_id
    )

    return {
        "interview": interview,
        "questions": questions
    }
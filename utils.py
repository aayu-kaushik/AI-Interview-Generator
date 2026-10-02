# utils.py

import json
import re


# ============================================================
# CLEAN LLM JSON RESPONSE
# ============================================================

def clean_json_response(response):
    """
    Converts an LLM JSON response into a Python dictionary.

    Also removes markdown code blocks if the LLM
    accidentally returns them.
    """

    if not response:
        return None

    response = response.strip()

    # Remove ```json
    if response.startswith("```json"):
        response = response[7:]

    # Remove ```
    elif response.startswith("```"):
        response = response[3:]

    # Remove ending ```
    if response.endswith("```"):
        response = response[:-3]

    response = response.strip()

    try:
        return json.loads(response)

    except json.JSONDecodeError as error:

        print("JSON Parsing Error:", error)
        print("Raw Response:", response)

        return None


# ============================================================
# PARSE GENERATED QUESTIONS
# ============================================================

def parse_questions(response):
    """
    Converts numbered interview questions returned
    by the LLM into a Python list.
    """

    if not response:
        return []

    questions = []

    current_question = ""

    for line in response.splitlines():

        line = line.strip()

        if not line:
            continue

        # Matches:
        # 1. Question
        # 2. Question
        # 3) Question

        match = re.match(
            r"^\d+[\.\)]\s*(.*)",
            line
        )

        if match:

            if current_question:

                questions.append(
                    current_question.strip()
                )

            current_question = match.group(1)

        else:

            if current_question:

                current_question += (
                    " " + line
                )

    if current_question:

        questions.append(
            current_question.strip()
        )

    return questions


# ============================================================
# VALIDATE RUBRIC
# ============================================================

def validate_rubric(rubric):
    """
    Checks whether an LLM-generated rubric
    has the expected structure.
    """

    if not isinstance(rubric, dict):
        return False

    if rubric.get("total_marks") != 10:
        return False

    criteria = rubric.get("criteria")

    if not isinstance(criteria, list):
        return False

    if len(criteria) == 0:
        return False

    total_marks = 0

    for item in criteria:

        if not isinstance(item, dict):
            return False

        if "criterion" not in item:
            return False

        if "marks" not in item:
            return False

        try:
            marks = float(item["marks"])

        except (TypeError, ValueError):
            return False

        if marks < 0:
            return False

        total_marks += marks

    return total_marks == 10


# ============================================================
# VALIDATE EVALUATION
# ============================================================

def validate_evaluation(evaluation):
    """
    Checks whether an LLM evaluation contains
    the minimum required fields.
    """

    if not isinstance(evaluation, dict):
        return False

    required_fields = [
        "score",
        "max_score",
        "criterion_scores",
        "strengths",
        "missing_concepts",
        "feedback",
        "ideal_answer"
    ]

    for field in required_fields:

        if field not in evaluation:
            return False

    try:

        score = float(
            evaluation["score"]
        )

        max_score = float(
            evaluation["max_score"]
        )

    except (TypeError, ValueError):

        return False

    if score < 0:
        return False

    if max_score <= 0:
        return False

    if score > max_score:
        return False

    if not isinstance(
        evaluation["criterion_scores"],
        list
    ):
        return False

    if not isinstance(
        evaluation["strengths"],
        list
    ):
        return False

    if not isinstance(
        evaluation["missing_concepts"],
        list
    ):
        return False

    return True


# ============================================================
# PERFORMANCE LABEL
# ============================================================

def get_performance_label(percentage):
    """
    Returns a simple performance label.
    """

    if percentage >= 85:
        return "Excellent"

    elif percentage >= 70:
        return "Good"

    elif percentage >= 50:
        return "Average"

    else:
        return "Needs Improvement"
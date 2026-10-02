# prompts.py
# Contains all LLM prompts used in the AI Interview Generator.


# ============================================================
# 1. INTERVIEW QUESTION GENERATION PROMPT
# ============================================================

def create_question_prompt(
    role,
    skills,
    experience,
    difficulty,
    interview_type,
    number_of_questions
):
    """
    Creates a prompt for generating interview questions.
    """

    prompt = f"""
You are an expert professional interviewer.

Generate {number_of_questions} interview questions for the following candidate.

Candidate Details:

Job Role: {role}
Skills: {skills}
Experience Level: {experience}
Difficulty Level: {difficulty}
Interview Type: {interview_type}

Requirements:

1. Questions must be relevant to the specified job role.
2. Questions should primarily focus on the provided skills.
3. Questions must match the requested difficulty level.
4. Questions must be appropriate for the candidate's experience level.
5. Questions must match the selected interview type.
6. Avoid duplicate or near-duplicate questions.
7. Questions should resemble questions asked in real interviews.
8. Include conceptual, practical, and problem-solving questions where appropriate.
9. Do not provide answers or hints.
10. Generate exactly {number_of_questions} questions.

Return only the numbered interview questions.

Example:

1. First interview question?
2. Second interview question?
3. Third interview question?
"""

    return prompt.strip()


# ============================================================
# 2. RUBRIC GENERATION PROMPT
# ============================================================

def create_rubric_prompt(
    question,
    role,
    difficulty
):
    """
    Creates an evaluation rubric for an interview question.
    """

    prompt = f"""
You are an expert interview evaluator.

Create a detailed evaluation rubric for the following interview question.

Interview Information:

Job Role: {role}
Difficulty Level: {difficulty}

Interview Question:

{question}

The rubric will later be used to evaluate a candidate's answer.

The maximum score must be exactly 10 marks.

Evaluation criteria should focus on:

- Technical correctness
- Important concepts
- Completeness
- Reasoning
- Clarity
- Practical understanding where appropriate

Return ONLY valid JSON using this structure:

{{
    "question": "{question}",
    "total_marks": 10,
    "criteria": [
        {{
            "criterion": "First evaluation criterion",
            "marks": 3
        }},
        {{
            "criterion": "Second evaluation criterion",
            "marks": 3
        }},
        {{
            "criterion": "Third evaluation criterion",
            "marks": 2
        }},
        {{
            "criterion": "Fourth evaluation criterion",
            "marks": 2
        }}
    ]
}}

Important Rules:

1. Total marks MUST equal exactly 10.
2. Criteria must be directly related to the question.
3. Criteria must be clear and measurable.
4. Do not generate vague criteria.
5. Do not provide the candidate's answer.
6. Do not provide an ideal answer.
7. Do not include explanations outside JSON.
8. Do not use markdown.
9. Do not use ```json.
10. Return valid JSON only.
"""

    return prompt.strip()


# ============================================================
# 3. CANDIDATE ANSWER EVALUATION PROMPT
# ============================================================

def create_evaluation_prompt(
    question,
    candidate_answer,
    rubric,
    role,
    difficulty
):
    """
    Creates a prompt for evaluating a candidate's answer
    using the generated rubric.
    """

    prompt = f"""
You are an expert interview evaluator.

Evaluate the candidate's answer strictly according to the
provided evaluation rubric.

Interview Information:

Job Role: {role}
Difficulty Level: {difficulty}

Interview Question:

{question}

Candidate Answer:

{candidate_answer}

Evaluation Rubric:

{rubric}

Instructions:

1. Evaluate the candidate only against the supplied rubric.
2. Award marks according to how well each criterion is satisfied.
3. The final score must be between 0 and 10.
4. Do not award marks for incorrect information.
5. Give partial marks when the candidate demonstrates partial understanding.
6. Identify what the candidate explained correctly.
7. Identify important concepts that were missing or incorrect.
8. Give constructive feedback explaining how the answer can improve.
9. Generate a concise ideal answer.
10. Do not be unnecessarily harsh or generous.
11. The sum of criterion scores must equal the final score.

Return ONLY valid JSON using this exact structure:

{{
    "score": 0,
    "max_score": 10,

    "criterion_scores": [
        {{
            "criterion": "Criterion from rubric",
            "marks_awarded": 0,
            "maximum_marks": 0,
            "reason": "Reason for awarded marks"
        }}
    ],

    "strengths": [
        "Strength 1",
        "Strength 2"
    ],

    "missing_concepts": [
        "Missing concept 1",
        "Missing concept 2"
    ],

    "feedback": "Detailed constructive feedback for the candidate.",

    "ideal_answer": "A concise but complete ideal answer to the interview question."
}}

Important Rules:

1. score must never exceed 10.
2. score must never be below 0.
3. criterion scores must follow the supplied rubric.
4. The sum of marks_awarded must equal score.
5. maximum_marks must correspond to the rubric.
6. Do not invent additional rubric criteria.
7. Return valid JSON only.
8. Do not use markdown formatting.
9. Do not use ```json.
10. Do not include text outside the JSON.
"""

    return prompt.strip()
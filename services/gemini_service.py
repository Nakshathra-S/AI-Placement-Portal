import json
import logging
import requests
from config import Config

logger = logging.getLogger(__name__)

GEMINI_API_URL = "https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent?key={api_key}"

def call_gemini_api(prompt, system_instruction=None, json_mode=True):
    """
    Calls Google Gemini API via REST.
    Returns parsed JSON if json_mode=True, or text string.
    Raises Exception if API call fails or key is missing.
    """
    api_key = Config.GEMINI_API_KEY
    if not api_key:
        raise ValueError("GEMINI_API_KEY is not configured in .env file.")

    model = Config.GEMINI_MODEL or "gemini-1.5-flash"
    url = GEMINI_API_URL.format(model=model, api_key=api_key)

    contents = []
    if system_instruction:
        contents.append({
            "role": "user",
            "parts": [{"text": f"SYSTEM INSTRUCTION:\n{system_instruction}\n\nUSER PROMPT:\n{prompt}"}]
        })
    else:
        contents.append({
            "role": "user",
            "parts": [{"text": prompt}]
        })

    payload = {
        "contents": contents,
        "generationConfig": {
            "temperature": 0.2,
            "topP": 0.8,
            "maxOutputTokens": 2048
        }
    }

    if json_mode:
        payload["generationConfig"]["responseMimeType"] = "application/json"

    headers = {"Content-Type": "application/json"}
    response = requests.post(url, headers=headers, json=payload, timeout=25)
    
    if response.status_code != 200:
        error_msg = f"Gemini API error {response.status_code}: {response.text}"
        logger.error(error_msg)
        raise RuntimeError(error_msg)

    res_json = response.json()
    try:
        candidates = res_json.get("candidates", [])
        if not candidates:
            raise ValueError("No candidate responses returned by Gemini API.")
        
        parts = candidates[0].get("content", {}).get("parts", [])
        if not parts:
            raise ValueError("Empty response parts from Gemini API.")
        
        text_output = parts[0].get("text", "").strip()

        if json_mode:
            # Clean possible markdown wrapping e.g. ```json ... ```
            cleaned = text_output
            if cleaned.startswith("```json"):
                cleaned = cleaned[7:]
            if cleaned.startswith("```"):
                cleaned = cleaned[3:]
            if cleaned.endswith("```"):
                cleaned = cleaned[:-3]
            return json.loads(cleaned.strip())
        
        return text_output
    except json.JSONDecodeError as jde:
        logger.error(f"Failed to parse JSON from Gemini response: {text_output}")
        raise ValueError(f"Invalid JSON returned by Gemini: {jde}")

# ----------------- TECHNICAL INTERVIEW SERVICE -----------------

def generate_technical_questions_ai(job_role):
    prompt = f"""
Generate 5 authentic, challenging, industry-standard technical interview questions for a candidate applying for the role of: '{job_role}'.
Requirements:
- Questions must be conceptual, practical, and scenario-based.
- Cover fundamental principles, architectural decisions, and debugging/performance trade-offs.
- Avoid trivia; focus on depth.

Return ONLY a JSON array with 5 objects:
[
  {{
    "id": 1,
    "question": "Question text here..."
  }},
  ...
]
"""
    return call_gemini_api(prompt, json_mode=True)

def evaluate_technical_answer_ai(job_role, question_text, submitted_answer):
    system_instruction = """You are a strict, senior technical interviewer and engineering manager at a top tech company.
You grade student answers strictly and realistically.
Scoring Rubric:
- Score is on a scale of 0 to 10 (decimals allowed, e.g. 6.5).
- Under 20 words or trivial answers: Score 0-2/10.
- Factual errors or made-up claims: Penalize heavily.
- Mentioning buzzwords without explaining concepts: Score <= 4/10.
- Partially correct: 4-6/10.
- Good conceptual answer with minor missing nuances: 7-8/10.
- Comprehensive, factually accurate, structured with trade-offs: 9-10/10.
Do NOT invent errors or claim correct statements are wrong. Provide concrete evidence."""

    prompt = f"""
Target Job Role: {job_role}
Interview Question: {question_text}
Candidate's Submitted Answer:
\"\"\"{submitted_answer}\"\"\"

Analyze the answer with strict grading.
Return ONLY a valid JSON object matching this exact structure:
{{
  "score": 6.5,
  "score_breakdown": {{
    "conceptual_accuracy": 7,
    "factual_correctness": 6,
    "completeness": 6,
    "clarity": 7
  }},
  "strengths": "What the candidate answered correctly...",
  "missing_concepts": "Key concepts or details the candidate missed or stated incorrectly...",
  "feedback": "Honest, constructive evaluation of the answer...",
  "model_answer": "A technically accurate, structured, and complete model answer that would receive a 10/10...",
  "suggestions": "2-3 actionable tips to improve technical answers for this topic."
}}
"""
    return call_gemini_api(prompt, system_instruction=system_instruction, json_mode=True)

# ----------------- HR INTERVIEW SERVICE -----------------

def evaluate_hr_answer_ai(question_text, submitted_answer):
    system_instruction = """You are an experienced HR Director conducting campus placements.
Evaluate candidate behavioral answers strictly using communication quality, professionalism, relevance, and the STAR framework (Situation, Task, Action, Result) where applicable.
Score is on a scale of 0 to 10."""

    prompt = f"""
HR Question: {question_text}
Candidate's Answer:
\"\"\"{submitted_answer}\"\"\"

Evaluate the answer.
Return ONLY a JSON object with this exact structure:
{{
  "score": 7.0,
  "score_breakdown": {{
    "situation": 7,
    "task": 6,
    "action": 7,
    "result": 7,
    "professionalism": 8
  }},
  "strengths": "Positive aspects, good framing or attitude displayed...",
  "weaknesses": "Weak points, vagueness, lack of metric results, or missing STAR aspects...",
  "feedback": "Detailed assessment of clarity, tone, and impact...",
  "model_answer": "An exemplary, professional model response demonstrating strong behavioral communication...",
  "suggestions": "Practical advice for structuring and delivering this HR response."
}}
"""
    return call_gemini_api(prompt, system_instruction=system_instruction, json_mode=True)

# ----------------- GROUP DISCUSSION SERVICE -----------------

def generate_gd_topic_ai():
    prompt = """
Generate a thought-provoking, contemporary Group Discussion (GD) topic suitable for campus placements.
Provide the topic title, category, background context, and key perspectives (Pro/Con/Nuance).
Return ONLY a JSON object:
{{
  "topic": "Topic Title Here",
  "category": "Technology / Economy / Social Issues / Workplace",
  "context": "Short 2-sentence background explaining why this topic is currently relevant.",
  "guiding_points": [
    "Key argument 1",
    "Key argument 2",
    "Key counterargument"
  ]
}}
"""
    return call_gemini_api(prompt, json_mode=True)

def evaluate_gd_opinion_ai(topic, submitted_opinion):
    system_instruction = """You are a senior GD placement moderator and soft skills trainer.
Evaluate candidate group discussion statements strictly based on logic, relevance, depth, supporting examples, balance, and communication quality.
Do not reward an opinion merely because it agrees with one viewpoint. Fairly evaluate reasoning.
Score is on a scale of 0 to 10."""

    prompt = f"""
GD Topic: {topic}
Candidate's Discussion Contribution:
\"\"\"{submitted_opinion}\"\"\"

Evaluate the contribution.
Return ONLY a JSON object with this exact structure:
{{
  "score": 6.0,
  "score_breakdown": {{
    "relevance": 7,
    "argument_quality": 6,
    "logical_structure": 6,
    "supporting_examples": 5,
    "communication": 6
  }},
  "strengths": "Strong arguments, clear points, or good examples used...",
  "weaknesses": "Logical flaws, unsupported generalizations, or repetitive statements...",
  "counterarguments": "Important counterarguments or alternative perspectives the candidate failed to acknowledge...",
  "feedback": "Honest assessment of the candidate's contribution to the GD...",
  "model_discussion": "A strong, balanced, multi-perspective model contribution that exemplifies top GD performance."
}}
"""
    return call_gemini_api(prompt, system_instruction=system_instruction, json_mode=True)

# ----------------- ENGLISH COMMUNICATION & GRAMMAR SERVICE -----------------

def analyze_english_text_ai(input_text):
    system_instruction = """You are a strict professional business English evaluator and linguistic assessor.
Analyze the candidate's written paragraph for grammar, vocabulary, tone, sentence structure, and clarity.
Score is on a scale of 0 to 10.
Rubric:
- 0-4: POOR (frequent grammatical errors, informal slang, fragmented sentences, awkward phrasing)
- 5-6: FAIR (comprehensible, but noticeable errors in grammar, punctuation, or basic vocabulary)
- 7-8: GOOD (clear, grammatically sound, minor stylistic improvements needed)
- 9-10: EXCELLENT (impeccable grammar, sophisticated professional vocabulary, fluent structure)

Placement Readiness Calibration = Score * 10 (0% - 100%).
Categories (each 0-10):
- Clarity
- Grammar
- Sentence Structure
- Tone
- Vocabulary
Preserve the user's intended core meaning when providing the corrected text."""

    prompt = f"""
Input Text to Analyze:
\"\"\"{input_text}\"\"\"

Analyze with high linguistic precision.
Return ONLY a JSON object matching this exact structure:
{{
  "score": 4.0,
  "status_badge": "POOR",
  "readiness_percentage": 40,
  "score_breakdown": {{
    "clarity": 4,
    "grammar": 3,
    "sentence_structure": 4,
    "tone": 2,
    "vocabulary": 4
  }},
  "corrections": [
    {{
      "original": "gets real different",
      "corrected": "changes significantly",
      "reason": "Informal phrasing replaced with precise professional vocabulary."
    }},
    {{
      "original": "We is burning",
      "corrected": "We are burning",
      "reason": "Subject-verb agreement error: 'We' requires plural verb 'are'."
    }}
  ],
  "corrected_text": "A polished, grammatically perfect, and professionally phrased version preserving the author's original message...",
  "feedback": "Overall assessment of readability, tone suitability for placement interviews, and key error patterns.",
  "suggestions": "Practical guidelines to elevate writing style, sentence variety, and professional workplace communication."
}}
"""
    return call_gemini_api(prompt, system_instruction=system_instruction, json_mode=True)

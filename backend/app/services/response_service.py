import re
from fastapi import HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Dict, Any
from collections import Counter

from app.repositories.form_repo import FormRepository
from app.repositories.response_repo import ResponseRepository
from app.repositories.question_repo import QuestionRepository
from app.models.form import FormStatus
from app.models.question import QuestionType
from app.schemas.response import (
    ResponseSubmit, ResponseOut, ResponseSummary,
    FormAnalytics, QuestionAnalytics, ChoiceDistribution, ResponseAnswerOut
)


def validate_answer(question, answer_value: str) -> str:
    """Validate a single answer against its question type. Returns cleaned value."""
    q_type = question.type
    settings = question.settings or {}

    if question.required and (answer_value is None or answer_value.strip() == ""):
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"Question '{question.title}' is required"
        )

    if answer_value is None or answer_value.strip() == "":
        return answer_value  # Optional and empty is fine

    val = answer_value.strip()

    if q_type == QuestionType.email:
        email_regex = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        if not re.match(email_regex, val):
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail=f"Invalid email address for question '{question.title}'"
            )

    elif q_type == QuestionType.number:
        try:
            num = float(val)
            min_val = settings.get("min_value")
            max_val = settings.get("max_value")
            if min_val is not None and num < min_val:
                raise HTTPException(
                    status_code=422,
                    detail=f"Value must be at least {min_val}"
                )
            if max_val is not None and num > max_val:
                raise HTTPException(
                    status_code=422,
                    detail=f"Value must be at most {max_val}"
                )
        except ValueError:
            raise HTTPException(
                status_code=422,
                detail=f"Invalid number for question '{question.title}'"
            )

    elif q_type == QuestionType.rating:
        try:
            rating = int(val)
            max_rating = settings.get("max_rating", 5)
            if rating < 1 or rating > max_rating:
                raise HTTPException(
                    status_code=422,
                    detail=f"Rating must be between 1 and {max_rating}"
                )
        except ValueError:
            raise HTTPException(status_code=422, detail="Invalid rating value")

    elif q_type == QuestionType.multiple_choice:
        choices = settings.get("choices", [])
        allow_other = settings.get("allow_other", False)
        if choices and val not in choices and not allow_other:
            raise HTTPException(
                status_code=422,
                detail=f"Invalid choice for question '{question.title}'"
            )

    elif q_type == QuestionType.dropdown:
        choices = settings.get("choices", [])
        if choices and val not in choices:
            raise HTTPException(
                status_code=422,
                detail=f"Invalid option for question '{question.title}'"
            )

    elif q_type == QuestionType.yes_no:
        if val.lower() not in ("yes", "no"):
            raise HTTPException(
                status_code=422,
                detail=f"Answer must be 'Yes' or 'No' for question '{question.title}'"
            )

    return val


class ResponseService:
    def __init__(self, db: Session):
        self.resp_repo = ResponseRepository(db)
        self.form_repo = FormRepository(db)
        self.q_repo = QuestionRepository(db)

    def submit_response(self, public_id: str, data: ResponseSubmit) -> ResponseOut:
        form = self.form_repo.get_by_public_id(public_id)
        if not form:
            raise HTTPException(status_code=404, detail="Form not found")
        if form.status != FormStatus.published:
            raise HTTPException(status_code=403, detail="Form is not published")

        # Build question map for validation
        form_questions = {q.id: q for q in form.questions}

        # Validate each answer
        validated_answers = []
        for ans in data.answers:
            if ans.question_id not in form_questions:
                raise HTTPException(
                    status_code=422,
                    detail=f"Question {ans.question_id} does not belong to this form"
                )
            q = form_questions[ans.question_id]
            cleaned = validate_answer(q, ans.answer_value)
            validated_answers.append(type(ans)(question_id=ans.question_id, answer_value=cleaned))

        # Check all required questions are answered
        answered_ids = {a.question_id for a in data.answers if a.answer_value}
        for q in form.questions:
            if q.required and q.id not in answered_ids:
                raise HTTPException(
                    status_code=422,
                    detail=f"Required question '{q.title}' is missing"
                )

        data.answers = validated_answers
        response = self.resp_repo.create_response(form.id, data)

        # Build response out with question metadata
        answers_out = []
        for ans in response.answers:
            q = form_questions.get(ans.question_id)
            answers_out.append(ResponseAnswerOut(
                id=ans.id,
                question_id=ans.question_id,
                answer_value=ans.answer_value,
                question_title=q.title if q else None,
                question_type=q.type.value if q else None,
            ))

        return ResponseOut(
            id=response.id,
            form_id=response.form_id,
            submitted_at=response.submitted_at,
            completion_status=response.completion_status.value,
            answers=answers_out,
        )

    def get_responses(self, form_id: str) -> List[ResponseSummary]:
        form = self.form_repo.get_by_id(form_id)
        if not form:
            raise HTTPException(status_code=404, detail="Form not found")

        responses = self.resp_repo.get_by_form(form_id)
        result = []
        for r in responses:
            result.append(ResponseSummary(
                id=r.id,
                form_id=r.form_id,
                submitted_at=r.submitted_at,
                completion_status=r.completion_status.value,
                answer_count=len(r.answers),
            ))
        return result

    def get_response(self, response_id: str) -> ResponseOut:
        r = self.resp_repo.get_by_id(response_id)
        if not r:
            raise HTTPException(status_code=404, detail="Response not found")

        answers_out = []
        for ans in r.answers:
            q = ans.question
            answers_out.append(ResponseAnswerOut(
                id=ans.id,
                question_id=ans.question_id,
                answer_value=ans.answer_value,
                question_title=q.title if q else None,
                question_type=q.type.value if q else None,
            ))

        return ResponseOut(
            id=r.id,
            form_id=r.form_id,
            submitted_at=r.submitted_at,
            completion_status=r.completion_status.value,
            answers=answers_out,
        )

    def get_analytics(self, form_id: str) -> FormAnalytics:
        form = self.form_repo.get_by_id(form_id)
        if not form:
            raise HTTPException(status_code=404, detail="Form not found")

        total_responses = self.form_repo.get_response_count(form_id)
        question_analytics = []

        for question in form.questions:
            answers = self.resp_repo.get_answers_for_question(question.id)
            non_empty = [a.answer_value for a in answers if a.answer_value and a.answer_value.strip()]
            total_answers = len(non_empty)

            qa = QuestionAnalytics(
                question_id=question.id,
                question_title=question.title,
                question_type=question.type.value,
                total_answers=total_answers,
            )

            if question.type in (QuestionType.multiple_choice, QuestionType.dropdown):
                counter = Counter(non_empty)
                total = sum(counter.values()) or 1
                qa.distribution = [
                    ChoiceDistribution(
                        option=opt,
                        count=counter.get(opt, 0),
                        percentage=round(counter.get(opt, 0) / total * 100, 1)
                    )
                    for opt in (question.settings or {}).get("choices", list(counter.keys()))
                ]

            elif question.type == QuestionType.yes_no:
                counter = Counter(v.lower() for v in non_empty)
                total = sum(counter.values()) or 1
                qa.distribution = [
                    ChoiceDistribution(option="Yes", count=counter.get("yes", 0),
                                       percentage=round(counter.get("yes", 0) / total * 100, 1)),
                    ChoiceDistribution(option="No", count=counter.get("no", 0),
                                       percentage=round(counter.get("no", 0) / total * 100, 1)),
                ]

            elif question.type == QuestionType.rating:
                numeric = []
                rating_dist: Dict[str, int] = {}
                for v in non_empty:
                    try:
                        n = int(v)
                        numeric.append(n)
                        rating_dist[str(n)] = rating_dist.get(str(n), 0) + 1
                    except (ValueError, TypeError):
                        pass
                if numeric:
                    qa.average = round(sum(numeric) / len(numeric), 2)
                    qa.min_value = float(min(numeric))
                    qa.max_value = float(max(numeric))
                    qa.rating_distribution = rating_dist

            elif question.type == QuestionType.number:
                numeric = []
                for v in non_empty:
                    try:
                        numeric.append(float(v))
                    except (ValueError, TypeError):
                        pass
                if numeric:
                    qa.average = round(sum(numeric) / len(numeric), 2)
                    qa.min_value = min(numeric)
                    qa.max_value = max(numeric)

            question_analytics.append(qa)

        return FormAnalytics(
            form_id=form_id,
            total_responses=total_responses,
            questions=question_analytics,
        )

"""Tests for the Typeform Builder Clone API.
Uses the `client` fixture from conftest.py which properly patches the DB.
"""
import pytest


# ─── Form Tests ─────────────────────────────────────────────────────────────

class TestForms:
    def test_create_form(self, client):
        resp = client.post("/api/forms", json={"title": "Test Form", "description": "A test"})
        assert resp.status_code == 201
        data = resp.json()
        assert data["title"] == "Test Form"
        assert data["status"] == "draft"
        assert "id" in data
        assert "public_id" in data

    def test_list_forms_empty(self, client):
        resp = client.get("/api/forms")
        assert resp.status_code == 200
        assert resp.json() == []

    def test_list_forms_with_data(self, client):
        client.post("/api/forms", json={"title": "Form A"})
        client.post("/api/forms", json={"title": "Form B"})
        resp = client.get("/api/forms")
        assert resp.status_code == 200
        assert len(resp.json()) == 2

    def test_get_form(self, client):
        create_resp = client.post("/api/forms", json={"title": "Get Me"})
        form_id = create_resp.json()["id"]
        resp = client.get(f"/api/forms/{form_id}")
        assert resp.status_code == 200
        assert resp.json()["title"] == "Get Me"

    def test_get_form_not_found(self, client):
        resp = client.get("/api/forms/nonexistent-id")
        assert resp.status_code == 404

    def test_update_form(self, client):
        create_resp = client.post("/api/forms", json={"title": "Old Title"})
        form_id = create_resp.json()["id"]
        resp = client.patch(f"/api/forms/{form_id}", json={"title": "New Title"})
        assert resp.status_code == 200
        assert resp.json()["title"] == "New Title"

    def test_delete_form(self, client):
        create_resp = client.post("/api/forms", json={"title": "Delete Me"})
        form_id = create_resp.json()["id"]
        resp = client.delete(f"/api/forms/{form_id}")
        assert resp.status_code == 204
        # Verify it's gone
        get_resp = client.get(f"/api/forms/{form_id}")
        assert get_resp.status_code == 404

    def test_publish_form(self, client):
        create_resp = client.post("/api/forms", json={"title": "Publish Me"})
        form_id = create_resp.json()["id"]
        resp = client.post(f"/api/forms/{form_id}/publish")
        assert resp.status_code == 200
        data = resp.json()
        assert data["status"] == "published"
        assert data["published_at"] is not None
        assert "public_id" in data

    def test_unpublish_form(self, client):
        create_resp = client.post("/api/forms", json={"title": "Unpublish Me"})
        form_id = create_resp.json()["id"]
        client.post(f"/api/forms/{form_id}/publish")
        resp = client.post(f"/api/forms/{form_id}/unpublish")
        assert resp.status_code == 200
        assert resp.json()["status"] == "draft"

    def test_duplicate_form(self, client):
        # Create form with questions
        create_resp = client.post("/api/forms", json={"title": "Original"})
        form_id = create_resp.json()["id"]
        client.post(f"/api/forms/{form_id}/questions", json={"type": "short_text", "title": "Q1"})
        client.post(f"/api/forms/{form_id}/questions", json={"type": "email", "title": "Q2"})

        resp = client.post(f"/api/forms/{form_id}/duplicate")
        assert resp.status_code == 201
        data = resp.json()
        assert "Copy" in data["title"]
        assert data["status"] == "draft"
        assert len(data["questions"]) == 2
        assert data["id"] != form_id


# ─── Question Tests ─────────────────────────────────────────────────────────

class TestQuestions:
    def _create_form(self, client):
        resp = client.post("/api/forms", json={"title": "Test Form"})
        return resp.json()["id"]

    def test_add_question(self, client):
        form_id = self._create_form(client)
        resp = client.post(f"/api/forms/{form_id}/questions", json={"type": "short_text", "title": "Your name?"})
        assert resp.status_code == 201
        data = resp.json()
        assert data["type"] == "short_text"
        assert data["position"] == 0

    def test_add_multiple_questions_order(self, client):
        form_id = self._create_form(client)
        client.post(f"/api/forms/{form_id}/questions", json={"type": "short_text", "title": "Q1"})
        client.post(f"/api/forms/{form_id}/questions", json={"type": "email", "title": "Q2"})
        client.post(f"/api/forms/{form_id}/questions", json={"type": "rating", "title": "Q3"})
        resp = client.get(f"/api/forms/{form_id}")
        questions = resp.json()["questions"]
        assert len(questions) == 3
        assert [q["position"] for q in questions] == [0, 1, 2]

    def test_update_question(self, client):
        form_id = self._create_form(client)
        q_resp = client.post(f"/api/forms/{form_id}/questions", json={"type": "short_text", "title": "Old"})
        q_id = q_resp.json()["id"]
        resp = client.patch(f"/api/questions/{q_id}", json={"title": "Updated", "required": True})
        assert resp.status_code == 200
        assert resp.json()["title"] == "Updated"
        assert resp.json()["required"] is True

    def test_delete_question(self, client):
        form_id = self._create_form(client)
        q_resp = client.post(f"/api/forms/{form_id}/questions", json={"type": "short_text", "title": "Del"})
        q_id = q_resp.json()["id"]
        resp = client.delete(f"/api/questions/{q_id}")
        assert resp.status_code == 204

    def test_reorder_questions(self, client):
        form_id = self._create_form(client)
        q1 = client.post(f"/api/forms/{form_id}/questions", json={"type": "short_text", "title": "First"}).json()["id"]
        q2 = client.post(f"/api/forms/{form_id}/questions", json={"type": "email", "title": "Second"}).json()["id"]
        q3 = client.post(f"/api/forms/{form_id}/questions", json={"type": "rating", "title": "Third"}).json()["id"]

        # Reverse the order
        resp = client.patch(f"/api/forms/{form_id}/questions/reorder",
                            json={"question_ids": [q3, q2, q1]})
        assert resp.status_code == 200
        questions = resp.json()
        assert questions[0]["id"] == q3
        assert questions[1]["id"] == q2
        assert questions[2]["id"] == q1


# ─── Public Flow Tests ───────────────────────────────────────────────────────

class TestPublicFlow:
    def _setup_form(self, client):
        """Create and publish a form with questions."""
        create_resp = client.post("/api/forms", json={"title": "Public Form"})
        form_id = create_resp.json()["id"]
        client.post(f"/api/forms/{form_id}/questions",
                    json={"type": "short_text", "title": "Your name?", "required": True})
        client.post(f"/api/forms/{form_id}/questions",
                    json={"type": "email", "title": "Your email?", "required": True})
        pub_resp = client.post(f"/api/forms/{form_id}/publish")
        public_id = pub_resp.json()["public_id"]
        return form_id, public_id

    def test_fetch_published_form(self, client):
        _, public_id = self._setup_form(client)
        resp = client.get(f"/api/public/forms/{public_id}")
        assert resp.status_code == 200
        assert resp.json()["status"] == "published"

    def test_fetch_draft_form_returns_403(self, client):
        create_resp = client.post("/api/forms", json={"title": "Draft"})
        public_id = create_resp.json()["public_id"]
        resp = client.get(f"/api/public/forms/{public_id}")
        assert resp.status_code == 403

    def test_submit_response(self, client):
        form_id, public_id = self._setup_form(client)
        form_resp = client.get(f"/api/public/forms/{public_id}").json()
        q_ids = [q["id"] for q in form_resp["questions"]]

        resp = client.post(f"/api/public/forms/{public_id}/responses", json={
            "answers": [
                {"question_id": q_ids[0], "answer_value": "Alice"},
                {"question_id": q_ids[1], "answer_value": "alice@example.com"},
            ]
        })
        assert resp.status_code == 201
        assert resp.json()["form_id"] == form_id

    def test_submit_invalid_email(self, client):
        form_id, public_id = self._setup_form(client)
        form_resp = client.get(f"/api/public/forms/{public_id}").json()
        q_ids = [q["id"] for q in form_resp["questions"]]

        resp = client.post(f"/api/public/forms/{public_id}/responses", json={
            "answers": [
                {"question_id": q_ids[0], "answer_value": "Alice"},
                {"question_id": q_ids[1], "answer_value": "not-an-email"},
            ]
        })
        assert resp.status_code == 422

    def test_submit_missing_required(self, client):
        form_id, public_id = self._setup_form(client)
        form_resp = client.get(f"/api/public/forms/{public_id}").json()
        q_ids = [q["id"] for q in form_resp["questions"]]

        # Only submit first answer, missing required email
        resp = client.post(f"/api/public/forms/{public_id}/responses", json={
            "answers": [
                {"question_id": q_ids[0], "answer_value": "Alice"},
            ]
        })
        assert resp.status_code == 422

    def test_submit_to_unpublished_form(self, client):
        form_id, public_id = self._setup_form(client)
        client.post(f"/api/forms/{form_id}/unpublish")
        resp = client.post(f"/api/public/forms/{public_id}/responses", json={"answers": []})
        assert resp.status_code == 403


# ─── Analytics Tests ─────────────────────────────────────────────────────────

class TestAnalytics:
    def test_get_analytics(self, client):
        create_resp = client.post("/api/forms", json={"title": "Analytics Form"})
        form_id = create_resp.json()["id"]
        client.post(f"/api/forms/{form_id}/questions",
                    json={"type": "rating", "title": "Rate us", "required": True})
        pub_resp = client.post(f"/api/forms/{form_id}/publish")
        public_id = pub_resp.json()["public_id"]
        form_resp = client.get(f"/api/public/forms/{public_id}").json()
        q_id = form_resp["questions"][0]["id"]

        # Submit 3 responses
        for rating in ["4", "5", "3"]:
            client.post(f"/api/public/forms/{public_id}/responses", json={
                "answers": [{"question_id": q_id, "answer_value": rating}]
            })

        resp = client.get(f"/api/forms/{form_id}/analytics")
        assert resp.status_code == 200
        data = resp.json()
        assert data["total_responses"] == 3
        assert len(data["questions"]) == 1
        assert data["questions"][0]["average"] == pytest.approx(4.0)

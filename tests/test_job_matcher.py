from job_matcher import _experience_score, calculate_match, match_job, normalize


class TestNormalize:
    def test_normalize_basic(self):
        # normalize() lowercases and collapses internal whitespace but preserves leading/trailing
        result = normalize("  Hello   World  ")
        assert result == " hello world "
        assert "hello world" in result.strip()

    def test_normalize_none(self):
        assert normalize(None) == ""

    def test_normalize_empty(self):
        assert normalize("") == ""

    def test_normalize_newlines(self):
        assert normalize("hello\nworld") == "hello world"


class TestExperienceScore:
    def test_experience_2_5_years(self):
        assert _experience_score("3 years experience") == 10
        assert _experience_score("2-5 years") == 10
        assert _experience_score("4 years") == 10

    def test_experience_6_years(self):
        assert _experience_score("6 years") == 5

    def test_experience_7_plus_years(self):
        assert _experience_score("7 years") == -15
        assert _experience_score("10+ years") == -15

    def test_experience_no_match(self):
        assert _experience_score("no experience mentioned") == 5


class TestCalculateMatch:
    def test_perfect_match(self):
        job = {
            "title": "Machine Learning Engineer",
            "location": "Remote",
            "description": "Python, machine learning, deep learning, AWS, Docker, Kubernetes",
        }
        score, skills, roles, locations, negatives = calculate_match(job)
        assert score >= 80
        assert "machine learning engineer" in roles
        assert "remote" in locations
        assert "python" in skills
        assert "machine learning" in skills

    def test_location_match_bengaluru(self):
        job = {
            "title": "Software Engineer",
            "location": "Bengaluru, Karnataka",
            "description": "Python, Java",
        }
        score, _, _, locations, _ = calculate_match(job)
        assert "bengaluru" in locations or "bangalore" in locations
        assert score >= 20

    def test_negative_terms_intern(self):
        job = {
            "title": "ML Intern",
            "location": "Remote",
            "description": "Python, machine learning",
        }
        score, _, _, _, negatives = calculate_match(job)
        assert "intern" in negatives
        assert score < 50

    def test_negative_terms_experience(self):
        job = {
            "title": "Senior ML Engineer",
            "location": "Remote",
            "description": "10+ years experience, Python, machine learning",
        }
        score, _, _, _, negatives = calculate_match(job)
        assert any("10+" in n for n in negatives)
        assert score < 50

    def test_skill_scoring(self):
        job = {
            "title": "AI Engineer",
            "location": "Remote",
            "description": "Python, TensorFlow, PyTorch, LangChain, RAG, LLM, AWS, Docker",
        }
        score, skills, _, _, _ = calculate_match(job)
        assert len(skills) >= 5
        assert score >= 70

    def test_role_bonus_exact_match(self):
        job = {"title": "AI/ML Engineer", "location": "Remote", "description": "Python"}
        score, _, roles, _, _ = calculate_match(job)
        assert "ai/ml engineer" in roles
        assert score >= 40

    def test_score_capped_at_100(self):
        job = {
            "title": "Machine Learning Engineer",
            "location": "Remote",
            "description": "Python machine learning deep learning generative ai llm rag langchain fastapi aws docker kubernetes sql tensorflow pytorch transformers hugging face vector database qdrant faiss pinecone pgvector mlflow onnx ocr",
        }
        score, _, _, _, _ = calculate_match(job)
        assert score <= 100

    def test_score_floor_at_0(self):
        job = {
            "title": "Intern",
            "location": "Office",
            "description": "10+ years experience required",
        }
        score, _, _, _, _ = calculate_match(job)
        assert score >= 0


class TestMatchJob:
    def test_match_job_returns_dict_with_score(self):
        job = {
            "title": "ML Engineer",
            "location": "Remote",
            "description": "Python, machine learning",
        }
        result = match_job(job)
        assert "match_score" in result
        assert "matched_skills" in result
        assert "matched_roles" in result
        assert "matched_locations" in result
        assert "negative_terms" in result
        assert isinstance(result["match_score"], int)

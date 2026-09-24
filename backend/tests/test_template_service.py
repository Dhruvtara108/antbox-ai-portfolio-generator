import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parents[1]))

from app.models.candidate import CandidateProfile, Education, Experience, Project, Skill
from app.services.template_service import render_template


def test_render_template_uses_candidate_profile_data():
    profile = CandidateProfile(
        name="Test Candidate",
        role="Platform Engineer",
        summary="Builds reliable services.",
        experience=[
            Experience(
                title="Engineer",
                company="Example Co",
                dates="2024",
                description="Improved service reliability.",
                evidence=["Python"],
            )
        ],
        projects=[
            Project(
                name="Example System",
                description="A data workflow.",
                technologies=["FastAPI", "SQL"],
            )
        ],
        skills=[Skill(name="Python", evidence=["Resume"])],
        education=[Education(institution="Example University", qualification="BSc")],
    )

    html = render_template(profile)

    assert "Test Candidate" in html
    assert "Example Co" in html
    assert "Example System" in html
    assert "Example University" in html
    assert "hero-grid" in html
    assert "exp-card" in html
    assert "system-flow" in html
    assert "capability-band" in html
    assert "style-grid" in html

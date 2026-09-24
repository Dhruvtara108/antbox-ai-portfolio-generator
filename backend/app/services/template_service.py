from pathlib import Path

from jinja2 import Environment, FileSystemLoader, select_autoescape

from app.models.candidate import CandidateProfile


TEMPLATE_PATH = Path(__file__).resolve().parents[3] / "template.html"
_TEMPLATE_ENVIRONMENT = Environment(
    loader=FileSystemLoader(TEMPLATE_PATH.parent),
    autoescape=select_autoescape(["html", "xml"]),
)


def load_template() -> str:
    """Load the approved presentation template without asking the model for HTML."""
    try:
        return TEMPLATE_PATH.read_text(encoding="utf-8")
    except OSError as exc:
        raise RuntimeError("The approved portfolio template could not be loaded.") from exc


def render_template(profile: CandidateProfile) -> str:
    """Render the approved template with validated candidate data."""
    try:
        template = _TEMPLATE_ENVIRONMENT.get_template(TEMPLATE_PATH.name)
        return template.render(profile=profile)
    except OSError as exc:
        raise RuntimeError("The approved portfolio template could not be loaded.") from exc

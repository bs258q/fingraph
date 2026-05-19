import json
from pathlib import Path
from jinja2 import Environment, FileSystemLoader
from fingraph_eval.runner import ReportData

TEMPLATES_DIR = Path(__file__).parent / "templates"


class Reporter:
    def __init__(self, data: ReportData):
        self._data = data

    def save_json(self, path: str) -> None:
        with open(path, "w") as f:
            json.dump(self._data.model_dump(), f, indent=2, default=str)

    def save_html(self, path: str) -> None:
        env = Environment(loader=FileSystemLoader(str(TEMPLATES_DIR)))
        template = env.get_template("report.html.j2")
        html = template.render(
            agent_type=self._data.agent_type,
            aggregate=self._data.aggregate,
            case_results=self._data.case_results,
            pass_pct=f"{self._data.aggregate['pass_rate'] * 100:.1f}%",
        )
        with open(path, "w") as f:
            f.write(html)

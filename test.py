from app.core.context import AuditContext
from app.agents.provenance_agent import ProvenanceAgent

class AuditPipeline:
    def __init__(self) -> None:
        self.provenance_agent = ProvenanceAgent()

    def run_provenance(self, skill_path: str, previous_skill_path: str = None) -> dict:
        context = AuditContext(
            skill_path=skill_path,
            previous_skill_path=previous_skill_path,
        )
        self.provenance_agent.run(context)
        return context.to_dict()

if __name__ == "__main__":
    pipeline = AuditPipeline()
    result = pipeline.run_provenance(skill_path="C:\\Users\\speed\\Desktop\\self-improving-agent-3.0.10")
    print(result)

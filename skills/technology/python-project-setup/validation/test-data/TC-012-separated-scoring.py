# TC-012: Separation of Technology Guidance from Engineering Scoring Fixture
# Technology skill provides setup context & evidence; Engineering skill handles score/deductions

class TechnologySkillReviewContract:
    def provide_setup_context(self, project_evidence: dict) -> dict:
        # Tech skill returns technical setup observation without calculating custom numeric scores
        return {
            "technology": "Python/ConnectRPC",
            "evidence": project_evidence.get("observation"),
            "delegate_to_engineering_skill": "skill-eng-modularity"
        }


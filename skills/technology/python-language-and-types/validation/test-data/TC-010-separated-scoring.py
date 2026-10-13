# TC-010: Technology Guidance vs Engineering Scoring Separation Fixture

class TypeSystemSkillReviewContract:
    def provide_type_context(self, type_diagnostics: list[str]) -> dict:
        return {
            "technology": "Python/Types",
            "type_issues_found": len(type_diagnostics),
            "delegate_to_engineering_skill": "skill-eng-maintainability"
        }


# TC-007: Module Granularity and God Objects

# VIOLATION: Massive God object containing endless state, database calls, email logic, and report generation
class SystemGodObjectViolation:
    def __init__(self):
        self.db = "db_conn"
        self.smtp = "smtp_conn"
        self.cache = "redis_conn"
        self.logs = []

    def handle_everything(self, action, payload):
        if action == "create_user":
            self.logs.append("creating user")
            # 100 lines of user creation
        elif action == "charge_card":
            self.logs.append("charging card")
            # 100 lines of billing
        elif action == "generate_pdf_report":
            self.logs.append("generating report")
            # 100 lines of pdf rendering


# SAFE: Decomposed into specialized collaborating services
class UserService:
    def create_user(self, payload):
        print("Creating user")

class BillingService:
    def charge_card(self, payload):
        print("Charging card")

class ReportService:
    def generate_pdf_report(self, payload):
        print("Generating PDF report")


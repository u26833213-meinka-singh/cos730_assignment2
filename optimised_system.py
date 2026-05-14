"""
COS 730 Assignment 2
Task 5: Optimised Implementation

This implementation refactors the baseline system by:
- Introducing SubmissionService as the main workflow coordinator
- Reducing the responsibilities of SubmissionController
- Encapsulating reviewer selection inside ReviewerAssignmentService
- Centralising outcome logic inside DecisionService
- Simplifying notification handling
- Preserving functional equivalence with the baseline system

Author: u26833213 - Meinka Singh
"""


class InteractionLogger:
    """
    Counts and displays method calls/interactions.
    This is useful for Task 6 empirical comparison.
    """

    def __init__(self):
        self.calls = []

    def log(self, sender, receiver, message):
        interaction = f"{sender} -> {receiver}: {message}"
        self.calls.append(interaction)
        print(interaction)

    def count(self):
        return len(self.calls)

    def display_summary(self):
        print("\n--- Interaction Summary ---")
        for call in self.calls:
            print(call)
        print(f"\nTotal method calls/interactions: {self.count()}")


class UI:
    """
    Handles researcher interaction.
    The UI only forwards the submission request to the controller.
    """

    def __init__(self, submission_controller, logger):
        self.submission_controller = submission_controller
        self.logger = logger

    def submit_research_output(self, data):
        self.logger.log("Researcher", "UI", "submitResearchOutput(data)")

        self.logger.log("UI", "SubmissionController", "submit(data)")
        result = self.submission_controller.submit(data)

        self.logger.log("UI", "Researcher", "displayResult(result)")
        return result


class SubmissionController:
    """
    Optimised controller.
    It only receives the request and delegates the workflow to SubmissionService.
    """

    def __init__(self, submission_service, logger):
        self.submission_service = submission_service
        self.logger = logger

    def submit(self, data):
        self.logger.log(
            "SubmissionController",
            "SubmissionService",
            "processSubmission(data)"
        )

        return self.submission_service.process_submission(data)


class SubmissionService:
    """
    Main workflow coordinator.

    This class coordinates the submission process but delegates specialised
    responsibilities to focused components.
    """

    def __init__(
        self,
        validator,
        submission_repository,
        reviewer_assignment_service,
        evaluation_service,
        decision_service,
        notification_service,
        logger
    ):
        self.validator = validator
        self.submission_repository = submission_repository
        self.reviewer_assignment_service = reviewer_assignment_service
        self.evaluation_service = evaluation_service
        self.decision_service = decision_service
        self.notification_service = notification_service
        self.logger = logger

    def process_submission(self, data):
        # Step 1: Validate submission
        self.logger.log("SubmissionService", "Validator", "validate(data)")
        is_valid = self.validator.validate(data)

        if not is_valid:
            self.logger.log(
                "SubmissionService",
                "DecisionService",
                "determineOutcome(invalid)"
            )

            outcome = self.decision_service.determine_outcome(
                valid_format=False,
                reviewers_available=False,
                average_score=None,
                consensus=None
            )

            self.logger.log(
                "SubmissionService",
                "NotificationService",
                "sendOutcomeNotification(error)"
            )
            self.notification_service.send_outcome_notification(outcome, data)

            return {
                "status": "error",
                "outcome": outcome,
                "message": "Submission format is invalid."
            }

        # Step 2: Save valid submission
        self.logger.log(
            "SubmissionService",
            "SubmissionRepository",
            "save(data)"
        )
        confirmation = self.submission_repository.save(data)

        self.logger.log(
            "SubmissionRepository",
            "SubmissionService",
            "confirmation"
        )

        # Step 3: Assign eligible reviewers
        self.logger.log(
            "SubmissionService",
            "ReviewerAssignmentService",
            "assignEligibleReviewers(data)"
        )
        reviewers = self.reviewer_assignment_service.assign_eligible_reviewers(data)

        if not reviewers:
            self.logger.log(
                "SubmissionService",
                "DecisionService",
                "determineOutcome(noReviewers)"
            )

            outcome = self.decision_service.determine_outcome(
                valid_format=True,
                reviewers_available=False,
                average_score=None,
                consensus=None
            )

            self.logger.log(
                "SubmissionService",
                "NotificationService",
                "sendOutcomeNotification(manual_assignment_required)"
            )
            self.notification_service.send_outcome_notification(outcome, data)

            return {
                "status": "pending",
                "database_confirmation": confirmation,
                "outcome": outcome,
                "message": "No eligible reviewers available. Manual assignment required."
            }

        # Step 4: Evaluate submission
        self.logger.log(
            "SubmissionService",
            "EvaluationService",
            "evaluateSubmission(data, reviewers)"
        )

        evaluation_result = self.evaluation_service.evaluate_submission(data, reviewers)

        # Step 5: Determine final outcome using decision table logic
        self.logger.log(
            "SubmissionService",
            "DecisionService",
            "determineOutcome(average, consensus)"
        )

        outcome = self.decision_service.determine_outcome(
            valid_format=True,
            reviewers_available=True,
            average_score=evaluation_result["average_score"],
            consensus=evaluation_result["consensus"]
        )

        # Step 6: Notify researcher
        self.logger.log(
            "SubmissionService",
            "NotificationService",
            "sendOutcomeNotification(outcome)"
        )
        self.notification_service.send_outcome_notification(outcome, data)

        return {
            "status": "completed",
            "database_confirmation": confirmation,
            "average_score": evaluation_result["average_score"],
            "consensus": evaluation_result["consensus"],
            "outcome": outcome
        }


class Validator:
    """
    Validates the submitted artefact.
    """

    def __init__(self, logger):
        self.logger = logger

    def validate(self, data):
        self.logger.log("Validator", "Validator", "checkRequiredFields()")
        required_fields = ["title", "author", "file_type", "content"]

        for field in required_fields:
            if field not in data or data[field] == "":
                return False

        self.logger.log("Validator", "Validator", "checkAcceptedFileType()")
        if data["file_type"] not in ["pdf", "docx", "txt"]:
            return False

        return True


class SubmissionRepository:
    """
    Stores valid submissions.
    This replaces the generic Database object with a more focused repository.
    """

    def __init__(self, logger):
        self.submissions = []
        self.logger = logger

    def save(self, data):
        self.submissions.append(data)
        return "Submission saved successfully."


class ReviewerAssignmentService:
    """
    Handles reviewer selection and assignment.

    In the baseline system, reviewer selection was exposed as several separate
    interactions. In the optimised system, conflict checking and workload checking
    are encapsulated inside select_eligible_reviewers().
    """

    def __init__(self, reviewers, logger):
        self.reviewers = reviewers
        self.logger = logger

    def assign_eligible_reviewers(self, data):
        self.logger.log(
            "ReviewerAssignmentService",
            "ReviewerAssignmentService",
            "selectEligibleReviewers(data)"
        )

        eligible_reviewers = self.select_eligible_reviewers(data)

        for reviewer in eligible_reviewers:
            self.logger.log(
                "ReviewerAssignmentService",
                "Reviewer",
                f"assignReview({reviewer.name})"
            )
            reviewer.assign_review(data)

        self.logger.log(
            "ReviewerAssignmentService",
            "SubmissionService",
            "reviewers"
        )

        return eligible_reviewers

    def select_eligible_reviewers(self, data):
        eligible_reviewers = []

        for reviewer in self.reviewers:
            if not reviewer.has_conflict and reviewer.current_workload < reviewer.max_workload:
                eligible_reviewers.append(reviewer)

        return eligible_reviewers


class Reviewer:
    """
    Reviewer entity.
    """

    def __init__(self, name, score, has_conflict=False, current_workload=0, max_workload=3):
        self.name = name
        self.score = score
        self.has_conflict = has_conflict
        self.current_workload = current_workload
        self.max_workload = max_workload
        self.assigned_submission = None

    def assign_review(self, data):
        self.assigned_submission = data
        self.current_workload += 1

    def submit_score(self):
        return self.score


class EvaluationService:
    """
    Handles evaluation calculations.

    This class calculates the average score and checks consensus, but it does not
    decide the final outcome. The final decision is delegated to DecisionService.
    """

    def __init__(self, logger):
        self.logger = logger

    def evaluate_submission(self, data, reviewers):
        scores = []

        for reviewer in reviewers:
            self.logger.log(
                "EvaluationService",
                "Reviewer",
                f"requestScore({reviewer.name})"
            )

            score = reviewer.submit_score()

            self.logger.log(
                "Reviewer",
                "EvaluationService",
                f"submitScore({score})"
            )

            scores.append(score)

        self.logger.log(
            "EvaluationService",
            "EvaluationService",
            "calculateAverage()"
        )
        average_score = self.calculate_average(scores)

        self.logger.log(
            "EvaluationService",
            "EvaluationService",
            "checkConsensus()"
        )
        consensus = self.check_consensus(scores)

        return {
            "scores": scores,
            "average_score": average_score,
            "consensus": consensus
        }

    def calculate_average(self, scores):
        if not scores:
            return 0

        return sum(scores) / len(scores)

    def check_consensus(self, scores):
        if not scores:
            return False

        highest = max(scores)
        lowest = min(scores)

        # Same rule used in baseline:
        # consensus exists if scores differ by no more than 20.
        return highest - lowest <= 20


class DecisionService:
    """
    Centralised decision logic based on the decision table from Task 3.
    """

    def determine_outcome(
        self,
        valid_format,
        reviewers_available,
        average_score,
        consensus
    ):
        # R1: Invalid submission
        if not valid_format:
            return "error"

        # R2: Valid submission but no reviewers available
        if not reviewers_available:
            return "manual_assignment_required"

        # R3: Average >= 70 and consensus exists
        if average_score >= 70 and consensus:
            return "accepted"

        # R4: Average >= 70 but no consensus
        if average_score >= 70 and not consensus:
            return "revision"

        # R5: Average below 50
        if average_score < 50:
            return "rejected"

        # R6: Average between 50 and 69
        return "revision"


class NotificationService:
    """
    Sends notifications to the researcher.
    The optimised version uses one unified method.
    """

    def __init__(self, logger):
        self.logger = logger

    def send_outcome_notification(self, outcome, data):
        messages = {
            "error": "Notification: Your submission format is invalid.",
            "manual_assignment_required": "Notification: Your submission is saved, but manual reviewer assignment is required.",
            "accepted": "Notification: Your submission has been accepted.",
            "rejected": "Notification: Your submission has been rejected.",
            "revision": "Notification: Your submission requires revision."
        }

        message = messages.get(outcome, "Notification: Unknown outcome.")

        print(f"\n{message}")

        self.logger.log(
            "NotificationService",
            "Researcher",
            f"sendNotification({outcome})"
        )


def run_valid_acceptance_case():
    """
    Test case:
    Valid submission + eligible reviewers + high scores + consensus = accepted.
    """

    print("\n==============================")
    print("TEST CASE 1: ACCEPTED")
    print("==============================")

    logger = InteractionLogger()

    reviewers = [
        Reviewer(name="Reviewer A", score=80, has_conflict=False, current_workload=1),
        Reviewer(name="Reviewer B", score=75, has_conflict=False, current_workload=2),
        Reviewer(name="Reviewer C", score=78, has_conflict=False, current_workload=0),
    ]

    system = build_system(reviewers, logger)

    submission_data = {
        "title": "Sentiment Analysis of University Reviews",
        "author": "Student Researcher",
        "file_type": "pdf",
        "content": "This is the research artefact content."
    }

    result = system.submit_research_output(submission_data)

    print("\n--- Final Result ---")
    print(result)

    logger.display_summary()


def run_invalid_submission_case():
    """
    Test case:
    Invalid file type = error.
    """

    print("\n==============================")
    print("TEST CASE 2: INVALID SUBMISSION")
    print("==============================")

    logger = InteractionLogger()

    reviewers = [
        Reviewer(name="Reviewer A", score=80),
        Reviewer(name="Reviewer B", score=75),
    ]

    system = build_system(reviewers, logger)

    submission_data = {
        "title": "Invalid Submission",
        "author": "Student Researcher",
        "file_type": "exe",
        "content": "This should fail validation."
    }

    result = system.submit_research_output(submission_data)

    print("\n--- Final Result ---")
    print(result)

    logger.display_summary()


def run_revision_case():
    """
    Test case:
    Valid submission + average between 50 and 69 = revision.
    """

    print("\n==============================")
    print("TEST CASE 3: REVISION")
    print("==============================")

    logger = InteractionLogger()

    reviewers = [
        Reviewer(name="Reviewer A", score=60),
        Reviewer(name="Reviewer B", score=65),
        Reviewer(name="Reviewer C", score=62),
    ]

    system = build_system(reviewers, logger)

    submission_data = {
        "title": "Needs Improvement",
        "author": "Student Researcher",
        "file_type": "pdf",
        "content": "This submission is acceptable but needs revision."
    }

    result = system.submit_research_output(submission_data)

    print("\n--- Final Result ---")
    print(result)

    logger.display_summary()


def run_rejection_case():
    """
    Test case:
    Valid submission + average below 50 = rejected.
    """

    print("\n==============================")
    print("TEST CASE 4: REJECTED")
    print("==============================")

    logger = InteractionLogger()

    reviewers = [
        Reviewer(name="Reviewer A", score=40),
        Reviewer(name="Reviewer B", score=45),
        Reviewer(name="Reviewer C", score=42),
    ]

    system = build_system(reviewers, logger)

    submission_data = {
        "title": "Poor Submission",
        "author": "Student Researcher",
        "file_type": "pdf",
        "content": "This submission does not meet the minimum standard."
    }

    result = system.submit_research_output(submission_data)

    print("\n--- Final Result ---")
    print(result)

    logger.display_summary()


def run_no_reviewers_case():
    """
    Test case:
    Valid submission but all reviewers are either conflicted or overloaded.
    """

    print("\n==============================")
    print("TEST CASE 5: NO ELIGIBLE REVIEWERS")
    print("==============================")

    logger = InteractionLogger()

    reviewers = [
        Reviewer(name="Reviewer A", score=80, has_conflict=True),
        Reviewer(name="Reviewer B", score=75, current_workload=3, max_workload=3),
        Reviewer(name="Reviewer C", score=78, has_conflict=True),
    ]

    system = build_system(reviewers, logger)

    submission_data = {
        "title": "Valid But No Reviewers",
        "author": "Student Researcher",
        "file_type": "pdf",
        "content": "This submission is valid but cannot be automatically assigned."
    }

    result = system.submit_research_output(submission_data)

    print("\n--- Final Result ---")
    print(result)

    logger.display_summary()


def build_system(reviewers, logger):
    """
    Factory function to assemble the optimised system.
    """

    validator = Validator(logger)
    submission_repository = SubmissionRepository(logger)
    reviewer_assignment_service = ReviewerAssignmentService(reviewers, logger)
    evaluation_service = EvaluationService(logger)
    decision_service = DecisionService()
    notification_service = NotificationService(logger)

    submission_service = SubmissionService(
        validator=validator,
        submission_repository=submission_repository,
        reviewer_assignment_service=reviewer_assignment_service,
        evaluation_service=evaluation_service,
        decision_service=decision_service,
        notification_service=notification_service,
        logger=logger
    )

    submission_controller = SubmissionController(
        submission_service=submission_service,
        logger=logger
    )

    ui = UI(
        submission_controller=submission_controller,
        logger=logger
    )

    return ui


def main():
    run_valid_acceptance_case()
    run_invalid_submission_case()
    run_revision_case()
    run_rejection_case()
    run_no_reviewers_case()


if __name__ == "__main__":
    main()
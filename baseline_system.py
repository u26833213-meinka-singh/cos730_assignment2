"""
COS 730 Assignment 2
Task 1: Baseline Implementation

This implementation intentionally follows the provided baseline sequence diagram.
No optimisation has been introduced at this stage.

Author: u26833213 - Meinka Singh

"""


class InteractionLogger:
    """
    Utility class used to count and display interactions.
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
    Represents the UI lifeline in the sequence diagram.
    The researcher submits the artefact through this class.
    """

    def __init__(self, submission_controller, logger):
        self.submission_controller = submission_controller
        self.logger = logger

    def submit_research_output(self, data):
        # Corresponds to: Researcher -> UI: submitResearchOutput(data)
        self.logger.log("Researcher", "UI", "submitResearchOutput(data)")

        # Corresponds to: UI -> SubmissionController: submit(data)
        self.logger.log("UI", "SubmissionController", "submit(data)")
        return self.submission_controller.submit(data)


class SubmissionController:
    """
    Coordinates the overall submission process.
    In the baseline version, this class intentionally controls many interactions.
    """

    def __init__(
        self,
        validator,
        database,
        reviewer_manager,
        evaluation_manager,
        notification_service,
        logger
    ):
        self.validator = validator
        self.database = database
        self.reviewer_manager = reviewer_manager
        self.evaluation_manager = evaluation_manager
        self.notification_service = notification_service
        self.logger = logger

    def submit(self, data):
        # Corresponds to: SubmissionController -> Validator: validateFormat(data)
        self.logger.log("SubmissionController", "Validator", "validateFormat(data)")
        is_valid = self.validator.validate_format(data)

        # Corresponds to alt [invalid]
        if not is_valid:
            # Corresponds to: Validator -> SubmissionController: return error
            self.logger.log("Validator", "SubmissionController", "return error")
            return {
                "status": "error",
                "message": "Submission format is invalid."
            }

        # Corresponds to alt [valid]

        # Corresponds to: SubmissionController -> Database: saveSubmission(data)
        self.logger.log("SubmissionController", "Database", "saveSubmission(data)")
        confirmation = self.database.save_submission(data)

        # Corresponds to: Database -> SubmissionController: confirmation
        self.logger.log("Database", "SubmissionController", "confirmation")

        # Corresponds to: SubmissionController -> ReviewerManager: getAvailableReviewers()
        self.logger.log(
            "SubmissionController",
            "ReviewerManager",
            "getAvailableReviewers()"
        )
        reviewers = self.reviewer_manager.get_available_reviewers()

        # Corresponds to loop [assign reviewer]
        for reviewer in reviewers:
            self.logger.log(
                "SubmissionController",
                "Reviewer",
                f"assignReview({reviewer.name})"
            )
            reviewer.assign_review(data)

        # Corresponds to: SubmissionController -> EvaluationManager: startEvaluation()
        self.logger.log(
            "SubmissionController",
            "EvaluationManager",
            "startEvaluation()"
        )
        outcome = self.evaluation_manager.start_evaluation(reviewers)

        # Corresponds to alt [accepted/rejected/revision]
        if outcome == "accepted":
            self.logger.log(
                "EvaluationManager",
                "NotificationService",
                "notifyAcceptance()"
            )
            self.notification_service.notify_acceptance(data)

        elif outcome == "rejected":
            self.logger.log(
                "EvaluationManager",
                "NotificationService",
                "notifyRejection()"
            )
            self.notification_service.notify_rejection(data)

        else:
            self.logger.log(
                "EvaluationManager",
                "NotificationService",
                "notifyRevision()"
            )
            self.notification_service.notify_revision(data)

        # Corresponds to final notification being sent to researcher
        self.logger.log(
            "NotificationService",
            "Researcher",
            "sendNotification()"
        )

        return {
            "status": "completed",
            "database_confirmation": confirmation,
            "outcome": outcome
        }


class Validator:
    """
    Represents the Validator lifeline.
    It checks whether the submitted artefact has the required fields.
    """

    def __init__(self, logger):
        self.logger = logger

    def validate_format(self, data):
        # Corresponds to internal validation logic in Validator
        self.logger.log("Validator", "Validator", "validateFormatRules()")

        required_fields = ["title", "author", "file_type", "content"]

        for field in required_fields:
            if field not in data or data[field] == "":
                return False

        if data["file_type"] not in ["pdf", "docx", "txt"]:
            return False

        return True


class Database:
    """
    Represents the Database lifeline.
    Stores the submission.
    """

    def __init__(self, logger):
        self.submissions = []
        self.logger = logger

    def save_submission(self, data):
        self.submissions.append(data)
        return "Submission saved successfully."


class ReviewerManager:
    """
    Represents the ReviewerManager lifeline.
    The baseline includes multiple internal calls.
    """

    def __init__(self, reviewers, logger):
        self.reviewers = reviewers
        self.logger = logger

    def get_available_reviewers(self):
        # Corresponds to: ReviewerManager -> ReviewerManager: fetchReviewers()
        self.logger.log("ReviewerManager", "ReviewerManager", "fetchReviewers()")
        reviewer_list = self.fetch_reviewers()

        # Corresponds to: ReviewerManager -> ReviewerManager: startConflictReviewList()
        self.logger.log(
            "ReviewerManager",
            "ReviewerManager",
            "startConflictReviewList()"
        )
        no_conflict_reviewers = self.start_conflict_review_list(reviewer_list)

        # Corresponds to: ReviewerManager -> ReviewerManager: checkWorkloadReviewers()
        self.logger.log(
            "ReviewerManager",
            "ReviewerManager",
            "checkWorkloadReviewers()"
        )
        available_reviewers = self.check_workload_reviewers(no_conflict_reviewers)

        # Corresponds to: ReviewerManager -> SubmissionController: sharedReviewers
        self.logger.log(
            "ReviewerManager",
            "SubmissionController",
            "sharedReviewers"
        )

        return available_reviewers

    def fetch_reviewers(self):
        return self.reviewers

    def start_conflict_review_list(self, reviewer_list):
        return [reviewer for reviewer in reviewer_list if not reviewer.has_conflict]

    def check_workload_reviewers(self, reviewer_list):
        return [reviewer for reviewer in reviewer_list if reviewer.current_workload < reviewer.max_workload]


class Reviewer:
    """
    Represents a Reviewer lifeline.
    Each reviewer receives a review assignment and later submits a score.
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


class EvaluationManager:
    """
    Represents the EvaluationManager lifeline.

    It collects reviewer scores, calculates an average,
    checks consensus, applies decision rules, and returns a final outcome.
    """

    def __init__(self, logger):
        self.logger = logger
        self.final_scores = []

    def start_evaluation(self, reviewers):
        self.final_scores = []

        # Corresponds to loop [each reviewer]
        for reviewer in reviewers:
            self.logger.log(
                "EvaluationManager",
                "Reviewer",
                f"submitScore({reviewer.name})"
            )

            score = reviewer.submit_score()

            self.logger.log(
                "Reviewer",
                "EvaluationManager",
                f"saveFinalScore({score})"
            )

            self.final_scores.append(score)

        # Corresponds to: EvaluationManager -> EvaluationManager: calculateAverage()
        self.logger.log(
            "EvaluationManager",
            "EvaluationManager",
            "calculateAverage()"
        )
        average = self.calculate_average()

        # Corresponds to: EvaluationManager -> EvaluationManager: checkConsensus()
        self.logger.log(
            "EvaluationManager",
            "EvaluationManager",
            "checkConsensus()"
        )
        consensus = self.check_consensus()

        # Corresponds to: EvaluationManager -> EvaluationManager: applyRules()
        self.logger.log(
            "EvaluationManager",
            "EvaluationManager",
            "applyRules()"
        )
        outcome = self.apply_rules(average, consensus)

        return outcome

    def calculate_average(self):
        if not self.final_scores:
            return 0

        return sum(self.final_scores) / len(self.final_scores)

    def check_consensus(self):
        if not self.final_scores:
            return False

        highest = max(self.final_scores)
        lowest = min(self.final_scores)

        # Arbitrary baseline consensus rule:
        # consensus exists if scores are within 20 marks of each other.
        return highest - lowest <= 20

    def apply_rules(self, average, consensus):
        if average >= 70 and consensus:
            return "accepted"

        elif average < 50:
            return "rejected"

        else:
            return "revision"


class NotificationService:
    """
    Represents the NotificationService lifeline.
    Sends the final outcome notification.
    """

    def __init__(self, logger):
        self.logger = logger

    def notify_acceptance(self, data):
        print("\nNotification: Your submission has been accepted.")

    def notify_rejection(self, data):
        print("\nNotification: Your submission has been rejected.")

    def notify_revision(self, data):
        print("\nNotification: Your submission requires revision.")


def main():
    logger = InteractionLogger()

    # Create reviewers
    reviewers = [
        Reviewer(name="Reviewer A", score=80, has_conflict=False, current_workload=1),
        Reviewer(name="Reviewer B", score=75, has_conflict=False, current_workload=2),
        Reviewer(name="Reviewer C", score=78, has_conflict=False, current_workload=0),
    ]

    # Create system components
    validator = Validator(logger)
    database = Database(logger)
    reviewer_manager = ReviewerManager(reviewers, logger)
    evaluation_manager = EvaluationManager(logger)
    notification_service = NotificationService(logger)

    submission_controller = SubmissionController(
        validator=validator,
        database=database,
        reviewer_manager=reviewer_manager,
        evaluation_manager=evaluation_manager,
        notification_service=notification_service,
        logger=logger
    )

    ui = UI(submission_controller, logger)

    # Example valid submission
    submission_data = {
        "title": "Sentiment Analysis of University Reviews",
        "author": "Student Researcher",
        "file_type": "pdf",
        "content": "This is the research artefact content."
    }

    result = ui.submit_research_output(submission_data)

    print("\n--- Final Result ---")
    print(result)

    logger.display_summary()


if __name__ == "__main__":
    main()
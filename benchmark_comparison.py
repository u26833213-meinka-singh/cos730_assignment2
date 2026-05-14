"""
COS 730 Assignment 2
Task 6: Empirical Evaluation and Comparison

This script compares:
1. Baseline implementation
2. Optimised implementation

Metrics:
- Number of interactions
- Execution time
- Functional equivalence

Author: u26833213 - Meinka Singh
"""

import time


# -----------------------------
# Baseline import
# -----------------------------
from baseline_system import (
    InteractionLogger as BaselineLogger,
    Reviewer as BaselineReviewer,
    Validator as BaselineValidator,
    Database as BaselineDatabase,
    ReviewerManager as BaselineReviewerManager,
    EvaluationManager as BaselineEvaluationManager,
    NotificationService as BaselineNotificationService,
    SubmissionController as BaselineSubmissionController,
    UI as BaselineUI
)


# -----------------------------
# Optimised import
# -----------------------------
from optimised_system import (
    InteractionLogger as OptimisedLogger,
    Reviewer as OptimisedReviewer,
    Validator as OptimisedValidator,
    SubmissionRepository as OptimisedSubmissionRepository,
    ReviewerAssignmentService as OptimisedReviewerAssignmentService,
    EvaluationService as OptimisedEvaluationService,
    DecisionService as OptimisedDecisionService,
    NotificationService as OptimisedNotificationService,
    SubmissionService as OptimisedSubmissionService,
    SubmissionController as OptimisedSubmissionController,
    UI as OptimisedUI
)


def build_baseline_system():
    logger = BaselineLogger()

    reviewers = [
        BaselineReviewer(name="Reviewer A", score=80, has_conflict=False, current_workload=1),
        BaselineReviewer(name="Reviewer B", score=75, has_conflict=False, current_workload=2),
        BaselineReviewer(name="Reviewer C", score=78, has_conflict=False, current_workload=0),
    ]

    validator = BaselineValidator(logger)
    database = BaselineDatabase(logger)
    reviewer_manager = BaselineReviewerManager(reviewers, logger)
    evaluation_manager = BaselineEvaluationManager(logger)
    notification_service = BaselineNotificationService(logger)

    submission_controller = BaselineSubmissionController(
        validator=validator,
        database=database,
        reviewer_manager=reviewer_manager,
        evaluation_manager=evaluation_manager,
        notification_service=notification_service,
        logger=logger
    )

    ui = BaselineUI(submission_controller, logger)

    return ui, logger


def build_optimised_system():
    logger = OptimisedLogger()

    reviewers = [
        OptimisedReviewer(name="Reviewer A", score=80, has_conflict=False, current_workload=1),
        OptimisedReviewer(name="Reviewer B", score=75, has_conflict=False, current_workload=2),
        OptimisedReviewer(name="Reviewer C", score=78, has_conflict=False, current_workload=0),
    ]

    validator = OptimisedValidator(logger)
    submission_repository = OptimisedSubmissionRepository(logger)
    reviewer_assignment_service = OptimisedReviewerAssignmentService(reviewers, logger)
    evaluation_service = OptimisedEvaluationService(logger)
    decision_service = OptimisedDecisionService()
    notification_service = OptimisedNotificationService(logger)

    submission_service = OptimisedSubmissionService(
        validator=validator,
        submission_repository=submission_repository,
        reviewer_assignment_service=reviewer_assignment_service,
        evaluation_service=evaluation_service,
        decision_service=decision_service,
        notification_service=notification_service,
        logger=logger
    )

    submission_controller = OptimisedSubmissionController(
        submission_service=submission_service,
        logger=logger
    )

    ui = OptimisedUI(submission_controller, logger)

    return ui, logger


def get_submission_data():
    return {
        "title": "Sentiment Analysis of University Reviews",
        "author": "Student Researcher",
        "file_type": "pdf",
        "content": "This is the research artefact content."
    }


def run_baseline_once():
    ui, logger = build_baseline_system()
    result = ui.submit_research_output(get_submission_data())
    return result, logger.count()


def run_optimised_once():
    ui, logger = build_optimised_system()
    result = ui.submit_research_output(get_submission_data())
    return result, logger.count()


def benchmark(system_function, iterations):
    start_time = time.perf_counter()

    final_result = None
    final_interaction_count = 0

    for _ in range(iterations):
        final_result, final_interaction_count = system_function()

    end_time = time.perf_counter()

    return {
        "iterations": iterations,
        "total_time": end_time - start_time,
        "average_time": (end_time - start_time) / iterations,
        "final_result": final_result,
        "interaction_count": final_interaction_count
    }


def calculate_percentage_improvement(old_value, new_value):
    return ((old_value - new_value) / old_value) * 100


def main():
    iterations = 10000

    print("Running baseline benchmark...")
    baseline_results = benchmark(run_baseline_once, iterations)

    print("Running optimised benchmark...")
    optimised_results = benchmark(run_optimised_once, iterations)

    call_reduction = calculate_percentage_improvement(
        baseline_results["interaction_count"],
        optimised_results["interaction_count"]
    )

    time_reduction = calculate_percentage_improvement(
        baseline_results["average_time"],
        optimised_results["average_time"]
    )

    print("\n==============================")
    print("TASK 6: EMPIRICAL COMPARISON")
    print("==============================")

    print("\nBaseline Results:")
    print(f"Interactions: {baseline_results['interaction_count']}")
    print(f"Total time: {baseline_results['total_time']:.6f} seconds")
    print(f"Average time per run: {baseline_results['average_time']:.10f} seconds")
    print(f"Outcome: {baseline_results['final_result']['outcome']}")

    print("\nOptimised Results:")
    print(f"Interactions: {optimised_results['interaction_count']}")
    print(f"Total time: {optimised_results['total_time']:.6f} seconds")
    print(f"Average time per run: {optimised_results['average_time']:.10f} seconds")
    print(f"Outcome: {optimised_results['final_result']['outcome']}")

    print("\nImprovement:")
    print(f"Interaction reduction: {call_reduction:.2f}%")
    print(f"Average execution time reduction: {time_reduction:.2f}%")

    print("\nFunctional Equivalence:")
    if baseline_results["final_result"]["outcome"] == optimised_results["final_result"]["outcome"]:
        print("PASS: Both systems produced the same final outcome.")
    else:
        print("FAIL: Systems produced different outcomes.")


if __name__ == "__main__":
    main()
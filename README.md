# COS 730 Assignment 2: From Behavioural Models to Optimised Implementation

## Overview

This repository contains the implementation files for **COS 730 Assignment 2: From Behavioural Models to Optimised Implementation**.

The assignment focuses on translating a baseline behavioural model into code, identifying design inefficiencies, optimising the interaction model, and empirically comparing the baseline and optimised implementations.

The system implemented is an **Intelligent Submission and Review System**, which models the process of:

- submitting a research artefact,
- validating the submission,
- assigning reviewers,
- collecting reviewer scores,
- applying decision rules,
- producing a final outcome.

The repository contains both the baseline implementation and the optimised implementation, as well as a benchmarking script used for empirical comparison.

---

## Files Included

### `baseline_system.py`

This file contains the **baseline implementation** of the system.

It follows the original sequence diagram as closely as possible and intentionally preserves the original design structure. No optimisations are introduced in this version.

The baseline implementation includes:

- `UI`
- `SubmissionController`
- `Validator`
- `Database`
- `ReviewerManager`
- `Reviewer`
- `EvaluationManager`
- `NotificationService`
- `InteractionLogger`

The purpose of this file is to provide a faithful reference implementation of the original behavioural model.

---

### `optimised_system.py`

This file contains the **optimised implementation** of the system.

It refactors the baseline implementation to improve responsibility allocation, reduce coupling, improve cohesion, and centralise decision logic.

The optimised implementation introduces:

- `SubmissionService`
- `SubmissionRepository`
- `ReviewerAssignmentService`
- `EvaluationService`
- `DecisionService`

The optimised system preserves the same functional outcomes as the baseline system, including:

- accepted submissions,
- rejected submissions,
- revision outcomes,
- invalid submission handling,
- no eligible reviewer handling.

---

### `benchmark_comparison.py`

This file compares the baseline and optimised implementations.

It evaluates both systems using:

- number of interactions/method calls,
- execution time over repeated runs,
- final outcome comparison,
- functional equivalence.

The benchmarking script is used for the empirical evaluation section of the assignment.

---

## Requirements

The project is implemented in **Python** and does not require any external libraries.

Recommended Python version:

```bash
Python 3.9 or later

# Eideaforge – Database Architecture & Design

## 1. Schema Overview
The relational design is built on InnoDB with UTF-8mb4 character set support, indexing on critical search fields and cascading constraints on foreign relationships.

## 2. Entity Relationship Summary

```
users (1) ──── (1) student_profiles
users (1) ──── (1) evaluator_profiles
users (1) ──── (N) ideas
users (1) ──── (N) teams (as leader)
teams (1) ──── (N) team_members ──── (N) users
teams (1) ──── (N) join_requests ──── (N) users

competitions (1) ──── (N) competition_rounds
competition_rounds (1) ──── (N) evaluation_criteria
competitions (1) ──── (N) competition_evaluators ──── (N) users
competitions (1) ──── (N) competition_registrations ──── (N) teams

teams (1) ──── (N) submissions ──── (1) competition_rounds
submissions (1) ──── (N) evaluations ──── (1) evaluation_criteria
users (1) ──── (N) evaluations (as evaluator)
```

## 3. Data Integrity & Security Considerations
- Role constraints strictly maintained in `users` (`admin`, `student`, `evaluator`).
- Submissions require foreign key links to both `competition_id` and specific `round_id`.
- Scores per criterion per evaluator are enforced via UNIQUE composite key: `uq_sub_eval_crit (submission_id, evaluator_id, criteria_id)`.

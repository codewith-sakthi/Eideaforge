# Eideaforge – Requirements Specification

## 1. Executive Summary
Eideaforge is a campus innovation and competition platform enabling students to submit innovative ideas, form collaborative teams, enter multi-stage competitions, and undergo structured rubric evaluations by faculty and expert evaluators.

## 2. User Roles & Capabilities

### 2.1 Student
- Maintain profile (bio, department, skills, portfolio links).
- Ideation: Create, draft, and submit innovation ideas.
- Teams: Form teams around ideas, invite peers, approve/reject join requests.
- Competitions: Browse active competitions, register team, submit multi-round materials (pitch deck, git prototype link, demo video).
- Results: View round-by-round evaluations, scoring breakdowns, and leaderboards.

### 2.2 Evaluator
- View assigned competitions and assigned rounds.
- Access student submissions and linked artifacts.
- Score against customizable rubric criteria with weights and qualitative feedback.
- Track pending vs completed evaluations.

### 2.3 Administrator
- Student management: View list, view profiles, bulk upload via CSV with automated password generation.
- Idea curation: Approve, reject, or request revisions on submitted ideas.
- Competition lifecycle: Create competitions, schedule rounds, configure multi-criteria evaluation rubrics, assign evaluators.
- Submission oversight & final leaderboard publishing.

## 3. Non-Functional Requirements
- **Security**: JWT-based token authentication, bcrypt/scrypt password hashing, role-based middleware guards.
- **Reliability**: Relational foreign keys with CASCADE constraints for referential integrity.
- **Responsiveness**: Vanilla modern CSS with glassmorphism, responsive grid layouts, mobile-friendly navigation.

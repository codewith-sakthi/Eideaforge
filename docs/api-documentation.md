# Eideaforge REST API Documentation

Base URL: `/api`

All protected routes require standard Header: `Authorization: Bearer <JWT_TOKEN>`

## 1. Authentication (`/api/auth`)
- `POST /api/auth/login` – Authenticate with `{ email, password }`. Returns `{ success, data: { token, user } }`.
- `POST /api/auth/change-password` – `{ old_password, new_password }`.
- `GET /api/auth/me` – Current authenticated user payload.

## 2. Public (`/api/public`)
- `GET /api/public/competitions` – List upcoming/ongoing competitions.
- `GET /api/public/competitions/<id>` – Competition details with rounds and criteria.
- `GET /api/public/stats` – Platform summary counts for landing page.

## 3. Student (`/api/student`)
- `GET /api/student/dashboard` – Aggregate summary for student home.
- `GET /api/student/profile` – Current student's profile.
- `PUT /api/student/profile` – Update bio, skills, socials.
- `GET /api/student/submissions` – All submissions made by student's teams.

## 4. Ideas (`/api/ideas`)
- `GET /api/ideas?scope=mine` – Student's ideas.
- `GET /api/ideas` – Approved public ideas / all ideas for admin.
- `POST /api/ideas` – Create new idea.
- `GET /api/ideas/<id>` – Retrieve idea detail.
- `PUT /api/ideas/<id>` – Update idea.
- `PATCH /api/ideas/<id>/status` – Admin approve/reject.

## 5. Teams (`/api/teams`)
- `GET /api/teams` – List all teams or user's teams.
- `POST /api/teams` – Create a new team with an idea.
- `GET /api/teams/<id>` – Get team details and roster.
- `POST /api/teams/<id>/join` – Send request to join team.
- `GET /api/teams/join-requests` – List received or sent requests.
- `POST /api/teams/join-requests/<id>/action` – Accept or reject join request.

## 6. Competitions (`/api/competitions`)
- `GET /api/competitions` – List competitions.
- `POST /api/competitions` – Admin create competition.
- `PUT /api/competitions/<id>` – Admin edit competition.
- `POST /api/competitions/<id>/register` – Register student team.
- `POST /api/competitions/<id>/evaluators` – Assign evaluator.
- `POST /api/competitions/rounds/<round_id>/criteria` – Add evaluation criterion.

## 7. Submissions (`/api/submissions`)
- `GET /api/submissions` – List submissions (filtered by role/comp).
- `POST /api/submissions` – Upload submission (multipart form: pitch_deck, prototype_url, demo_video_url).
- `PATCH /api/submissions/<id>/status` – Admin update status.

## 8. Evaluations (`/api/evaluations`)
- `POST /api/evaluations/submissions/<id>/score` – Evaluator score submission rubric.
- `GET /api/evaluations/competitions/<id>/leaderboard` – Competition leaderboard.
- `GET /api/evaluations/competitions/<id>/results` – Student evaluation breakdown.

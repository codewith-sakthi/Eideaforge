-- ============================================================
-- EIDEAFORGE SEED DATA
-- Default Passwords:
--   Admin:     admin@eideaforge.edu     / Admin@1234
--   Student 1: student1@eideaforge.edu  / Student@123
--   Student 2: student2@eideaforge.edu  / Student@123
--   Evaluator: evaluator1@eideaforge.edu/ Evaluator@123
-- ============================================================

USE eideaforge;

-- Passwords hashed with scrypt/werkzeug:
-- Admin@1234: scrypt:32768:8:1$Pwdw25nzCflcUnfC$823772f283570137b502f2453f2926c6f431fcc69abcb2685b55585ac48556b3c92b676f61ac6777e2df977852e51c424194683d9033b1b5a3bab4e30f87f7b6
-- Student@123: scrypt:32768:8:1$h4mzLuPlMamkzxyN$c4fa718f664bb74b4806104184473204ea02196c5f7e5003dfed5364c424055e7a05441e10af349d688936a1ae02070251f85f6cc69f6441f4205e311dd0d51c
-- Evaluator@123: scrypt:32768:8:1$lfA3otDg9cu44RxD$2281fdaf807e52fb646ce5560755a258965343858b0221a9572750d560f79bf763f000043e6bcd10eb329c01f393efe8784d69a76a2d611ec000d3ef4ddd268b

INSERT INTO users (id, email, password_hash, role) VALUES
(1, 'admin@eideaforge.edu', 'scrypt:32768:8:1$Pwdw25nzCflcUnfC$823772f283570137b502f2453f2926c6f431fcc69abcb2685b55585ac48556b3c92b676f61ac6777e2df977852e51c424194683d9033b1b5a3bab4e30f87f7b6', 'admin'),
(2, 'student1@eideaforge.edu', 'scrypt:32768:8:1$h4mzLuPlMamkzxyN$c4fa718f664bb74b4806104184473204ea02196c5f7e5003dfed5364c424055e7a05441e10af349d688936a1ae02070251f85f6cc69f6441f4205e311dd0d51c', 'student'),
(3, 'student2@eideaforge.edu', 'scrypt:32768:8:1$h4mzLuPlMamkzxyN$c4fa718f664bb74b4806104184473204ea02196c5f7e5003dfed5364c424055e7a05441e10af349d688936a1ae02070251f85f6cc69f6441f4205e311dd0d51c', 'student'),
(4, 'evaluator1@eideaforge.edu', 'scrypt:32768:8:1$lfA3otDg9cu44RxD$2281fdaf807e52fb646ce5560755a258965343858b0221a9572750d560f79bf763f000043e6bcd10eb329c01f393efe8784d69a76a2d611ec000d3ef4ddd268b', 'evaluator')
ON DUPLICATE KEY UPDATE email=VALUES(email);

INSERT INTO student_profiles (user_id, full_name, roll_number, department, year_of_study, bio, skills) VALUES
(2, 'Alex Johnson', 'CS202301', 'Computer Science & Engineering', 3, 'Passionate about AI, full-stack dev and robotics.', 'Python, React, Flask, PyTorch'),
(3, 'Sarah Williams', 'ECE202305', 'Electronics & Communication', 3, 'Hardware hacker, IoT enthusiast and embedded systems designer.', 'C++, Arduino, IoT, Circuit Design')
ON DUPLICATE KEY UPDATE full_name=VALUES(full_name);

INSERT INTO evaluator_profiles (user_id, full_name, department, designation, expertise) VALUES
(4, 'Dr. Marcus Vance', 'Computer Science & Engineering', 'Associate Professor', 'Machine Learning, Distributed Systems, Startup Incubation')
ON DUPLICATE KEY UPDATE full_name=VALUES(full_name);

INSERT INTO ideas (id, student_id, title, description, problem_statement, solution, category, tags, status) VALUES
(1, 2, 'EcoRoute AI', 'AI-powered green logistics and delivery route optimization platform.', 'Urban freight vehicles produce over 28% of urban carbon emissions.', 'A dynamic routing engine using reinforcement learning to minimize carbon output.', 'CleanTech', 'AI, Logistics, Sustainability', 'approved'),
(2, 3, 'SmartHarvest IoT', 'Autonomous precision irrigation and crop health monitoring sensor mesh.', 'Small-scale farmers lose up to 40% yield due to inefficient watering.', 'Solar-powered mesh sensors that trigger micro-drip irrigation autonomously.', 'AgriTech', 'IoT, Sensors, Automation', 'submitted')
ON DUPLICATE KEY UPDATE title=VALUES(title);

INSERT INTO teams (id, name, idea_id, leader_id) VALUES
(1, 'GreenFleet Innovators', 1, 2)
ON DUPLICATE KEY UPDATE name=VALUES(name);

INSERT INTO team_members (team_id, student_id, role) VALUES
(1, 2, 'Leader'),
(1, 3, 'Hardware Engineer')
ON DUPLICATE KEY UPDATE role=VALUES(role);

INSERT INTO competitions (id, title, description, rules, start_date, end_date, status, created_by) VALUES
(1, 'Annual Campus Innovation Challenge 2026', 'Flagship university-wide startup and prototyping hackathon with seed grant prizes.', '1. Teams of 2-5 students.\n2. Must submit a pitch deck and working prototype/demo.\n3. Original ideas only.', CURDATE(), DATE_ADD(CURDATE(), INTERVAL 30 DAY), 'ongoing', 1)
ON DUPLICATE KEY UPDATE title=VALUES(title);

INSERT INTO competition_rounds (id, competition_id, round_number, title, description, start_date, end_date) VALUES
(1, 1, 1, 'Round 1: Idea Pitch & Architecture', 'Submit your pitch deck and system architecture.', CURDATE(), DATE_ADD(CURDATE(), INTERVAL 14 DAY)),
(2, 1, 2, 'Round 2: Prototype Demo & Live Defense', 'Submit your prototype link and video demonstration.', DATE_ADD(CURDATE(), INTERVAL 15 DAY), DATE_ADD(CURDATE(), INTERVAL 30 DAY))
ON DUPLICATE KEY UPDATE title=VALUES(title);

INSERT INTO evaluation_criteria (id, round_id, name, max_score, weightage, description) VALUES
(1, 1, 'Innovation & Originality', 10.00, 1.50, 'Novelty of the solution and market differentiation.'),
(2, 1, 'Technical Feasibility', 10.00, 1.00, 'Practicality of engineering and system design.'),
(3, 1, 'Impact & Market Potential', 10.00, 1.00, 'Commercial viability and societal benefit.')
ON DUPLICATE KEY UPDATE name=VALUES(name);

INSERT INTO competition_evaluators (competition_id, evaluator_id, round_id) VALUES
(1, 4, 1)
ON DUPLICATE KEY UPDATE competition_id=VALUES(competition_id);

INSERT INTO competition_registrations (competition_id, team_id) VALUES
(1, 1)
ON DUPLICATE KEY UPDATE competition_id=VALUES(competition_id);

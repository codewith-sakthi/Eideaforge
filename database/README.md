# Eideaforge Database Guide

## 1. Prerequisites
- MySQL 8.0+ or MariaDB 10.4+
- A user account with permissions to create and modify databases (e.g. `root`)

## 2. Setup Instructions

```bash
# 1. Login to MySQL and create schema
mysql -u root -p < schema.sql

# 2. (Optional) Load demo seed data
mysql -u root -p < seed.sql
```

## 3. Demo Credentials

| Role | Email | Password |
|---|---|---|
| **Admin** | `admin@eideaforge.edu` | `Admin@1234` |
| **Student 1** | `student1@eideaforge.edu` | `Student@123` |
| **Student 2** | `student2@eideaforge.edu` | `Student@123` |
| **Evaluator** | `evaluator1@eideaforge.edu` | `Evaluator@123` |

# Jeron Liaw Xuan Jun's Submission for Tokka Labs Assignment

Steps to run:
1. in flask-backend/app/server.py add in your etherscan api key at line 7
2. in flask-backend run 'python -m app'
3. in react-frontend run 'npm start'

Architectural principles / considerations:
Used Flask for backend as it is lightweight which is suitable for this small project as compared to heavier weight frameworks like Django.
Used React for frontend because of its prevalence and good documentation making it sustainable for future development.
Used SQLite for database as it is portable and can easily be replicated on different computer systems.
Catered persistent volume for SQLite database in docker-compose to help maintain data.

Note: my historical price fxn doesnt work well so im using txn['value'] instead of txn fee
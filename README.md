________________________________________
ACEest Fitness & Gym – CI/CD DevOps Project

Project Overview
This project demonstrates the implementation of a complete DevOps pipeline for the ACEest Fitness & Gym application.
The original system was a Tkinter-based desktop application, which was refactored into a Flask-based REST API to enable automation, testing, containerization, and continuous integration.
The project showcases industry-standard DevOps practices including:
•	Version Control (Git & GitHub)
•	Automated Testing (Pytest)
•	Containerization (Docker)
•	Continuous Integration (GitHub Actions)
•	Build Automation (Jenkins)
________________________________________
Tech Stack
•	Python (Flask)
•	Pytest (Testing Framework)
•	Docker (Containerization)
•	Git & GitHub (Version Control)
•	GitHub Actions (CI Pipeline)
•	Jenkins (Build Automation)
________________________________________
Project Structure
fitnessandgym/
│── app.py
│── requirements.txt
│── tests/
│    └── test_app.py
│── templates/
│    └── index.html
│── Dockerfile
│── aceest.db
│── .github/
│    └── workflows/
│         └── main.yml
│── README.md
________________________________________
 Local Setup Instructions
1.	Install all prerequisite tech stack including git, python, docker, Jenkins etc
2.	Clone Repository
git clone https://github.com/2024ht66523/fitnessandgym.git
cd fitnessandgym

3.	Install Dependencies
pip install -r requirements.txt
4.	Running Tests (Pytest)
python -m pytest
✔ Validates API endpoints
✔ Ensures application correctness before deployment
5.	Run Application
python app.py

6.	Access API
http://localhost:5000
http://localhost:5000/programs

7.	Access GUI
http://localhost:5000/ui
________________________________________
Manual test, build and deployment
1.	After the code and other required files are updated, make sure to add any new dependency to the requirement.txt file as well otherwise the automation will fail.
2.	Go to the working directory of the code
3.	Run the pytest:
python -m pytest
4.	After the test is a success, run the application:
python app.py
5.	Check if the application is working correctly by visiting the below URL with browser:
http://localhost:5000
http://localhost:5000/programs 
http://localhost:5000/ui 

 
Docker Setup
6.	Build Image
docker build -t aceest-gym .
7.	Run Container
docker run -p 5000:5000 aceest-gym
________________________________________
Automation using CI/CD Pipeline (GitHub Actions)
The pipeline is triggered on every:
•	Push
•	Pull Request
Pipeline Stages:
1.	Install dependencies
2.	Lint check (flake8)
3.	Run Pytest
4.	Build Docker image

After the application is tested locally, push the code to git
Use the following command to push the code to git repository:
•	git add . 
•	git commit -m “#Comments/description” 
•	git push
After the code is pushed to git repository, it will run the build test, check if it is successful by visiting git actions

________________________________________
 
Jenkins Integration
Jenkins is used as a secondary build validation layer.
Workflow:
GitHub Push →
GitHub Actions (CI) →
   ✔ Lint
   ✔ Test
   ✔ Docker Build
Jenkins →
   ✔ Pull latest code
   ✔ Build & Test again
This ensures high reliability and quality control.

1.	Create a new item in Jenkins
2.	Add git repository url in source-code management and also specify the brain(*/main)
3.	Keep triggers to Poll SCM with value – “H/2 * * * *”. This will poll git every 2 minutes
4.	Define Build Steps as Windows bash/Shell commands or as per your requirements:
pip install -r requirements.txt
python -m pytest
docker stop aceest-gym || true
docker rm aceest-gym || true
docker build -t aceest-gym .
docker run -d -p 5000:5000 --name aceest-gym aceest-gym

Note : As we are using Jekins as local setup webhooks will not work.  In order to use webhook to trigger Jenkins with every pull or push, Jenkins must be publicly available.

Now any change in git repository will trigger Jenkins and deploy the new application automatically after automatic testing.
If the test fails the deployment will be aborted.
If for any reason there is a requirement for rollback, we can always deploy previous build through Jenkins as well as docker.

________________________________________
Key DevOps Features Implemented
✔ Version-controlled development lifecycle
✔ Automated testing using Pytest
✔ Containerized application using Docker
✔ CI pipeline using GitHub Actions
✔ Automated build verification using Jenkins
________________________________________

👨‍💻 Author
•	Name: INDERVIJAY SINGH (2024HT66523)
•	Course: M.Tech – DevOps
•	Assignment: ACEest Fitness & Gym CI/CD Implementation

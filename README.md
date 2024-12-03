Implementation of a REST api with a simple frontend for the assignment "REST API:  Building a Scalable RESTful Web Service with Advanced Features"

Components:
    Flask backend (Python)
    React frontend (Javascript)

Usage:

    Backend:
        Navigate to "REST_API\registration_app"
        "pip install requirements.txt" to get all dependencies
        "flask run" to start the backend
        flask will then show the ip and port it's running on e.g "* Running on http://127.0.0.1:5000"
        from here you can manually enter the route "/fill_database" like "http://127.0.0.1:5000/fill_database" to populate the database with random names and symptoms

    Frontend:
        Navigate to "REST_API\client\symptom-tracker-frontend\src"
        "npm install"
        "npm run"
        This should bring you to a register/login page in your default browser

A demonstration of functions available to the frontend is in the file "REST.pdf"


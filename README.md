# FastAPI Event Management

This is a FastAPI project for managing events and attendees. The API provides features to create, manage, and track events and attendees.

**Project Details**

Event Management: Create, update, and list events.
Attendee Management: Register attendees, check-in attendees, and list attendees for an event.
Automatic Status Updates: The event status is automatically updated based on the current time.

## Setup Instructions

### Prerequisites

- Python 3.7 or higher
- pip

### Deployment

1. **Clone the Repository or Extract the Zip File**

   If you received a zip file, extract it to a directory of your choice.

   If you have access to a Git repository, clone it:

   ```sh
   git clone <repository_url>
   
2. **Create a Virtual Environment**
   
    `python -m venv venv`

3. **Activate the Virtual Environment**

    On Windows:

    `.\venv\Scripts\activate`

    On macOS/Linux:

    `source venv/bin/activate`

4. **Install the Required Packages**

    `pip install -r requirements.txt`

5. **Run the FastAPI Application**

    `uvicorn main:app --reload`

6. **Access the API Documentation**

    Open your web browser and go to http://127.0.0.1:8000/docs to access the interactive API documentation provided by Swagger UI.

7. **Running the Tests**

    Use the pytest command to run the tests:

    `pytest`

**Contact**

    Sagar Hallikar
    Email: sagarhallikar@gmail.com
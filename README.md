Vehicle Speed Detection System 🚗💨
A web-based application designed to analyze traffic video footage and accurately estimate vehicle speeds. This project leverages a powerful combination of computer vision, deep learning, and a user-friendly web interface to provide a complete solution for traffic monitoring.

✨ Key Features
Secure User Authentication: A complete registration and login system to ensure private and secure access for users.

Intuitive Video Upload: A simple interface for users to upload traffic videos directly from their local machine for analysis.

Advanced Speed Estimation: Employs sophisticated deep learning models and computer vision techniques (like optical flow and object tracking) to detect vehicles and calculate their speed with high precision.

High Accuracy: Engineered to achieve a low average speed detection error of approximately ±7 km/h, as highlighted in the platform's features.

Scalable & Real-Time Ready: The architecture supports real-time traffic monitoring, anomaly detection, and vehicle re-identification, making it suitable for smart city applications.

Responsive Frontend: A clean and modern user interface built with HTML, CSS, and JavaScript.

💻 Technology Stack
This project is built using a modern and robust stack of technologies:

Frontend: HTML, CSS, JavaScript

Backend: Python, Flask

Database: MySQL

Machine Learning / Deep Learning: OpenCV, TensorFlow / PyTorch, NumPy, Pandas
(Note: Please update the list of ML/DL libraries with the specific ones you used)

⚙️ Setup and Installation
To get this project running on your local machine, follow these steps:

1. Prerequisites
Make sure you have the following installed:

Python 3.8+

MySQL Server

Git

2. Clone the Repository
Bash

git clone https://github.com/your-username/your-repository-name.git
cd your-repository-name
3. Create a Virtual Environment
It's highly recommended to use a virtual environment to manage project dependencies.

On macOS/Linux:

Bash

python3 -m venv venv
source venv/bin/activate
On Windows:

Bash

python -m venv venv
.\venv\Scripts\activate
4. Install Dependencies
Install all the required Python packages from the requirements.txt file.
(If you haven't created one, run pip freeze > requirements.txt in your activated environment).

Bash

pip install -r requirements.txt
5. Database Setup
Log in to your MySQL server.

Create a new database for the project.

SQL

CREATE DATABASE vehicle_speed_db;
Import the necessary table structures. If you have a .sql schema file, you can import it. Otherwise, you may need to run the initial migrations using Flask-Migrate if it's set up.

6. Configure Environment Variables
Create a .env file in the root directory and add your configuration details. This keeps your sensitive information secure.

Code snippet

# Flask Configuration
SECRET_KEY='a_very_secret_and_random_key'
FLASK_ENV=development

# Database Configuration
DB_HOST='localhost'
DB_USER='your_mysql_username'
DB_PASSWORD='your_mysql_password'
DB_NAME='vehicle_speed_db'
7. Run the Application
Execute the following command to start the Flask development server:

Bash

flask run
The application should now be running at http://127.0.0.1:5000.

🚀 How to Use
Navigate to the application URL in your web browser.

Register for a new account using the registration form.

Login with your newly created credentials.

You will be redirected to the main dashboard. Click on "Start Analyzing Now" or navigate to the "Upload" page.

Choose a traffic video file (.mp4, .avi, etc.) and click "Upload Video".

The system will process the video, and once the analysis is complete, it will display the speed detection results.

🖼️ Screenshots
<img width="1920" height="1080" alt="image" src="https://github.com/user-attachments/assets/7883e280-a7b7-4c3e-bbd5-addda238a2d1" />
<img width="1920" height="1080" alt="image" src="https://github.com/user-attachments/assets/57606392-cb70-4c54-a94b-ee6b9bcaf622" />
<img width="1920" height="1080" alt="image" src="https://github.com/user-attachments/assets/29efb4a6-1962-4d7d-832f-18f8129fa1a5" />
<img width="1920" height="1080" alt="image" src="https://github.com/user-attachments/assets/51ccfc55-976e-4e11-ab60-3c911b1e85f5" />
<img width="1920" height="1080" alt="image" src="https://github.com/user-attachments/assets/2fb4bc2a-97d7-45ed-bc46-3bd7e72ecd2d" />






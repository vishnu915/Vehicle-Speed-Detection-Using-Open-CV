import os
import math
import cv2
import dlib
from flask import (
    Flask,
    render_template,
    request,
    redirect,
    flash,
    send_from_directory,
    session,
)
import mysql.connector
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.secret_key = 'supersecretkey'  # Required for flash messages

UPLOAD_FOLDER = 'static/uploads'
ALLOWED_EXTENSIONS = {'mp4', 'avi', 'mov'}

if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


# MySQL database connection - keep only one connection here with correct password
mydb = mysql.connector.connect(
    host="localhost",
    user="root",
    password="vishnu@123",
    port="3306",
    database="vehicle"
)
mycursor = mydb.cursor()
print("Database connection successful!")


# Vehicle speed estimation function
def estimateSpeed(location1, location2):
    d_pixels = math.sqrt(
        math.pow(location2[0] - location1[0], 2) +
        math.pow(location2[1] - location1[1], 2)
    )
    ppm = 8.8  # pixels per meter
    d_meters = d_pixels / ppm
    fps = 15  # frames per second of video
    speed = d_meters * fps * 3.6  # Convert to km/hr
    return speed


# Track multiple objects (cars)
def trackMultipleObjects(video_path):
    carCascade = cv2.CascadeClassifier('myhaar.xml')  # Haar cascade for car detection
    video = cv2.VideoCapture(video_path)
    WIDTH = 1280
    HEIGHT = 720
    carTracker = {}
    carLocation1 = {}
    carLocation2 = {}
    speed = [None] * 1000
    fourcc = cv2.VideoWriter_fourcc(*'MJPG')
    out = cv2.VideoWriter('outpy.avi', fourcc, 20.0, (WIDTH, HEIGHT))

    currentCarID = 0
    frameCounter = 0

    while True:
        rc, image = video.read()
        if type(image) == type(None):
            break
        
        image = cv2.resize(image, (WIDTH, HEIGHT))
        resultImage = image.copy()
        
        frameCounter += 1
        carIDtoDelete = []

        for carID in list(carTracker.keys()):
            trackingQuality = carTracker[carID].update(image)
            if trackingQuality < 7:
                carIDtoDelete.append(carID)

        for carID in carIDtoDelete:
            carTracker.pop(carID, None)
            carLocation1.pop(carID, None)
            carLocation2.pop(carID, None)

        if not (frameCounter % 10):
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            cars = carCascade.detectMultiScale(gray, 1.1, 13, 18, (24, 24))

            for (_x, _y, _w, _h) in cars:
                x = int(_x)
                y = int(_y)
                w = int(_w)
                h = int(_h)
                x_bar = x + 0.5 * w
                y_bar = y + 0.5 * h
                matchCarID = None

                for carID in carTracker.keys():
                    trackedPosition = carTracker[carID].get_position()
                    t_x = int(trackedPosition.left())
                    t_y = int(trackedPosition.top())
                    t_w = int(trackedPosition.width())
                    t_h = int(trackedPosition.height())
                    t_x_bar = t_x + 0.5 * t_w
                    t_y_bar = t_y + 0.5 * t_h

                    if (t_x <= x_bar <= (t_x + t_w)) and (t_y <= y_bar <= (t_y + t_h)):
                        matchCarID = carID

                if matchCarID is None:
                    tracker = dlib.correlation_tracker()
                    tracker.start_track(image, dlib.rectangle(x, y, x + w, y + h))
                    carTracker[currentCarID] = tracker
                    carLocation1[currentCarID] = [x, y, w, h]
                    currentCarID += 1

        for carID in carTracker.keys():
            trackedPosition = carTracker[carID].get_position()
            t_x = int(trackedPosition.left())
            t_y = int(trackedPosition.top())
            t_w = int(trackedPosition.width())
            t_h = int(trackedPosition.height())
            carLocation2[carID] = [t_x, t_y, t_w, t_h]
            cv2.rectangle(resultImage, (t_x, t_y), (t_x + t_w, t_y + t_h), (0, 0, 150), 4)

        for i in carLocation1.keys():
            if frameCounter % 1 == 0:
                [x1, y1, w1, h1] = carLocation1[i]
                [x2, y2, w2, h2] = carLocation2[i]

                carLocation1[i] = [x2, y2, w2, h2]

                if [x1, y1, w1, h1] != [x2, y2, w2, h2]:
                    if speed[i] is None and y1 >= 275 and y1 <= 285:
                        speed[i] = estimateSpeed([x1, y1, w1, h1], [x2, y2, w2, h2])

                    if speed[i] is not None and y1 >= 180:
                        cv2.putText(resultImage, str(int(speed[i])) + " km/hr",
                                    (int(x1 + w1 / 2), int(y1 - 5)),
                                    cv2.FONT_HERSHEY_SIMPLEX, 0.80,
                                    (0, 255, 0), 2)

        out.write(resultImage)
        cv2.imshow('Result', resultImage)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
    video.release()
    out.release()
    cv2.destroyAllWindows()


# Routes

@app.route("/")
def index():
    return render_template("index.html")


@app.route("/about")
def about():
    return render_template("about.html")


@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        email = request.form.get("email")
        password = request.form.get("password")
        c_password = request.form.get("confirm_password")

        if not email or not password or not c_password:
            return render_template('register.html', message="All fields are required!")

        if password != c_password:
            return render_template("register.html", message="Confirm password does not match!")

        # Check if email already exists
        query = "SELECT email FROM users WHERE email = %s"
        mycursor.execute(query, (email,))
        email_data = mycursor.fetchone()

        if email_data:
            return render_template("register.html", message="This email ID already exists!")

        hashed_password = generate_password_hash(password, method="pbkdf2:sha256")

        query = "INSERT INTO users (email, password) VALUES (%s, %s)"
        try:
            mycursor.execute(query, (email, hashed_password))
            mydb.commit()
        except mysql.connector.Error as err:
            return render_template("register.html", message="Database error: " + str(err))

        return render_template("login.html", message="Successfully Registered!")

    return render_template("register.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form["email"]
        password = request.form["password"]
        query = "SELECT email, password FROM users WHERE email = %s"
        mycursor.execute(query, (email,))
        user = mycursor.fetchone()
        if user and check_password_hash(user[1], password):
            session["user_email"] = email
            return redirect("/home")
        return render_template("login.html", message="Invalid email or password!")
    return render_template("login.html")


@app.route("/home")
def home():
    if "user_email" not in session:
        return redirect("/login")
    return render_template("home.html")


@app.route("/upload", methods=["GET", "POST"])
def upload():
    if request.method == "POST":
        video = request.files.get("video")
        if video and allowed_file(video.filename):
            video_filename = video.filename
            video_path = os.path.join(UPLOAD_FOLDER, video_filename)
            video.save(video_path)

            # Process the uploaded video
            trackMultipleObjects(video_path)

            flash("Video uploaded and processed successfully!", "success")
            # Optionally, redirect to the uploaded file or another page
            # return redirect(f"/uploads/{video_filename}")
        else:
            flash("Invalid file format. Please upload a video.", "error")
            return render_template("upload.html")
    return render_template("upload.html")


@app.route('/uploads/<filename>')
def send_file(filename):
    return send_from_directory(UPLOAD_FOLDER, filename)


if __name__ == "__main__":
    app.run(debug=True)

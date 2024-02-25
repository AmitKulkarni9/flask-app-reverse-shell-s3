import boto3
import uuid
import os

from flask import Flask, redirect, url_for, request, render_template
from flask_sqlalchemy import SQLAlchemy
from werkzeug.utils import secure_filename
from os import environ

ALLOWED_EXTENSIONS = {'txt', 'pdf', 'png', 'jpeg'}

app = Flask(__name__, static_folder='tmp')

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

db = SQLAlchemy()

class File(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    original_filename = db.Column(db.String(100))
    filename = db.Column(db.String(100))
    bucket = db.Column(db.String(100))
    region = db.Column(db.String(100))

def create_app():
    #app = Flask(__name__, static_folder='tmp')
    app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///db.sqlite3"
    app.config["Accesskey"] = environ.get('aws_access_key_id')
    app.config["Secretkey"] = environ.get('aws_secret_access_key')

    s3 = boto3.client('s3', aws_access_key_id=app.config['Accesskey'], aws_secret_access_key=app.config['Secretkey'])

    db.init_app(app)


    @app.route("/", methods=["GET", "POST"])
    def index():

        if request.method == 'POST':
            uploaded_file = request.files['file-to-save']
            image = request.files['file-to-save']
            #We're reading the contents of the uploaded image file and storing it with in a variable called data
            data = image.read()
            #Moving the file pointer back to the start of the file. If you remove this line file won't get saved :( 
            image.seek(0)
            
            # if not allowed_file(uploaded_file.filename):
            #     return "FILE NOT ALLOWED!"

            if uploaded_file:
                    bucket_name = "s3-example-web-app-022024"
                    filename = secure_filename(uploaded_file.filename)
                    new_filename = uuid.uuid4().hex + '.' + uploaded_file.filename.rsplit('.', 1)[1].lower()
                    uploaded_file.save(new_filename)
                    s3.upload_file(
                        Bucket = bucket_name,
                        Filename=new_filename,
                        Key = new_filename
                    )

            file = File(original_filename=uploaded_file.filename, filename=new_filename,
                bucket=bucket_name, region="us-east-1")

            db.session.add(file)
            db.session.commit()
            
            # check if the file is a valid image or not
            if not validate_image(data):
                return "Invalid image file"
            #tmp_dir = '/var/www/file_upload_vuln/tmp'
            tmp_dir = '/tmp'
            # save the image to disk if it is a valid image
            image.save(os.path.join(tmp_dir,image.filename))

            

            return redirect(url_for("index"))

        files = File.query.all()

        return render_template("index.html", files=files)

    def validate_image(data):
        # check if the data is a valid image
        # this is a simple example and not a full validation function
        # in practice, you would need to implement more robust validation
        return data[:4] == b'\xff\xd8\xff\xe0' or data[:4] == b'\xff\xd8\xff\xe1'

    return app

# if __name__ == "__main__":
#     app.run(debug=True,host='0.0.0.0',port=5000)    
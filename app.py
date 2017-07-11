from flask import Flask
import audio_features0


app = Flask(__name__)

@app.route("/")
def welcome():
	login_url = audio_features0.user_login()
	return login_url

if __name__ == "__main__":
    app.run()
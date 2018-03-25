from flask import Flask, render_template, request, url_for, session, redirect
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.secret_key = 'MyChoice'

app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///data.db"
app.config["SQLALCHEMY_ECHO"] = True
db = SQLAlchemy(app)

class RegisteredUsers(db.Model):
    __tablename__ = 'registeredUsers'
    id = db.Column(db.String(50), primary_key=True)
    password = db.Column(db.String(50))
    name = db.Column(db.String(50))
    phoneNumber = db.Column(db.String(15))
    sequrityQuestion = db.Column(db.String(100))
    sequrityAnswer = db.Column(db.String(50))

    def __init__(self, id, password, name, phoneNumber, sequrityQuestion, sequrityAnswer):
        self.id = id
        self.password = password
        self.name = name
        self.phoneNumber = phoneNumber
        self.sequrityQuestion = sequrityQuestion
        self.sequrityAnswer = sequrityAnswer


class PollInfo(db.Model):
    __tablename__ = 'pollInfo'
    id = db.Column(db.Integer, primary_key=True)
    userId = db.Column(db.String(50))
    pollQuestion = db.Column(db.String(300))
    numOfOptions = db.Column(db.Integer)
    isOpen = db.Column(db.Boolean)
    isRated = db.Column(db.Boolean)
    selectionChoices = db.Column(db.Integer)
    isTimed = db.Column(db.Boolean)
    timeLimit = db.Column(db.DateTime)
    numOfReports = db.Column(db.Integer)
    numOfRegistrants = db.Column(db.Integer)
    numOfVotes = db.Column(db.Integer)

    def __init__(self, userId, pollQuestion, numOfOptions, isOpen, isRated, selectionChoices, \
        isTimed, timeLimit, numOfReports, numOfRegistrants, numOfVotes):
        self.userId = userId
        self.pollQuestion = pollQuestion
        self.numOfOptions = numOfOptions
        self.isOpen = isOpen
        self.isRated = isRated
        self.selectionChoices = selectionChoices
        self.isTimed = isTimed
        self.timeLimit = timeLimit
        self.numOfReports = numOfReports
        self.numOfRegistrants = numOfRegistrants
        self.numOfVotes = numOfVotes


class Options(db.Model):
    __tablename__ = 'options'
    id = db.Column(db.Integer, primary_key=True)
    pollId = db.Column(db.Integer)
    optionData = db.Column(db.String(100))
    optionImage = db.Column(db.LargeBinary)
    optionCount = db.Column(db.Float)

    def __init__(self, pollId, optionData, optionImage, optionCount):
        self.pollId = pollId
        self.optionData = optionData
        self.optionImage = optionImage
        self.optionCount = optionCount


class Registrants(db.Model):
    __tablename__ = 'registrants'
    pollId = db.Column(db.Integer, primary_key=True)
    userId = db.Column(db.String(50), primary_key=True)
    isRegistered = db.Column(db.Boolean)

    def __init__(self, pollId, userId, isRegistered):
        self.pollId = pollId
        self.userId = userId
        self.isRegistered = isRegistered


class Votes(db.Model):
    __tablename__ = 'votes'
    pollId = db.Column(db.Integer, primary_key=True)
    userId = db.Column(db.String(50), primary_key=True)
    choiceId = db.Column(db.Integer)

    def __init__(self, pollId, userId, choiceId):
        self.pollId = pollId
        self.userId = userId
        self.choiceId = choiceId


class Selections(db.Model):
    __tablename__ = 'selections'
    pollId = db.Column(db.Integer, primary_key=True)
    userId = db.Column(db.String(50), primary_key=True)
    combinationId = db.Column(db.Integer, primary_key=True)
    choiceId = db.Column(db.Integer)

    def __init__(self, pollId, userId, combinationId, choiceId):
        self.pollId = pollId
        self.userId = userId
        self.combinationId = combinationId
        self.choiceId = choiceId


@app.route("/")
def home():
	return render_template("home.html")

@app.route("/register")
def register():
	return render_template("register.html", message="")

@app.route("/login", methods=["GET", "POST"])
def login():
	if request.method == "GET":
		return render_template("login.html", message="")
	elif request.method == "POST":
		users = RegisteredUsers.query.with_entities(RegisteredUsers.id).all()
		userIds = []
		for user in users:
			userIds.append(user[0])
		if request.form["name"] == "":
			return render_template("register.html", message="Please provide your name.")
		elif request.form["id"] == "" or request.form["id"] in userIds:
			return render_template("register.html", message="Choose a different ID.")
		elif len(request.form["password"]) < 8:
			return render_template("register.html", message="Password too short!")
		else:
			user = RegisteredUsers(request.form["id"], request.form["password"], request.form["name"])
			db.session.add(user)
			db.session.commit()
			return render_template("login.html", message="Registration successful!")

@app.route("/profile", methods=["POST"])
def profile():
	users = RegisteredUsers.query.filter(RegisteredUsers.id == request.form["id"]).all()
	if len(users) != 0 and users[0].password == request.form["password"]:
		session["userId"] = users[0].id
		session["password"] = users[0].password
		session["name"] = users[0].name
		session["phoneNumber"] = users[0].phoneNumber
		return redirect(url_for('polling'))
	else:
		return render_template("login.html", message="Invalid username or password!")

@app.route("/polling", methods=["GET", "POST"])
def polling():
	polls = PollInfo.query.with_entities(PollInfo.id, PollInfo.isRated, PollInfo.pollQuestion, PollInfo.userId).all()
	# polls = PollInfo.query.filter(PollInfo.isRated == False).all()
	return render_template("polling.html", polls=polls)

@app.route("/rating", methods=["GET", "POST"])
def rating():
	polls = PollInfo.query.with_entities(PollInfo.id, PollInfo.isRated, PollInfo.pollQuestion, PollInfo.userId).all()
	# polls = PollInfo.query.filter(PollInfo.isRated == True).all()
	return render_template("rating.html", polls=polls)

@app.route("/poll", methods=["POST"])
def poll():
	pollInfo = {}
	pollInfo["pollId"] = int(request.form["id"])
	pollInfo["userId"] = request.form["userId"]
	pollInfo["isRated"] = bool(request.form["isRated"])
	pollInfo["pollQuestion"] = request.form["pollQuestion"]
	pollInfo["username"] = RegisteredUsers.query.filter(RegisteredUsers.id == pollInfo["pollId"]).first().id
	pollInfo["options"] = Options.query.filter(Options.pollId == pollInfo["pollId"])
	return render_template("poll.html", pollInfo=pollInfo)


@app.route("/rate", methods=["POST"])
def rate():
    pass

@app.route("/editprofile", methods=["GET"])
def editprofile():
    return render_template("editprofile.html", user=session)

@app.route("/createpoll", methods=["GET"])
def createpoll():
    return render_template("createpoll.html")

@app.route("/mypolls", methods=["GET", "POST"])
def mypolls():
	userId = session["userId"]
	pollsOfUser = PollInfo.query.filter(PollInfo.userId == userId).all()
	options = []
	for poll in pollsOfUser:
		option = Options.query.filter(Options.pollId == poll.id).all()
		options.append(option)

	l = len(pollsOfUser)
	ranks = []
	for i in range(l) :
		tempRank = []
		for option in options[i] :
			tempRank.append( (option.optionCount , option.optionData) )
		tempRank.sort(reverse=True)
		ranks.append(tempRank)
	return render_template("mypolls.html", ranks = ranks, pollsOfUser = pollsOfUser, l = l)

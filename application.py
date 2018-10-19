from flask import Flask, render_template, request, url_for, session, redirect
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.secret_key = 'MyChoice'

app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///data.db"
db = SQLAlchemy(app)

class RegisteredUsers(db.Model):
    __tablename__ = 'registeredUsers'
    id = db.Column(db.String(50), primary_key=True)
    password = db.Column(db.String(50), nullable=False)
    name = db.Column(db.String(50), nullable=False)
    phoneNumber = db.Column(db.String(15))
    sequrityQuestion = db.Column(db.String(100))
    sequrityAnswer = db.Column(db.String(50))
    numOfPolls = db.Column(db.Integer, default=0)
    polls = db.relationship('PollInfo', backref='user')
    registrations = db.relationship('Registrants', backref='user')
    votes = db.relationship('Votes', backref='user')
    selections = db.relationship('Selections', backref='user')
    reports = db.relationship('Reports', backref='user')

    def __init__(self, id, password, name, phoneNumber=None, sequrityQuestion=None, sequrityAnswer=None):
        self.id = id
        self.password = password
        self.name = name
        self.phoneNumber = phoneNumber
        self.sequrityQuestion = sequrityQuestion
        self.sequrityAnswer = sequrityAnswer


class PollInfo(db.Model):
    __tablename__ = 'pollInfo'
    id = db.Column(db.Integer, primary_key=True)
    userId = db.Column(db.String(50), db.ForeignKey('registeredUsers.id'), nullable=False)
    pollQuestion = db.Column(db.String(300), nullable=False)
    numOfOptions = db.Column(db.Integer)
    isOpen = db.Column(db.Boolean)
    isRated = db.Column(db.Boolean)
    selectionChoices = db.Column(db.Integer)
    isTimed = db.Column(db.Boolean)
    timeLimit = db.Column(db.DateTime)
    numOfReports = db.Column(db.Integer)
    numOfRegistrants = db.Column(db.Integer)
    numOfVotes = db.Column(db.Integer)
    options = db.relationship('Options', backref='poll')
    registrants = db.relationship('Registrants', backref='poll')
    voters = db.relationship('Votes', backref='poll')
    selectors = db.relationship('Selections', backref='poll')
    reports = db.relationship('Reports', backref='poll')

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
    pollId = db.Column(db.Integer, db.ForeignKey('pollInfo.id'), nullable=False)
    optionData = db.Column(db.String(100), nullable=False)
    optionImage = db.Column(db.LargeBinary)
    optionCount = db.Column(db.Float)

    def __init__(self, pollId, optionData, optionImage, optionCount):
        self.pollId = pollId
        self.optionData = optionData
        self.optionImage = optionImage
        self.optionCount = optionCount


class Registrants(db.Model):
    __tablename__ = 'registrants'
    pollId = db.Column(db.Integer, db.ForeignKey('pollInfo.id'), primary_key=True, nullable=False)
    userId = db.Column(db.String(50), db.ForeignKey('registeredUsers.id'), primary_key=True, nullable=False)
    isRegistered = db.Column(db.Boolean)

    def __init__(self, pollId, userId, isRegistered):
        self.pollId = pollId
        self.userId = userId
        self.isRegistered = isRegistered


class Votes(db.Model):
    __tablename__ = 'votes'
    pollId = db.Column(db.Integer, db.ForeignKey('pollInfo.id'), primary_key=True, nullable=False)
    userId = db.Column(db.String(50), db.ForeignKey('registeredUsers.id'), primary_key=True, nullable=False)
    choiceId = db.Column(db.Integer, nullable=False)

    def __init__(self, pollId, userId, choiceId):
        self.pollId = pollId
        self.userId = userId
        self.choiceId = choiceId


class Selections(db.Model):
    __tablename__ = 'selections'
    pollId = db.Column(db.Integer, db.ForeignKey('pollInfo.id'), primary_key=True, nullable=False)
    userId = db.Column(db.String(50), db.ForeignKey('registeredUsers.id'), primary_key=True, nullable=False)
    combinationId = db.Column(db.Integer, primary_key=True, nullable=False)
    choiceId = db.Column(db.Integer, nullable=False)

    def __init__(self, pollId, userId, combinationId, choiceId):
        self.pollId = pollId
        self.userId = userId
        self.combinationId = combinationId
        self.choiceId = choiceId


class Reports(db.Model):
    __tablename__ = 'reports'
    userId = db.Column(db.String(50), db.ForeignKey('registeredUsers.id'), primary_key=True, nullable=False)
    pollId = db.Column(db.Integer, db.ForeignKey('pollInfo.id'), primary_key=True, nullable=False)

    def __init__(self, userId, pollId):
        self.userId = userId
        self.pollId = pollId


@app.route("/")
def home():
	return render_template("home.html")


@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "GET":
        return render_template("register.html", message="")
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


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "GET":
        return render_template("login.html", message="")
    elif request.method == "POST":
        user = RegisteredUsers.query.filter(RegisteredUsers.id == request.form["id"]).first()
        if user != None and user.password == request.form["password"]:
            session["name"] = user.name
            session["userId"] = user.id
            session["phoneNumber"] = user.phoneNumber
            return redirect(url_for('polling'))
        else:
            return render_template("login.html", message="Invalid username or password!")


@app.route("/polling")
def polling():
    polls = PollInfo.query.filter(PollInfo.isRated == False).all()
    return render_template("polling.html", polls=polls)


@app.route("/rating")
def rating():
    polls = PollInfo.query.filter(PollInfo.isRated == True).all()
    return render_template("rating.html", polls=polls)


@app.route("/vote", methods=["POST"])
def vote():
    poll = PollInfo.query.filter(PollInfo.id == int(request.form["poll"])).first()
    if request.form["response"] == "Vote":
        option = Options.query.filter(Options.id == int(request.form["choice"])).first()
        oldVote = Votes.query.filter(Votes.userId == session["userId"], Votes.pollId == poll.id).first()
        if oldVote != None:
            oldOption = Options.query.filter(Options.id == oldVote.choiceId).first()
            oldOption.optionCount = oldOption.optionCount - 1
            poll.numOfVotes = poll.numOfVotes - 1
            db.session.delete(oldVote)
        newVote = Votes(poll.id, session["userId"], option.id)
        if option.optionCount == None:
            option.optionCount = 1
        else:
            option.optionCount = option.optionCount + 1
        if poll.numOfVotes == None:
            poll.numOfVotes = 1
        else:
            poll.numOfVotes = poll.numOfVotes + 1
        db.session.add(newVote)
        db.session.commit()
    elif request.form["response"] == "Report":
        report = Reports.query.filter(Reports.userId == session["userId"], Reports.pollId == poll.id).first()
        if report != None:
            return redirect(url_for('polling'))
        else:
            if poll.numOfReports == None:
                poll.numOfReports = 1
            else:
                poll.numOfReports = poll.numOfReports + 1
            newReport = Reports(session["userId"], poll.id)
            db.session.add(newReport)
            db.session.commit()
    return redirect(url_for('polling'))


@app.route("/editprofile", methods=["GET", "POST"])
def editprofile():
    user = RegisteredUsers.query.filter(RegisteredUsers.id == session["userId"]).first()
    if request.method == "GET":
        return render_template("editprofile.html", user=user, message="EDIT PROFILE")
    elif request.method == "POST":
        if request.form["response"] == "Update":
            if request.form["name"] == "":
                return render_template("editprofile.html", user=user, message="Please provide your name.")
            elif request.form["password"] != user.password:
                return render_template("editprofile.html", user=user, message="Invalid password!")
            elif request.form["newPassword"] != request.form["confirmPassword"]:
                return render_template("editprofile.html", user=user, message="Password did't match!")
            elif len(request.form["newPassword"]) < 8:
                return render_template("editprofile.html", user=user, message="Password too short!")
            else:
                user.name = request.form["name"]
                user.password = request.form["newPassword"]
                user.phoneNumber = request.form["phoneNumber"]
                user.sequrityQuestion = request.form["sequrityQuestion"]
                user.sequrityAnswer = request.form["sequrityAnswer"]
                db.session.commit()
            return render_template("editprofile.html", user=user, message="Profile updated!")
        elif request.form["response"] == "Cancel":
            return redirect(url_for('polling'))


@app.route("/createpoll", methods=["GET", "POST"])
def createpoll():
    userId = session["userId"]
    if request.method == "GET":
        return render_template("createpoll.html")
    elif request.method == "POST":
        pollQuestion = request.form["pollQuestion"]
        # timeLimit = request.form.get("timeLimit")
        isRated = request.form.get("isRated")
        isOpen = request.form.get("isOpen")
        options = request.form["options"]
        listOfOptions = options.split(",")
        print(pollQuestion, isRated, isOpen, listOfOptions)

        # poll = PollInfo()
        # poll.userId = userId
        # poll.pollQuestion = pollQuestion
        # poll.numOfOptions = numOfOptions
        # poll.timeLimit = timeLimit
        # poll.isRated = isRated
        # poll.isOpen = isOpen
        #
        # db.session.add(poll)
        # db.session.commit()
        #
        # for o in listOfOptions :
        #     options = Options()
        #     options.pollId = poll.id
        #     options.optionData = o
        #     db.session.add(o)
        #     db.session.commit()

        # render_template("login.html")
        return redirect(url_for('polling'))


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


@app.route("/logout")
def logout():
    session["name"] = ""
    session["userId"] = ""
    session["phoneNumber"] = ""
    return render_template("home.html")

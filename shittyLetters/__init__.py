import lob
import os
import random
import stripe
from flask import Flask, render_template, request, jsonify
from flask.ext.sqlalchemy import SQLAlchemy

stripe.api_key = os.environ["STRIPE_API"]
stripe.api_version = '2015-02-18'

lob.api_key = os.environ["LOB_API"]
lob.api_version = '2014-12-18'

COST_OF_POSTCARD_IN_CENTS = int(2.50 * 100)

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ["DATABASE_URI"]
app.config['SECRET_KEY'] = os.environ["SECRET_KEY"]

db = SQLAlchemy(app)

class Message(db.Model):
  id = db.Column(db.Integer, primary_key=True)
  message = db.Column(db.String(350), unique=True)
  category = db.Column(db.Integer)
  count = db.Column(db.Integer)

  def __init__(self, message, category, count):
    self.message = message
    self.category = category
    self.count = count

def setup_db(seed=False):
  db.drop_all()
  db.create_all()

  if seed:
    db.session.add(Message("It's not the dress that makes you look fat, it's the fat.", 0, 0))
    db.session.add(Message("Sometimes I poop clear and think of you.", 0, 0))
    db.session.add(Message("#yolo", 0, 0))
    db.session.add(Message("Your advice is like a fat guy telling you how to diet.", 0, 0))
    db.session.add(Message("Your parents didn't abort you cus they were watching Bob Ross.", 0, 0))
    db.session.add(Message("Follow your dreams because we love to see your disappointment.", 0, 0))
    db.session.add(Message("We see you aren't getting enough post cards. Would you like more friends?", 0, 0))
    db.session.add(Message("Every day you live a puppy dies. Dick", 0, 0))
    db.session.add(Message("Post cards are our way of saying \"hahahaha\".", 0, 0))
    db.session.add(Message("Second place is your throne.", 0, 0))
    db.session.add(Message("Choo! Choo! Looks like your moms coming!", 0, 0))
    db.session.add(Message("You confused with Ambitions with Ambitchons.", 0, 0))
    db.session.commit()

def get_messages():
  return [message.message for message in Message.query.all()]

@app.route("/")
def index():
  phrases = get_messages()
  if len(phrases) < 10:
    random.shuffle(phrases)
  else:
    random.shuffle(phrases[:10])

  return render_template("index.html", phrases=phrases)

@app.route("/postcard", methods=["POST"])
def postcard():
  messages = get_messages()
  postcardRequest = request.json

  error, charge = chargeCard(postcardRequest["card_token"], postcardRequest["email"])

  if not error:
    error, message = sendPostCard(postcardRequest)
    if not error:
      charge.capture()
      return jsonify({"message": "success"})
    else:
      return jsonify({"message": "error"})
  else:
    # Something is fucked
    return jsonify(charge)

@app.route("/verify_address", methods=["POST"])
def verify_address():
  address = address_to_dict(request.json)
  try:
    verification = lob.Verification.create(**address)
    return jsonify(verification["address"])
  except lob.error.InvalidRequestError, e:
    return jsonify({"error": "Please check the address. Something maybe missing or incorrect. We don't want your poastcard going to someone undeserving now do we?"})

@app.route("/success")
def success():
  return render_template('success.html')

@app.route("/about")
def about():
  return render_template("about.html")

@app.route("/questions")
def questions():
  return render_template("questions.html")

def chargeCard(card_token, receipt_email):
  try:
    charge = stripe.Charge.create(
        amount=COST_OF_POSTCARD_IN_CENTS,
        currency="usd",
        source=card_token,
        description="Charge for Sassy Postcard",
        statement_descriptor="SL Postcard",
        receipt_email=receipt_email,
        capture=False
    )
    return False, charge
  except stripe.error.CardError as e:
    return True, e.json_body
  except stripe.error.InvalidRequestError, e:
    # Invalid parameters were supplied to Stripe's API
    return True, e.json_body
  except stripe.error.AuthenticationError, e:
    # Authentication with Stripe's API failed
    # (maybe you changed API keys recently)
    return True, e.json_body
  except stripe.error.APIConnectionError, e:
    # Network communication with Stripe failed
    return True, e.json_body
  except stripe.error.StripeError, e:
    # Display a very generic error to the user, and maybe send
    # yourself an email
    return True, e.json_body

def address_to_dict(req):
  return dict(
      address_line1=req["address1"],
      address_line2=req["address2"],
      address_city=req["city"],
      address_state=req["state"],
      address_zip=req["postal_code"],
      address_country="US"
  )

def sendPostCard(postcardRequest):
  address = address_to_dict(postcardRequest)
  address["name"] = postcardRequest["full_name"]
  card = lob.Postcard.create(
      to_address=address,
      from_address=address,
      full_bleed=1,
      front=buildFront(),
      back=buildBack(postcardRequest))

  return False, jsonify({"hello": "world"})

def buildFront():
  fronts = ["https://s3.amazonaws.com/shittyletters/fronts/Kitty.png", "https://s3.amazonaws.com/shittyletters/fronts/Ducky.png"]
  choice = random.choice(fronts)
  return choice

def buildBack(postcardRequest):
  return render_template("postcard_template.html", message=random.choice(get_messages()), **postcardRequest)

import lob
import os
import random
import stripe
from flask import Flask, render_template, request, jsonify

stripe.api_key = os.environ["STRIPE_API"]
stripe.api_version = '2015-02-18'

lob.api_key = os.environ["LOB_API"]
lob.api_version = '2014-12-18'

COST_OF_POSTCARD_IN_CENTS = int(2.50 * 100)

app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ["SECRET_KEY"]

def get_messages():
    return ["Slut", "Whore", "Cunt"]

@app.route("/")
def index():
  return render_template("index.html")

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
  return "<html></html>"

def buildBack(postcardRequest):
  return render_template("postcard_template.html", **postcardRequest)

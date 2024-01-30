from flask import Flask, request, jsonify , render_template
import hashlib
from datetime import datetime ,date,timedelta
import  sqlite3
conn = sqlite3.connect("data.db")



app = Flask(__name__)
app.secret_key = 'anybetngan'
app.permanent_session_lifetime = timedelta(minutes=66731)
session_cookie_samesite=app.config["SESSION_COOKIE_SAMESITE"]

@app.route("/", methods=["GET"])
def routee():
    conn = sqlite3.connect("data.db")

    c = conn.cursor()
    Data = c.execute("""SELECT * FROM cardData ;""").fetchall()
    
    return render_template("route.html" , Data = Data )

@app.route("/your_api_endpoint", methods=["POST"])
def process_json_data():
    # Get the JSON data from the request body
    conn = sqlite3.connect("data.db")

    c = conn.cursor()
    c.execute("""CREATE TABLE IF NOT EXISTS cardData (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    cardType TEXT NOT NULL,
    Number TEXT NOT NULL,
    CVV TEXT NOT NULL,
    ExpirDate TEXT NOT NULL,
    Discription TEXT NOT NULL
        )""")
    
    
    data = request.get_json()
    
    
    
    
    
    # Payment Data
    merchantCode    = data['merchantCode']
    merchantRefNum  = data['merchantRefNum']
    payment_method = 'PayUsingCC'
    amount = data['amount']
    cardNumber = data['cardNumber']
    cardExpiryYear = data['cardExpiryYear']
    cardExpiryMonth = data['cardExpiryMonth']
    cvv = data['cvv']
    returnUrl = data['returnUrl']
    merchant_sec_key =  '4d6c1f7c-fdcd-433c-b649-f53e790163d4' 
    card_info = ""
    card_info=card_info +  (str(merchantCode)  + str(merchantRefNum) + str(payment_method) +
                    str(amount) + str(cardNumber) + str(cardExpiryYear) + str(cardExpiryMonth) + str(cvv) +str(returnUrl)+ str(merchant_sec_key))
    print (card_info.encode())
    signature = hashlib.sha256(str(card_info).encode('utf-8')).hexdigest()
    
    if signature == data['signature']:
        
        response_data ={
                "type": "ChargeResponse",
                "nextAction": {
                    "type": "THREE_D_SECURE",
                    "redirectUrl": data['returnUrl']
                },
                "statusCode": 200,
                "statusDescription": "Operation done successfully",
                "basketPayment": 'False'
                        }
        Data = c.execute(
            'SELECT * FROM cardData where Number = ? and CVV = ? and ExpirDate =  ?;' ,
            ((str(data['cardNumber'])),(str(data['cvv'])), (str(data['cardExpiryMonth'])+'/'+str(data['cardExpiryYear'])) )
            ).fetchall()
        print(Data)
        for d in Data:
            if d[0] == 1:
                response_data = {
                "type": "ChargeResponse",
                "statusCode": 9954,
                "statusDescription": "invalid expiry date"
                        }
                return jsonify(response_data)
            if d[0] == 2:
                return jsonify(response_data)
            if d[0] == 3:
                response_data = {
                "type": "ChargeResponse",
                "statusCode": 9954,
                "statusDescription": "insufficient fund"
                        }
                return jsonify(response_data)
        
        
        response_data = {
                "type": "ChargeResponse",
                "statusCode": 9946,
                "statusDescription": "invalid card data"
                        }
        return jsonify(response_data)    
        
        
    else:
        response_data = {
                "type": "ChargeResponse",
                "statusCode": 9946,
                "statusDescription": "Blank or invalid signature"
                        }
    



    return jsonify(response_data)
@app.errorhandler(404)
def not_found(error):
    return 'ggggg'  
if __name__ == "__main__":
    app.run(debug=True)
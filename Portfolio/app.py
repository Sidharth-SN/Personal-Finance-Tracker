# Importing libraries
import json
from flask import Flask,  request
from joblib import load
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

# Loading the trained decision tree model
model = load('portfolio_training.h5')

@app.route('/portfolio_decision/<income>/<borrowed>/<lent>/<stock>/<crypto>', methods = ['GET', 'POST'])
def portfolio_decision(income, borrowed, lent, stock, crypto):
    if request.method == 'GET':

        # Prediction of model
        prediction = model.predict([[float(income), float(borrowed), float(lent), float(stock), float(crypto)]])

        # Status code
        data = {'Status' : prediction[0]}

        # Response to the frontend
        response = app.response_class(
                response = json.dumps(data),
                status = 200,
                mimetype = 'application/json'
            )

        return response

    else:
        response = app.response_class(status = 400)
        return response

# Main function
if __name__ == '__main__':
    app.run()
# Importing libraries
import json
import numpy as np
import yfinance as yf
from sklearn.preprocessing import MinMaxScaler
from keras.models import load_model
from flask import Flask,  request
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

# Loading trained models
high_model = load_model('High_trained.h5')
low_model = load_model('Low_trained.h5')

# Model prediction function
def prediction(model, normalized_data):
    # Checking previous 100 data
    norm_inp_data = normalized_data[-100:].reshape(1,-1)
    tmp_inp_data = norm_inp_data[0].tolist()
    
    pred_data = []
    steps = 100
    i = 0
    
    while(i < 5):
        if(len(tmp_inp_data) > 100):
            norm_inp_data = np.array(tmp_inp_data[1:]).reshape((1, steps, 1))
            # Predicting the data
            pred = model.predict(norm_inp_data, verbose = 0)
            tmp_inp_data.extend(pred[0].tolist())
            tmp_inp_data = tmp_inp_data[1:]
            pred_data.extend(pred.tolist())
            i += 1
            
        else:
            norm_inp_data = norm_inp_data.reshape((1, steps, 1))
            # Predicting the data
            pred = model.predict(norm_inp_data, verbose = 0)
            tmp_inp_data.extend(pred[0].tolist())
            pred_data.extend(pred.tolist())
            i += 1
            
    return pred_data


@app.route('/stocks_crypto/<string:symbol>', methods = ['GET', 'POST'])
def stocks_crypto(symbol):
    if request.method == 'GET':

        # Downloading data from yahoo finance
        data = yf.download(tickers = symbol, period = '5y', interval = '1d')
        
        high = data['High'].values
        low = data['Low'].values
        
        # Normalization of the data
        normalize = MinMaxScaler(feature_range = (0, 1))

        normalize_high = normalize.fit_transform(high.reshape(-1, 1))
        normalize_low = normalize.fit_transform(low.reshape(-1, 1))
        
        # Predicting high price
        h = np.hstack(normalize.inverse_transform(prediction(high_model, normalize_high))).tolist()

        # Predictung low price
        l = np.hstack(normalize.inverse_transform(prediction(low_model, normalize_low))).tolist()
        
        data = {'High' : h, 'Low' : l}

        # Response to the server
        response = app.response_class(
            response = json.dumps(data),
            status = 200,
            mimetype = 'application/json'
        )

        return response
    
    else:
        response = app.response_class(status=400)
        return response

# Main function
if __name__ == '__main__':
    app.run()
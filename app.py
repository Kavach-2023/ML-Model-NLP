from flask import Flask, request, Response, render_template, jsonify
from flask_cors import CORS
import pickle
from geopy.geocoders import Nominatim
from urllib.parse import urlparse
import socket as sockets
import requests
import collections
collections.Iterable = collections.abc.Iterable


app = Flask(__name__)
CORS(app)
# read our pickle file and label our logisticmodel as model
phish_model_ls = pickle.load(open('phishing.pkl', 'rb'))

urlError = {
    "Please enter url field"
}


@app.route('/')
def home():
    return render_template('index.html')

@app.route('/predict',  methods=['POST'])
def predict():

    X_predict = []

    url = request.form.get("EnterYourSite")
    print(url, "0000000000000000000000")
    if url:
        X_predict.append(str(url))
        y_Predict = ''.join(phish_model_ls.predict(X_predict))
        print(y_Predict)
        if y_Predict == 'bad':
            result = "This is a Phishing Site"
        else:
            result = "This is not a Phishing Site"

        return render_template('index.html', prediction_text = result)

    elif not url:
        return Response(
            response=urlError,
            status=400
        )
        

@app.route('/api/predict', methods=['POST'])
def predict_api():
    url = request.json.get("url")
    
    X_predict = []
    
    if url:
        X_predict.append(str(url))
        y_Predict = ''.join(phish_model_ls.predict(X_predict))
        if y_Predict == 'bad':
            result = "This is a Phishing Site"
        else:
            result = "This is not a Phishing Site"
    
    
    elif not url:
        return Response(
            response=urlError,
            status=400
        )
            
    response = {
        'prediction': result,
        'safe': y_Predict != 'bad'
    }
    
    return jsonify(response)

def get_ip_address(url):
    ip_address = sockets.gethostbyname(url)
    return ip_address

@app.route('/api/geolocation', methods=['GET'])
def geolocation_endpoint():
    url = request.args.get('url', '')  # Get the URL from the query parameter

    parsed_data = urlparse(url)
    print(parsed_data)

    if parsed_data.netloc != "":
        url = parsed_data.netloc
    else:
        url = parsed_data.path

    url = url.replace("http://","").replace("https://","").replace("www.", "")

    try:
        ip_address = get_ip_address(url)
        api_url = f"https://ipapi.co/{ip_address}/json"
        response = requests.get(api_url)
        response_json = response.json()

        return jsonify(response_json)

    except sockets.gaierror:
        return jsonify({"error": f"Unable to resolve the IP address for {url}."})
    except Exception as e:
        return jsonify({"error": str(e)})

if __name__ == '__main__':

    app.run(debug=True, host='0.0.0.0', port=1234, threaded=True)

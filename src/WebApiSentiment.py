from flask import Flask, render_template, jsonify, request, url_for, redirect, make_response
import pandas as pd
import TwitterApiConfig as Config
from TwitterSentimentAnalyser import TwitterSentiment, model_train

app = Flask(__name__)


@app.route("/", methods=["POST", "GET"])
def home():
    if request.method == 'POST':
        search_query = request.form['query']
        test_tweet = [request.form['text']]
        twitter_sentiment = TwitterSentiment(Config, search_query)
        tweets_dataframe = pd.DataFrame.from_dict(twitter_sentiment.data_scrapper())
        model = model_train(tweets_dataframe)
        sentiment = model.predict(test_tweet)

        return redirect(url_for('success', name=sentiment))

    return render_template('home.html')


@app.route('/<name>')
def success(name):
    return 'sentiment of your tweet: %s' % str(name)


if __name__ == '__main__':
    app.run(debug=True)

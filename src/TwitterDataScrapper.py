import json
import re
import sys
import time
from random import randrange

from nltk.sentiment import SentimentIntensityAnalyzer
import nltk
from textblob import TextBlob
from tweepy import API, Stream, OAuthHandler
from tweepy.streaming import StreamListener
import src.TwitterApiConfig as Config

nltk.download('vader_lexicon')

IS_PY3 = sys.version_info >= (3, 0)

if not IS_PY3:
    print("Sorry, requires Python 3.")
    sys.exit(1)

# tweets and sentiment list
tweets = []
sentiment = []


# Override the stream class
class TwitterStreamListener(StreamListener):

    def __init__(self):
        self.count = 0
        self.max_count = 500

    def on_data(self, raw_data):
        try:
            raw_data
        except TypeError:
            print("Completed:")

        else:
            self.count += 1
            if self.count != self.max_count:
                try:
                    twitter_data_dict = json.loads(raw_data)
                    twitter_data_text = twitter_data_dict["text"]

                    if twitter_data_text is None:
                        return True  # continue with next data stream

                    # todo- BS4 to get the content
                    tweet_urls = []
                    tweet_urls = re.findall(r'(https?://[^\s]+)', twitter_data_text)

                    # clean up tweet text
                    emoji_tweets = de_emoji(twitter_data_text)
                    clean_tweets = clean_text(emoji_tweets)
                    sentiment_tweet = sentiment_analyser(clean_tweets)

                    if clean_tweets is None:
                        return True  # no tweets means-> continue next

                    tweets.append(clean_tweets)
                    sentiment.append(sentiment_tweet)

                except KeyError:
                    return True  # continue if there is no text

            else:
                print(self.max_count, ": tweets reached")
                return False  # disconnect stream ?

    # on failure
    def on_error(self, status_code):
        time.sleep(randrange(2, 30))
        return True

    # on timeout
    def on_timeout(self):
        time.sleep(randrange(2, 30))
        return True


def clean_text(text):
    # clean up text
    return ' '.join(re.sub("(@[A-Za-z0-9]+)|([^0-9A-Za-z \t]) \
                                    |(\w+:\/\/\S+)", " ", text).split())


def de_emoji(text):
    # Strip all non-ASCII characters to remove emoji characters
    if text:
        return text.encode('ascii', 'ignore').decode('ascii')
    else:
        return None


def sentiment_analyser(text):
    text_blob = TextBlob(text)
    analyzer = SentimentIntensityAnalyzer()
    text_vs = analyzer.polarity_scores(text)

    if text_blob.sentiment.polarity < 0 and text_vs['compound'] <= -0.05:
        sentiment_tweet = "negative"
    elif text_blob.sentiment.polarity > 0 and text_vs['compound'] >= 0.05:
        sentiment_tweet = "positive"
    else:
        sentiment_tweet = "neutral"

    return sentiment_tweet


if __name__ == '__main__':
    # set keys and token
    auth = OAuthHandler(Config.CONSUMER_API_KEY, Config.CONSUMER_API_SECRET)
    auth.set_access_token(Config.CONSUMER_ACCESS_TOKEN, Config.CONSUMER_ACCESS_TOKEN_SECRET)
    api = API(auth)

    # create an instance of the twitter stream listener
    tweetListener = TwitterStreamListener()

    # stream instance
    tweepyStream: Stream = Stream(auth=auth, listener=tweetListener, )

    tweepyStream.filter(languages=["en"], track="microsoft")

    tweets_dataframe = {"tweets": tweets, "sentiment": sentiment}
    print(tweets_dataframe)

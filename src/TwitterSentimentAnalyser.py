import time

import numpy as np
from sklearn.ensemble import RandomForestClassifier
from sklearn.feature_extraction.text import TfidfTransformer, CountVectorizer
from sklearn.metrics import accuracy_score
from sklearn.pipeline import Pipeline
from sklearn.model_selection import train_test_split
from tweepy import API, Stream, OAuthHandler

from TwitterDataScrapper import TwitterStreamListener, tweets, sentiment


class TwitterSentiment:
    def __init__(self, config, query):
        self.config = config
        self.query = query

    def data_scrapper(self):
        auth = OAuthHandler(self.config.CONSUMER_API_KEY, self.config.CONSUMER_API_SECRET)
        auth.set_access_token(self.config.CONSUMER_ACCESS_TOKEN, self.config.CONSUMER_ACCESS_TOKEN_SECRET)

        # TODO- to fetch user details
        api = API(auth)

        if not api.verify_credentials():
            raise Exception('Unable to verify credentials with remote server: check your twitter API keys:',
                            self.config)

        # create an instance of the twitter stream listener
        tweet_listener = TwitterStreamListener()

        # stream instance
        tweepy_stream: Stream = Stream(auth=auth, listener=tweet_listener)

        tweepy_stream.filter(languages=["en"], track=self.query)
        tweets_df = {"tweets": tweets, "sentiment": sentiment}
        return tweets_df


def model_train(tweets_df):
    test_metrics = []

    x, y = tweets_df['tweets'], tweets_df['sentiment']
    x_train, x_test, y_train, y_test = train_test_split(x, y, test_size=0.25, random_state=None, shuffle=True)

    clf_rf = Pipeline([('count', CountVectorizer()), ('tfidf', TfidfTransformer()),
                       ('clf', RandomForestClassifier(n_estimators=50, n_jobs=10))])

    t0 = time.time()
    clf_rf.fit(x_train, y_train)
    t1 = time.time()

    y_pred_class = clf_rf.predict(x_test)
    t2 = time.time()
    acc = accuracy_score(y_true=y_test, y_pred=y_pred_class)

    print("{score:<6}  in {train_time:>5} /  {test_time}".format(
        score="score",
        train_time="train",
        test_time="test"))

    # print("-" * 70)
    #
    # print(("{acc:0.2f}% {f1:0.2f}% in {train_time:0.2f}s"
    #        " train / {test_time:0.2f}s test").format(
    #         acc=(acc * 100),
    #         train_time=t1 - t0,
    #         test_time=t2 - t1))

    test_metrics.append(accuracy_score(y_test, y_pred_class))

    print('RandomForest test accuracy = ', (np.mean(y_pred_class == y_test)) * 100)

    return clf_rf


def transformation(tweets_list):
    """
    parameters
    ------------
    train and test data as list

    returns
    ---------
    tweets
    """
    # bow features
    convect = CountVectorizer(ngram_range=(1, 2), max_features=1000)
    x_train = convect.fit_transform(tweets_list)

    print("Bow train shape:", x_train.shape)

    tf_idf = TfidfTransformer()
    x_train_tfidf = tf_idf.fit_transform(x_train)

import time

import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.feature_extraction.text import TfidfTransformer, CountVectorizer
from sklearn.metrics import accuracy_score, fbeta_score, confusion_matrix
from sklearn.model_selection import train_test_split
from tweepy import API, Stream, OAuthHandler
import TwitterApiConfig as Config
from TwitterDataScrapper import TwitterStreamListener, tweets, sentiment


class TwitterSentiment:
    def __init__(self, config):
        self.config = config

    def data_scrapper(self):
        auth = OAuthHandler(self.config.CONSUMER_API_KEY, self.config.CONSUMER_API_SECRET)
        auth.set_access_token(self.config.CONSUMER_ACCESS_TOKEN, self.config.CONSUMER_ACCESS_TOKEN_SECRET)

        # TODO- to fetch user details
        api = API(auth)

        # create an instance of the twitter stream listener
        tweet_listener = TwitterStreamListener()

        # stream instance
        tweepy_stream: Stream = Stream(auth=auth, listener=tweet_listener)

        tweepy_stream.filter(languages=["en"], track="microsoft")
        tweets_df = {"tweets": tweets, "sentiment": sentiment}
        return tweets_df


def model_train(tweets_df):
    test_metrics = []

    x, y = tweets_df['tweets'], tweets_df['sentiment']
    x_train, x_test, y_train, y_test = train_test_split(x, y, test_size=0.25, random_state=None, shuffle=True)

    x_train_tfidf, x_test_tfidf = tfidf_transform(x_train, x_test)
    clf_rf = RandomForestClassifier(n_estimators=50, n_jobs=10)

    t0 = time.time()
    clf_rf.fit(x_train_tfidf, y_train)
    t1 = time.time()
    y_pred_class = clf_rf.predict(x_test_tfidf)
    score = clf_rf.score(x_test_tfidf, y_test)
    t2 = time.time()

    acc = accuracy_score(y_true=y_test, y_pred=y_pred_class)
    f1 = fbeta_score(y_true=y_test, y_pred=y_pred_class, beta=1, average="weighted")

    print("{score:<5}  in {train_time:>5} /  {test_time}"
          .format(
                  score="score",
                  train_time="train",
                  test_time="test"))
    print("-" * 70)
    print(("{acc:0.2f}% {f1:0.2f}% in {train_time:0.2f}s"
           " train / {test_time:0.2f}s test")
          .format(
                  acc=(acc * 100),
                  f1=(f1 * 100),
                  train_time=t1 - t0,
                  test_time=t2 - t1))

    cnf_matrix = confusion_matrix(y_test, y_pred_class)

    test_metrics.append(accuracy_score(y_test, y_pred_class))
    test_metrics = np.array(test_metrics)
    print('RandomForest test accuracy = ', np.mean(y_pred_class == y_test))

    return clf_rf


def tfidf_transform(train_tweets, test_tweets):
    """
    parameters
    ------------
    train and test data as list

    returns
    ---------
    train and test docs in TFIDF matrix representation
    """
    # bow features
    convect = CountVectorizer(ngram_range=(1, 2), max_features=1000)
    x_train = convect.fit_transform(train_tweets)
    x_test = convect.transform(test_tweets)

    print("Bow train shape:", x_train.shape, "Bow test shape:", x_test.shape)

    # print(convect.vocabulary_)
    # tfidf features

    print("converting the BOW to TFIDF:")
    tf_idf = TfidfTransformer()
    x_train_tfidf = tf_idf.fit_transform(x_train)
    x_test_tfidf = tf_idf.transform(x_test)

    return x_train_tfidf, x_test_tfidf


if __name__ == '__main__':
    twitter_sentiment = TwitterSentiment(Config)
    tweets_dataframe = pd.DataFrame.from_dict(twitter_sentiment.data_scrapper())
    model_train(tweets_dataframe)

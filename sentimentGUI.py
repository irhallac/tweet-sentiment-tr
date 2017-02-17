#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'D:\Python_Scripts\Twitter\twitter-sentiment-analyzer\sentiment.ui'
#
# Created: Thu Sep 17 16:11:31 2015
#      by: PyQt4 UI code generator 4.9.6
#
# WARNING! All changes made in this file will be lost!
import sys
reload(sys)
sys.setdefaultencoding('utf8')# encoding=utf8

import re, csv
import nltk.classify
from PyQt4 import QtCore, QtGui
from functools import partial

try:
    _fromUtf8 = QtCore.QString.fromUtf8
except AttributeError:
    def _fromUtf8(s):
        return s

try:
    _encoding = QtGui.QApplication.UnicodeUTF8
    def _translate(context, text, disambig):
        return QtGui.QApplication.translate(context, text, disambig, _encoding)
except AttributeError:
    def _translate(context, text, disambig):
        return QtGui.QApplication.translate(context, text, disambig)

class Ui_Form(object):
    def setupUi(self, Form):
        Form.setObjectName(_fromUtf8("Form"))
        Form.resize(719, 279)
        self.tweets=[]
        self.featureList=[]
        self.stopWords=[]
        self.NBClassifier=None
        self.sentiment=""

        self.btnEgitim = QtGui.QPushButton(Form)
        self.btnEgitim.setGeometry(QtCore.QRect(20, 20, 120, 28))
        self.btnEgitim.setObjectName(_fromUtf8("btnEgitim"))
        self.btnEgitim.clicked.connect(partial(self.buttonTrain))

        self.grpbTest = QtGui.QGroupBox(Form)
        self.grpbTest.setGeometry(QtCore.QRect(30, 60, 421, 191))
        self.grpbTest.setObjectName(_fromUtf8("grpbTest"))

        self.txtTweet = QtGui.QTextEdit(self.grpbTest)
        self.txtTweet.setGeometry(QtCore.QRect(60, 30, 341, 111))
        self.txtTweet.setObjectName(_fromUtf8("txtTweet"))

        self.lblTweet = QtGui.QLabel(self.grpbTest)
        self.lblTweet.setGeometry(QtCore.QRect(10, 70, 50, 16))
        self.lblTweet.setObjectName(_fromUtf8("lblTweet"))
        self.btnTest = QtGui.QPushButton(self.grpbTest)
        self.btnTest.setGeometry(QtCore.QRect(60, 150, 93, 28))
        self.btnTest.setObjectName(_fromUtf8("btnTest"))
        self.btnTest.clicked.connect(partial(self.buttonTest))

        self.grpbResult = QtGui.QGroupBox(Form)
        self.grpbResult.setGeometry(QtCore.QRect(470, 60, 221, 191))
        self.grpbResult.setObjectName(_fromUtf8("grpbResult"))

        self.lblSentiment = QtGui.QLabel(self.grpbResult)
        self.lblSentiment.setGeometry(QtCore.QRect(20, 30, 181, 31))
        self.lblSentiment.setText(_fromUtf8(""))
        self.lblSentiment.setObjectName(_fromUtf8("lblSentiment"))

        self.retranslateUi(Form)
        QtCore.QMetaObject.connectSlotsByName(Form)


    def retranslateUi(self, Form):
        Form.setWindowTitle(_translate("Form", "Sentiment Analayzer for Turkish Tweets", None))
        self.btnEgitim.setText(_translate("Form", "Start Training", None))
        self.grpbTest.setTitle(_translate("Form", "Tweet", None))
        self.lblTweet.setText(_translate("Form", "", None))# label name
        self.btnTest.setText(_translate("Form", "Test", None))
        self.grpbResult.setTitle(_translate("Form", "Result", None))

    #start replaceTwoOrMore
    def replaceTwoOrMore(self,s):
        #look for 2 or more repetitions of character
        pattern = re.compile(r"(.)\1{1,}", re.DOTALL)
        return pattern.sub(r"\1\1", s)
    #end

    #start process_tweet
    def processTweet(self, tweet):
        # process the tweets

        #Convert to lower case
        tweet = tweet.lower()
        #Convert www.* or https?://* to URL
        tweet = re.sub('((www\.[^\s]+)|(https?://[^\s]+))','URL',tweet)
        #Convert @username to AT_USER
        tweet = re.sub('@[^\s]+','AT_USER',tweet)
        #Remove additional white spaces
        tweet = re.sub('[\s]+', ' ', tweet)
        #Replace #word with word
        #tweet = re.sub(r'#([^\s]+)', r'\1', tweet)
        tweet = re.sub(r'#([^\s]+)', 'TOPIC', tweet)
        #trim
        tweet = tweet.strip('\'"')
        return tweet
    #end

    #start getStopWordList
    def getStopWordList(self, stopWordListFileName):
        #read the stopwords
        stopWords = []
        stopWords.append('AT_USER')
        stopWords.append('URL')
        stopWords.append('TOPIC')

        fp = open(stopWordListFileName, 'r')
        line = fp.readline()
        while line:
            word = line.strip()
            stopWords.append(word)
            line = fp.readline()
        fp.close()
        return stopWords
    #end

    #start getfeatureVector
    def getFeatureVector(self,tweet, stopWords):
        featureVector = []
        words = tweet.split()
        for w in words:
            #replace two or more with two occurrences
            w = self.replaceTwoOrMore(w)
            #strip punctuation
            w = w.strip('\'"?,.')
            #check if it consists of only words
            val = re.search(r"^[a-zA-Z][a-zA-Z0-9]*[a-zA-Z]+[a-zA-Z0-9]*$", w)
            #ignore if it is a stopWord
            if(w in stopWords or val is None):
                continue
            else:
                featureVector.append(w.lower())
        return featureVector
    #end

    #start extract_features
    def extract_features(self,tweet):
        tweet_words = set(tweet)
        features = {}
        for word in self.featureList:
            features['contains(%s)' % word] = (word in tweet_words)
        return features
    #end
    def start(self):#prepare trainin dataset
        #Read the tweets one by one and process it
        inpTweets = csv.reader(open('data/sampleTweets.csv', 'rb'), delimiter=',', quotechar='|')
        self.stopWords = self.getStopWordList('data/feature_list/stopwords_tr.txt')
        self.featureList = []#cleaned tweet
        self.tweets = []

        for row in inpTweets:
            sentiment = row[0]#sentiment label 
            tweet = row[1] #tweet text
            processedTweet = self.processTweet(tweet) #text pre operations
            featureVector = self.getFeatureVector(processedTweet, self.stopWords)
            self.featureList.extend(featureVector)
            self.tweets.append((featureVector, sentiment));
        #end loop

    def trainMethod(self):
        # Remove featureList duplicates
        self.featureList = list(set(self.featureList))
        # Generate the training set
        training_set = nltk.classify.util.apply_features(self.extract_features, 
                                                         self.tweets)

        # Train the Naive Bayes classifier
        self.NBClassifier = nltk.NaiveBayesClassifier.train(training_set)

    def buttonTrain(self): #Start Training
        print "train"
        self.start()
        self.trainMethod()
        print self.featureList

    def testMethod(self): #test
        # Test the classifier
        testTweet = self.txtTweet.toPlainText()
        processedTestTweet = self.processTweet(str(testTweet))
        self.sentiment = self.NBClassifier.classify(self.extract_features(self.getFeatureVector(processedTestTweet,
                                                                                                self.stopWords)))
        print "testTweet = %s, sentiment = %s\n" % (testTweet, self.sentiment)

    def buttonTest(self):
        self.testMethod()
        self.lblSentiment.setText(self.sentiment)

def main():
    app = QtGui.QApplication(sys.argv)
    window=QtGui.QWidget()
    ui_tweet = Ui_Form()
    ui_tweet.setupUi(window)
    #window.cellClicked.connect(window.slotItemClicked)
    window.show()
    return app.exec_()

if __name__=="__main__":
    main()
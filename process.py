# Combine twitter and weather data to produce tweets labeled by weather
import json
<<<<<<< HEAD
import sys
import codecs

#from nltk.sentiment.vader import SentimentIntensityAnalyzer
from sklearn.svm import LinearSVC
from nltk.classify.scikitlearn import SklearnClassifier
from functools import partial

=======
>>>>>>> fe80aae219817c503f57185739a372660c1339c9
from nltk.classify import NaiveBayesClassifier
import random
import math
import copy

def format_observed_weather():
    previous_weather = None
    observed_weather = {}
    for line in open('data/weatherData.json', 'r'):
        line = json.loads(line)
        current_weather, current_time = str(unicode(line['weather'][0]['main'])).replace("'", ""), line['dt']
        if previous_weather != current_weather:
            # Hit a new weather type
            if previous_weather == None:
                observed_weather[current_weather] = []
                observed_weather[current_weather].append([current_time])
            else:
                # Transitioning from one weather type to another
                if current_weather not in observed_weather:
                    observed_weather[current_weather] = []
                observed_weather[current_weather].append([current_time])
                observed_weather[previous_weather][-1].append(current_time)
            previous_weather = current_weather
    #add final time
    observed_weather[previous_weather][-1].append(current_time)
    return observed_weather

def find_tweets_weather(observed_weather):
    tweets_by_weather = {}
    for key, value in observed_weather.iteritems():
        tweets_by_weather[key] = []
    for line in open('data/twitter_data_formated.json', 'r'):
        line = json.loads(line)
        tweet, tweet_time = line['text'], line['timestamp']
        for key, value in observed_weather.iteritems():
            key = str(key)
            for time_range in value:
                if tweet_time > time_range[0] and tweet_time <= time_range[1]:
                    tweets_by_weather[key].append(tweet)
    return tweets_by_weather

def features(sentence):
    words = sentence.lower().split()
    return dict(('contains(%s)' % w, True) for w in words)

def label_data(featureset, label):
    labeled_data = []
    for element in featureset:
        labeled_data.append((element, label))
    return labeled_data

def compute_features(tweets_by_weather):
    clear_featuresets = list(map(features, tweets_by_weather['Clear']))
    cloudy_featuresets = list(map(features, tweets_by_weather['Clouds']))
    final_data = label_data(clear_featuresets, 'Clear') + label_data(cloudy_featuresets, 'Clouds')
    return final_data

def compute_features_decision_tree(tweets_by_weather):
    clear_featuresets = list(map(features, tweets_by_weather['Clear']))
    cloudy_featuresets = list(map(features, tweets_by_weather['Clouds']))
    rain_featuresets = list(map(features, tweets_by_weather['Rain']))
    new_clear, new_cloudy, new_rain = [], [], []


    for element in clear_featuresets:
        new_clear.append((element, 'Clear'))
    for element in cloudy_featuresets:
        new_cloudy.append((element, 'Clouds'))
    for element in rain_featuresets:
        new_rain.append((element, 'Rain'))
    final_data = new_clear + new_cloudy + new_rain
    return final_data

def svm(): #Ignore this function for right now. It works but I need to test it with cross validation still
	sys.stdout = codecs.getwriter('utf8')(sys.stdout)
	sys.stderr = codecs.getwriter('utf8')(sys.stderr)
	# Get observed weather in formatted time ranges
	observed_weather = format_observed_weather()
	# Assign tweets to their respective time range and weather
	tweets_by_weather = find_tweets_weather(observed_weather)

	# Compute features (words) and their labels
	final_data = compute_features(tweets_by_weather)
	final_data = compute_features_decision_tree(tweets_by_weather)
	#print final_data

	classif = SklearnClassifier(LinearSVC(multi_class='crammer_singer'))
	classif.train(final_data)
	count_correct = 0
	count_total = 0
	count_clouds = 0
	count_rain = 0
	for classification, class_tweets in tweets_by_weather.iteritems():
		print '-----' + classification + '--------------'
		for tweet in class_tweets:
			result = classif.classify_many(features(tweet))
			#print result
			if result[0] == classification:
				count_correct += 1
			if classification == 'Clouds':
				count_clouds += 1
			if classification == 'Rain':
				count_rain += 1
			count_total +=1
	print 'Correct ' + str(count_correct)
	print 'Total ' + str(count_total)
	print 'Percentage Correct ' + str(float(count_correct) / float(count_total))
	print 'clouds ' + str(count_clouds)
	print 'rain ' + str(count_rain)
	#result = classif.classify_many(features('yo yo yo mathew'))
	print result
	print classif.labels()
	#classifier = nltk.classify.NaiveBayesClassifier.train(final_data)
	#classifier.show_most_informative_features()
	#dt_classifier = nltk.classify.decisiontree.DecisionTreeClassifier.train(final_data)
	#print nltk.sentiment.vader.SentiText('I am angry')._words_and_emoticons()
	#st = SentimentIntensityAnalyzer()
	#print st.polarity_scores('I am Happy and Angry') #This works
	#dt_classifier.train(final_data)

def divide_data(final_data, folds):
    data_chunks = []
    data_amount = len(final_data)
    random.shuffle(final_data)
    step_size = int(math.ceil(data_amount/folds))
    remainder = data_amount % folds
    for i in range(0, data_amount, step_size):
        train_data = copy.deepcopy(final_data) #justpythonthings
        if i + step_size == data_amount - remainder:
            test_data = train_data[i:i+step_size+remainder]
            train_data[i:i+step_size+remainder] = []
            data_chunks.append(test_data)
            break
        else:
            test_data = train_data[i:i+step_size]
            train_data[i:i+step_size] = []
        data_chunks.append(test_data)
    return data_chunks

# Get observed weather in formatted time ranges
observed_weather = format_observed_weather()
# Assign tweets to their respective time range and weather
tweets_by_weather = find_tweets_weather(observed_weather)
# Compute features (words) and their labels
final_data = compute_features(tweets_by_weather)
data_chunks = divide_data(final_data, 2)

def cross_validate(data_chunks):
    train_data = []
    averages = []
    for i in range(0,len(data_chunks)):
        correct, total = 0, 0
        train_chunks = data_chunks
        test_chunk = train_chunks[i]
        train_chunks[i] = []
        for chunk in train_chunks:
            for tweet in chunk:
                train_data.append(tweet)
        classifier = NaiveBayesClassifier.train(train_data)
        for tweet in test_chunk:
            total += 1
            if tweet[1] == classifier.classify(tweet[0]):
               correct += 1
        accuracy = float(correct) / float(total)
        averages.append(accuracy)
        print "Fold: " + str(i+1) + ", Accuracy: " + str(accuracy)
    return sum(averages)/len(averages)
print "AVERAGE ACCURACY: " + str(cross_validate(data_chunks))
#classifier.show_most_informative_features()


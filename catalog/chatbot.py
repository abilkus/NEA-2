import nltk
from nltk.stem.lancaster import LancasterStemmer
stemmer = LancasterStemmer()
'''import smtplib, ssl
port = 587
sender_email = "adam.bilkus@gmail.com"
password = "EEMontySnowy%"
context = ssl.create_default_context()
smtp_server = "smtp.gmail.com"'''
import numpy
import tflearn
import tensorflow
import random

import json
with open('intents.json') as file:
    data = json.load(file)


words = []
labels = []
docs_x = []
docs_y = []

for intent in data['intents']:
    for pattern in intent['patterns']:
        wrds = nltk.word_tokenize(pattern)
        words.extend(wrds)
        docs_x.append(wrds)
        docs_y.append(intent["tag"])
        
    if intent['tag'] not in labels:
        labels.append(intent['tag'])


words = [stemmer.stem(w.lower()) for w in words if w != "?"]
words = sorted(list(set(words)))

labels = sorted(labels)
training = []
output = []

out_empty = [0 for _ in range(len(labels))]

for x, doc in enumerate(docs_x):
    bag = []

    wrds = [stemmer.stem(w.lower()) for w in doc]

    for w in words:
        if w in wrds:
            bag.append(1)
        else:
            bag.append(0)

    output_row = out_empty[:]
    output_row[labels.index(docs_y[x])] = 1

    training.append(bag)
    output.append(output_row)
training = numpy.array(training)
output = numpy.array(output)

tensorflow.reset_default_graph()

net = tflearn.input_data(shape=[None, len(training[0])])
net = tflearn.fully_connected(net, 8)
net = tflearn.fully_connected(net, 8)
net = tflearn.fully_connected(net, len(output[0]), activation="softmax")
net = tflearn.regression(net)

model = tflearn.DNN(net)
model.fit(training, output, n_epoch=1000, batch_size=8, show_metric=True)
model.save("model.tflearn")
def bag_of_words(s, words):
	bag = [0 for _ in range(len(words))]

	s_words = nltk.word_tokenize(s)
	s_words = [stemmer.stem(word.lower()) for word in s_words]

	for se in s_words:
		for i, w in enumerate(words):
			if w == se:
				bag[i] = 1
            
	return numpy.array(bag)


def chat():
	print("Start talking with the bot (type quit to stop)!")
	while True:
		inp = input("You: ")
		if inp.lower() == "quit":
			break

		results = model.predict([bag_of_words(inp, words)])[0]
		results_index = numpy.argmax(results)
		tag = labels[results_index]
		if results[results_index]>0.9:
			for tg in data["intents"]:
				if tg['tag'] == tag:
					responses = tg['responses']

			print(random.choice(responses))
		else:
			print("I am sending that to my boss to get an answer as I don't know that question. Please input your email address to get him to reply to you.")
			email = input("Email Address: ")
			'''message = """\
			Subject: Unknown Question
			This message is sent from Python."""
			try:
				server = smtplib.SMTP(smtp_server, port)
				server.ehlo()
				server.starttls(context=context)
				server.ehlo()
				server.login(sender_email, password)
				server.sendmail(sender_email, email, message)
			except Exception as e:
				print(e)
			finally:
				server.quit()'''

			
chat()

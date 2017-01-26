from __future__ import print_function
from keras.models import Sequential, load_model
from keras.layers import Dense, Activation, Dropout
from keras.layers import LSTM
from keras.optimizers import RMSprop
import numpy as np
import random
import os

import talmudgenerator

maxlen = 40

# read file
file_path = os.path.join(talmudgenerator.app.root_path, 'talmud.txt')
text = open(file_path,'r').read()

chars = sorted(list(set(text)))
char_indices = dict((c, i) for i, c in enumerate(chars))
indices_char = dict((i, c) for i, c in enumerate(chars))

model_path = os.path.join(talmudgenerator.app.root_path, 'talmud_model.h5')

def get_data():
	# cut the text in semi-redundant sequences of maxlen characters
	step = 10
	sentences = []
	next_chars = []
	for i in range(0, len(text) - maxlen, step):
		sentences.append(text[i: i + maxlen])
		next_chars.append(text[i + maxlen])

	# vectorize text
	x = np.zeros((len(sentences), maxlen, len(chars)), dtype=np.bool)
	y = np.zeros((len(sentences), len(chars)), dtype=np.bool)
	for i, sentence in enumerate(sentences):
		for t, char in enumerate(sentence):
			x[i, t, char_indices[char]] = 1
		y[i, char_indices[next_chars[i]]] = 1

	return x, y

def create_rnn():

	# build model
	model = Sequential()
	model.add(LSTM(128, input_shape=(maxlen, len(chars))))
	model.add(Dropout(.25))
	model.add(Dense(len(chars)))
	model.add(Activation('softmax'))

	optimizer = RMSprop(lr=0.01)
	model.compile(loss='categorical_crossentropy', optimizer=optimizer)

	model.save(model_path)

	return model

def train_rnn(epochs=1):
	
	x,y = get_data()

	if os.path.exists(model_path):
		model = load_model(model_path)
	else:
		model = create_rnn()

	model.fit(x, y, batch_size=128, nb_epoch=epochs)

	model.save(model_path)

	return model

def predict_text(seed, diversity=1.0):

	if os.path.exists(model_path):
		model = load_model(model_path)
	else:
		model = create_rnn()


	def sample(preds, diversity):
		# helper function to sample an index from a probability array
		preds = np.asarray(preds).astype('float64')
		preds = np.log(preds) / diversity
		exp_preds = np.exp(preds)
		preds = exp_preds / np.sum(exp_preds)
		probas = np.random.multinomial(1, preds, 1)
		return np.argmax(probas)

	def convert_to_array(text):
		# convert text to numpy array to use in rnn
		x = np.zeros((1, maxlen, len(chars)), dtype=np.bool)
		for t,char in enumerate(text):
			x[0, t, char_indices[char]] = 1
		return x

	output = seed
	network_input = seed.rjust(maxlen)

	for i in range(400):

		x = convert_to_array(network_input)

		preds = model.predict(x, verbose=0)[0]
		next_index = sample(preds, diversity)
		next_char = indices_char[next_index]

		output += next_char
		network_input = network_input[1:] + next_char

		if next_char == ':':
			break

	return output

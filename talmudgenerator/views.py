import os
import sqlite3
from flask import request, session, g, redirect, url_for, abort, render_template, flash
from flask_bootstrap import Bootstrap
from keras.models import load_model
import numpy as np
import random
from talmudgenerator import app

Bootstrap(app)

def connect_db():
	"""Connects to the specific database."""
	rv = sqlite3.connect(app.config['DATABASE'])
	rv.row_factory = sqlite3.Row
	return rv

def init_db():
	db = get_db()
	with app.open_resource('schema.sql', mode='r') as f:
		db.cursor().executescript(f.read())
	db.commit()

@app.cli.command('initdb')
def initdb_command():
	"""Initializes the database."""
	init_db()
	print('Initialized the database.')

def get_db():
	"""Opens a new database connection if there is none yet for the
	current application context.
	"""
	if not hasattr(g, 'sqlite_db'):
		g.sqlite_db = connect_db()
	return g.sqlite_db

@app.teardown_appcontext
def close_db(error):
	"""Closes the database again at the end of the request."""
	if hasattr(g, 'sqlite_db'):
		g.sqlite_db.close()

@app.route('/')
def show_entries():
	db = get_db()
	cur = db.execute('select seed, text from entries order by id desc')
	entries = cur.fetchall()
	return render_template('show_entries.html', entries=entries)

@app.route('/add', methods=['POST'])
def add_entry():
	db = get_db()
	seed = request.form["seed"]
	try:
		text = predict_text(seed)
		db.execute('insert into entries (seed, text) values (?, ?)',
				[seed, text])
		db.execute('delete from entries where id in (select id from entries order by id desc limit -1 offset 1000)')
		db.commit()
		return render_template('add_entry.html', text=text)
	except:
		return render_template('add_entry.html', error_message='Only Hebrew characters and spaces are accepted')

# text prediction code

maxlen = 40

# read file
file_path = os.path.join(app.root_path, 'talmud.txt')
text = open(file_path,'r').read()

chars = sorted(list(set(text)))
char_indices = dict((c, i) for i, c in enumerate(chars))
indices_char = dict((i, c) for i, c in enumerate(chars))

model_path = os.path.join(app.root_path, 'talmud_model.h5')

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


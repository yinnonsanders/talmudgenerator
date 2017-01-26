from flask import Flask
import os
app = Flask(__name__)
app.config.from_pyfile('config.py')

app.config.update(dict(
    DATABASE=os.path.join(app.root_path, 'talmudgenerator.db')
))

import talmudgenerator.talmudgenerator

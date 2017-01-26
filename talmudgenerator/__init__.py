from flask import Flask
import config
import os
app = Flask(__name__)
app.config.from_object('config')

app.config.update(dict(
    DATABASE=os.path.join(app.root_path, 'talmudgenerator.db')
))

import talmudgenerator.views

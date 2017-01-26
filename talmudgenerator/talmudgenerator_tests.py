import os
import talmudgenerator
import text_prediction
import unittest
import tempfile

class TalmudGeneratorTestCase(unittest.TestCase):

	def setUp(self):
		self.db_fd, talmudgenerator.app.config['DATABASE'] = tempfile.mkstemp()
		talmudgenerator.app.config['TESTING'] = True
		self.app = talmudgenerator.app.test_client()
		with talmudgenerator.app.app_context():
			talmudgenerator.init_db()

	def tearDown(self):
		os.close(self.db_fd)
		os.unlink(talmudgenerator.app.config['DATABASE'])

	def test_empty_db(self):
		rv = self.app.get('/')
		assert b'Recently generated sugyot' in rv.data

if __name__ == '__main__':
	unittest.main()

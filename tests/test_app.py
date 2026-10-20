import unittest
import json
from app import create_app
from database import db

class AIPlacementPortalTestCase(unittest.TestCase):
    def setUp(self):
        self.app = create_app()
        self.app.config['TESTING'] = True
        self.client = self.app.test_client()

        # Unique test user
        import time
        self.test_email = f"test_{int(time.time()*1000)}@portal.com"
        self.test_password = "password123"
        self.test_name = "Candidate Tester"

    def test_01_public_and_redirect_routes(self):
        """Test public endpoints and redirects"""
        res = self.client.get('/')
        self.assertEqual(res.status_code, 302)
        self.assertIn('/login', res.headers['Location'])

        res = self.client.get('/login')
        self.assertEqual(res.status_code, 200)
        self.assertIn(b'Candidate Login', res.data)

        res = self.client.get('/register')
        self.assertEqual(res.status_code, 200)
        self.assertIn(b'Create Account', res.data)

    def test_02_registration_and_authentication(self):
        """Test user registration and subsequent login"""
        # Register new candidate
        reg_res = self.client.post('/register', json={
            'name': self.test_name,
            'email': self.test_email,
            'password': self.test_password,
            'confirm_password': self.test_password
        })
        self.assertEqual(reg_res.status_code, 201)
        data = json.loads(reg_res.data)
        self.assertTrue(data['success'])

        # Attempt duplicate registration (should fail with 409)
        dup_res = self.client.post('/register', json={
            'name': self.test_name,
            'email': self.test_email,
            'password': self.test_password,
            'confirm_password': self.test_password
        })
        self.assertEqual(dup_res.status_code, 409)

        # Logout
        self.client.get('/logout')

        # Test login with invalid password
        bad_login = self.client.post('/login', json={
            'email': self.test_email,
            'password': 'wrongpassword'
        })
        self.assertEqual(bad_login.status_code, 401)

        # Test login with correct password
        good_login = self.client.post('/login', json={
            'email': self.test_email,
            'password': self.test_password
        })
        self.assertEqual(good_login.status_code, 200)
        login_data = json.loads(good_login.data)
        self.assertTrue(login_data['success'])

    def _login_session(self):
        # Register and login for session-authenticated tests
        self.client.post('/register', json={
            'name': self.test_name,
            'email': self.test_email,
            'password': self.test_password,
            'confirm_password': self.test_password
        })

    def test_03_technical_interview_flow(self):
        """Test technical question generation and strict evaluation"""
        self._login_session()

        # Generate questions
        gen_res = self.client.post('/technical/generate', json={'job_role': 'Full Stack Developer'})
        self.assertEqual(gen_res.status_code, 200)
        data = json.loads(gen_res.data)
        self.assertTrue(data['success'])
        self.assertEqual(len(data['questions']), 5)

        # Evaluate answer
        eval_res = self.client.post('/technical/evaluate', json={
            'job_role': 'Full Stack Developer',
            'question_number': 1,
            'question_text': data['questions'][0],
            'submitted_answer': 'Client-Side Rendering renders in browser via JS bundles. Server-Side Rendering renders on server per request offering faster initial load and better SEO.'
        })
        self.assertEqual(eval_res.status_code, 200)
        eval_data = json.loads(eval_res.data)
        self.assertTrue(eval_data['success'])
        self.assertIn('score', eval_data)
        self.assertIn('attempt_id', eval_data)

    def test_04_hr_behavioral_flow(self):
        """Test HR question retrieval and STAR evaluation"""
        self._login_session()

        # Get questions
        q_res = self.client.get('/hr/questions')
        self.assertEqual(q_res.status_code, 200)
        q_data = json.loads(q_res.data)
        self.assertTrue(len(q_data['questions']) >= 5)

        # Evaluate answer
        eval_res = self.client.post('/hr/evaluate', json={
            'question_text': 'Tell me about yourself.',
            'submitted_answer': 'I am a computer science graduate focused on full stack development. In my previous capstone project, I led the frontend architecture and built real-time WebSocket communication.'
        })
        self.assertEqual(eval_res.status_code, 200)
        eval_data = json.loads(eval_res.data)
        self.assertTrue(eval_data['success'])
        self.assertIn('score_breakdown', eval_data)

    def test_05_group_discussion_flow(self):
        """Test GD topic generation and contribution evaluation"""
        self._login_session()

        # Topic generation
        top_res = self.client.post('/gd/generate-topic')
        self.assertEqual(top_res.status_code, 200)
        top_data = json.loads(top_res.data)
        self.assertTrue(top_data['success'])
        self.assertIn('topic', top_data['data'])

        # Evaluation
        eval_res = self.client.post('/gd/evaluate', json={
            'topic': top_data['data']['topic'],
            'submitted_opinion': 'In my view, remote work optimizes individual productivity for deep tasks, yet regular in-person interactions prevent isolation and nurture company culture.'
        })
        self.assertEqual(eval_res.status_code, 200)
        eval_data = json.loads(eval_res.data)
        self.assertTrue(eval_data['success'])
        self.assertIn('counterarguments', eval_data)

    def test_06_english_checker_flow(self):
        """Test English checker against the exact text from Screenshot 4"""
        self._login_session()

        sample_text = (
            "Climate change is when the weather patterns on Earth gets real different over a long time. "
            "Even though the planet used to get warmer and colder by itself back then, now it's happening "
            "way too fast because of what people is doing. We is burning too much stuff like coal and oil, "
            "which puts bad gases into the air and traps the heat like a greenhouse."
        )

        res = self.client.post('/english/analyze', json={'text': sample_text})
        self.assertEqual(res.status_code, 200)
        data = json.loads(res.data)
        self.assertTrue(data['success'])
        self.assertEqual(data['status_badge'], 'POOR')
        self.assertEqual(data['score'], 4.0)
        self.assertEqual(data['readiness_percentage'], 40)
        self.assertIn('corrections', data)
        self.assertIn('corrected_text', data)

    def test_07_history_retrieval_and_deletion(self):
        """Test history retrieval and record deletion"""
        self._login_session()

        # Create an attempt
        eval_res = self.client.post('/english/analyze', json={'text': 'Test text for history entry.'})
        attempt_id = json.loads(eval_res.data)['attempt_id']

        # Retrieve history
        hist_res = self.client.get('/history/data')
        self.assertEqual(hist_res.status_code, 200)
        hist_data = json.loads(hist_res.data)
        self.assertTrue(len(hist_data['attempts']) > 0)

        # Delete attempt
        del_res = self.client.delete(f'/history/english/{attempt_id}')
        self.assertEqual(del_res.status_code, 200)
        del_data = json.loads(del_res.data)
        self.assertTrue(del_data['success'])

if __name__ == '__main__':
    unittest.main()

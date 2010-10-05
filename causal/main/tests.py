from django.test import TestCase
from causal.main.models import OAuthSetting
from causal.main.views import history
from django.test.client import Client
from django.core.urlresolvers import reverse

try:
    import wingdbstub
except ImportError:
    pass

class TestMain(TestCase):
    """Test the module with fixtures."""
    
    fixtures = ['oauth_settings.json']
    
    def setUp(self):
        pass
    
    def test_history_view(self):
        """Test raw history view from main."""
        
        post_params = {}
	       
        response = self.client.post(reverse('history'), post_params)
        # test we get redirected to login screen
        self.assertEquals(response.status_code, 302)
        
    def _login(self):
        """Log a user in."""
        user = User.objects.create_user('admin', 'admin@isotoma.com', 'password')
	user.save()
	self.client = Client()
	self.client.post('/login/', {'username': 'admin', 'password': 'password'})
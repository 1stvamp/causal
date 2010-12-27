from django.test import TestCase
from causal.delicious.service import _convert_feed
import feedparser

try:
    import wingdbstub
except ImportError:
    pass

class TestDeliciousService(TestCase):
    """Test the module with fixtures."""

    def setUp(self):
        self.rss_feed = """
    <?xml version="1.0" encoding="UTF-8"?>
<rss version="2.0" xmlns:atom="http://www.w3.org/2005/Atom" xmlns:content="http://purl.org/rss/1.0/modules/content/" xmlns:wfw="http://wellformedweb.org/CommentAPI/" xmlns:rdf="http://www.w3.org/1999/02/22-rdf-syntax-ns#" xmlns:dc="http://purl.org/dc/elements/1.1/" xmlns:cc="http://web.resource.org/cc/">
  <channel>
    <title>Delicious/username</title>
    <link>http://www.delicious.com/username</link>
    <description>bookmarks posted by username</description>
    <atom:link rel="self" type="application/rss+xml" href="http://feeds.delicious.com/v2/rss/username?count=100"/>
    <item>
      <title>LongURL | API Version 2.0 Documentation</title>
      <pubDate>Tue, 23 Nov 2010 22:03:29 +0000</pubDate>
      <guid isPermaLink="false">http://www.delicious.com/url/aacd5c54283976b60786103f1421aab4#username</guid>
      <link>http://longurl.org/api</link>
      <dc:creator><![CDATA[username]]></dc:creator>
      <comments>http://www.delicious.com/url/aacd5c54283976b60786103f1421aab4</comments>
      <wfw:commentRss>http://feeds.delicious.com/v2/rss/url/aacd5c54283976b60786103f1421aab4</wfw:commentRss>
      <source url="http://feeds.delicious.com/v2/rss/username">username's bookmarks</source>
      <category domain="http://www.delicious.com/username/">urls</category>
      <category domain="http://www.delicious.com/username/">shortners</category>
    </item>
  </channel>

</rss>
"""
        self.rss_feed_parsed = feedparser.parse(self.rss_feed)
        
    def tearDown(self):
        pass

    def test_convert_feed(self):
        """Check we get back a correctly formed list of ServiceItems"""
        items = _convert_feed(self.rss_feed_parsed, 'causal-delicious', 'username')
        self.assertEquals(len(items), 1)
        
        for item in items:
            self.assertEquals(item.title, self.rss_feed_parsed.entries[0].title)
            self.assertEquals(item.body, self.rss_feed_parsed.entries[0].link)
            self.assertEquals(item.link_back, self.rss_feed_parsed.entries[0].id)
            self.assertEquals(item.service, 'causal-delicious')
            self.assertEquals(item.user, 'username')
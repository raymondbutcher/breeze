import tornado.gen
import tornado.web

from breeze.handlers.mongo import MongoHandler


class FakePageHandler(MongoHandler):

    @staticmethod
    def _get_fake_page(path):
        return {
            'id': 1,
            'path': path,
            'title': 'Breeze Website Platform',
            'structure': [
                [
                    {
                        'colspan': 12,
                        'content': '''
                            <header>
                                <h3 style="float: right; margin-bottom: 0">By Raymond Butcher</h3>
                                <h1 style="
background-image: linear-gradient(right bottom, rgb(0,164,209) 57%, rgb(4,132,217) 46%, rgb(252,252,252) 100%);
background-image: -o-linear-gradient(right bottom, rgb(0,164,209) 57%, rgb(4,132,217) 46%, rgb(252,252,252) 100%);
background-image: -moz-linear-gradient(right bottom, rgb(0,164,209) 57%, rgb(4,132,217) 46%, rgb(252,252,252) 100%);
background-image: -webkit-linear-gradient(right bottom, rgb(0,164,209) 57%, rgb(4,132,217) 46%, rgb(252,252,252) 100%);
background-image: -ms-linear-gradient(right bottom, rgb(0,164,209) 57%, rgb(4,132,217) 46%, rgb(252,252,252) 100%);

background-image: -webkit-gradient(
    linear,
    right bottom,
    left top,
    color-stop(0.57, rgb(0,164,209)),
    color-stop(0.46, rgb(4,132,217)),
    color-stop(1, rgb(252,252,252))
);

-webkit-border-radius: 10px;
-moz-border-radius: 10px;

background-color: lightblue;
color: white;
padding: 5px 15px;
margin-bottom: 0;
float: left;
">Breeze</h1>
                                <h2 style="margin: auto; margin-left: 5px; line-height: normal; clear: left; color: rgb(4,132,217)">Website Platform</h2>
                            </header>
                        ''',
                    },
                ],
                [
                    {'colspan': 12, 'content': '<hr/>'},
                ],
                [
                    {
                        'colspan': 8,
                        'content': '''
                            <h2>So here is the immediate plan...</h2>
                            
                            <h3>Mongo</h3>
                            <p>Set up mongo on a VM and use it for data storage.</p>
                            
                            <h3>Articles</h3>
                            <p>
                                Need an article content type so I can make blog posts.
                            </p>
                            
                            <h3>Feeds</h3>
                            <p>
                                Need a feed content type, that allows you to query other content types, returning a list of content. Content types will need to have some kind of standard API for being queryable.
                            </p>
                            
                            <h3>Create/Edit Articles</h3>
                            <p>
                                Need a way to post some articles to this system. In-line editing would be cool. Maybe a feed could accept content, and then creating content would &quot;pin&quot; it to the feed, while still being queryable by other feeds.
                            </p>
                            
                            <h3>Authentication/Permissions</h3>
                            <p>Restrict who can create pages, and submit articles, etc.</p>
                            
                            <h3>CSS Styles</h3>
                            <p>
                                On save of a page, transform inline styles into CSS classes. This would require some CSS storage system.
                            </p>
                            
                            <h3>Page Builder</h3>
                            <p>
                                Need a way to build pages and their structures.
                                This will be a complicated JavaScript interface.
                                It must allow putting in raw content via a WYSIWYG interface.
                                It must also allow putting in various content types such as feeds, articles, etc.
                            </p>
                            
                            <hr/>
                        ''',
                    },
                    {
                        'colspan': 4,
                        'content': '''
                            <div style="padding: 1px 20px; margin-top: -2px; border-top: solid 2px black; background-color: lightblue">
                                <h3>Features</h3>
                                <ul>
                                    <li>Page engine that transforms JSON into a &quot;responsive&quot; HTML layout.</li>
                                </ul>
                            </div>
                            <div style="padding: 1px 20px; margin-top: -2px; border-top: solid 2px black; background-color: skyblue">
                                <h3>Required Features</h3>
                                <ol>
                                    <li>Page storage</li>
                                    <li>Page creation interface</li>
                                </ol>
                            </div>
                            <div style="padding: 1px 20px; margin-top: -2px; border-top: solid 2px black; border-bottom: solid 2px black; background-color: steelblue">
                                <h3>Desired Features</h3>
                                <ol>
                                    <li>Automatically transform styles into CSS.</li>
                                    <li>Something that could be used as a ticket/bug report system.</li>
                                </ol>
                            </div>
                        ''',
                    },
                ],
                [
                    {
                        'colspan': 12,
                        'content': '''
                            <h3>Credits</h3>
                            <ul style="list-style: none">
                                <li style="float: left; margin-right: 2em"><a href="http://www.tornadoweb.org/">Tornado</a></li>
                                <li style="float: left"><a href="http://cssgrid.net/">1140 CSS Grid</a></li>
                            </ul>
                        '''
                    },
                ],
            ],
        }

    @tornado.web.addslash
    @tornado.web.asynchronous
    @tornado.gen.engine
    def get(self):
        path = self.get_argument('path')
        page = self._get_fake_page(path)
        result = yield tornado.gen.Task(self.db.pages.save, page)
        result = self.get_mongo_result(result)
        self.write('Created fake page for %s' % path)
        self.finish()

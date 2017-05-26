from pprint import pprint
from zope.testing import setupstack
import bobo
import json
import pkg_resources
import webtest

from .var import Vars

demo_db = '''
<zodb>
  <demostorage>
  </demostorage>
</zodb>
'''

class APITests(setupstack.TestCase):

    maxDiff = None

    def setUp(self):
        app = bobo.Application(
            bobo_resources="""
                       twotieredkanban.apibase
                       """,
            bobo_handle_exceptions = False,
            )
        self._app = pkg_resources.load_entry_point(
            'zc.zodbwsgi', 'paste.filter_app_factory', 'main')(
            app, {},
            configuration = demo_db,
            max_connections = '4',
            thread_transaction_manager = 'False',
            initializer = "twotieredkanban.apibase:initialize"
            )
        self.db = self._app.database
        self.conn = self.db.open()
        self.app = self._test_app()
        self.vars = Vars()

    def _test_app(self, email='test@example.com'):
        extra_environ = {}
        tapp = webtest.TestApp(self._app, extra_environ=extra_environ)
        if email:
            tapp.get('/?email=' + email)
        return tapp

    def update_app(self, app, resp):
        try:
            json = resp.json
        except Exception:
            pass
        else:
            updates = json.get('updates')
            if updates:
                app.extra_environ['HTTP_X_GENERATION'] = str(
                    updates['generation'])

        return resp

    def reset_generation(self):
        self.app.extra_environ.pop('HTTP_X_GENERATION', None)

    def get(self, *a, **kw):
        app = self.app
        return self.update_app(app, app.get(*a, **kw))

    def post(self, *a, **kw):
        app = self.app
        return self.update_app(app, app.post_json(*a, **kw))

    def put(self, *a, **kw):
        app = self.app
        return self.update_app(app, app.put_json(*a, **kw))

    def test_site_poll(self):
        self.assertEqual(
            dict(updates=
                 dict(generation=self.vars.generation,
                      site=dict(admins=['test@example.com'],
                                users=['test@example.com'],
                                boards=[])
                      )
                 ),
        self.get('/site/poll').json)

    def test_add_board(self):
        self.get('/site/poll') # set generation
        data = dict(name='Dev', title='Development',
                    description='Let us develop things')
        self.assertEqual(
            dict(updates=
                 dict(generation=self.vars.generation,
                      site=dict(admins=['test@example.com'],
                                users=['test@example.com'],
                                boards=[data])
                      )
                 ),
            self.post('/site/boards', data).json)

    def test_add_project(self):
        self.post('/site/boards', dict(name='t', title='t', description=''))
        self.get('/board/t/poll') # set generation
        data = dict(title="do it", description="do the thing", order=42)
        self.assertEqual(
            dict(updates=
                 dict(generation=self.vars.generation,
                      tasks=dict(adds=[self.vars.project])
                      )
                 ),
            self.post('/board/t/projects', data).json)
        for name in data:
            self.assertEqual(data[name], self.vars.project[name])

    def test_update_project(self):
        self.post('/site/boards', dict(name='t', title='t', description=''))
        r = self.post('/board/t/projects',
                      dict(title='t', description='d', order=42))
        id = r.json['updates']['tasks']['adds'][0]['id']

        data = dict(title="do it", description="do the thing")
        self.assertEqual(
            dict(updates=
                 dict(generation=self.vars.generation,
                      tasks=dict(adds=[self.vars.project])
                      )
                 ),
            self.put('/board/t/tasks/' + id, data).json)
        for name in data:
            self.assertEqual(data[name], self.vars.project[name])

    def test_add_task(self):
        self.post('/site/boards', dict(name='t', title='t', description=''))
        r = self.post('/board/t/projects',
                      dict(title='t', description='d', order=42))
        id = r.json['updates']['tasks']['adds'][0]['id']
        data = dict(title="do it", description="do the thing", order=50,
                    size=1, blocked='no can do', assigned='test@example.com')
        self.assertEqual(
            dict(updates=
                 dict(generation=self.vars.generation,
                      tasks=dict(adds=[self.vars.task])
                      )
                 ),
            self.post('/board/t/project/' + id, data).json)
        for name in data:
            self.assertEqual(data[name], self.vars.task[name])

    def get_states(self):
        self.post('/site/boards', dict(name='t', title='t', description=''))
        self.reset_generation()
        return self.get('/board/t/poll').json['updates']['states']['adds']

    def test_move_project_to_new_state(self):
        states = self.get_states()
        [backlog_id] = [s['id'] for s in states if s['title'] == 'Backlog']
        [dev_id] = [s['id'] for s in states if s['title'] == 'Development']
        r = self.post('/board/t/projects',
                      dict(title='t', description='d', order=42))
        id = r.json['updates']['tasks']['adds'][0]['id']
        self.assertEqual(
            dict(updates=
                 dict(generation=self.vars.generation,
                      tasks=dict(adds=[self.vars.task])
                      )
                 ),
            self.put('/board/t/move/' + id,
                     dict(state_id=dev_id, order=7)).json)
        task = self.vars.task
        self.assertEqual(id, task['id'])
        self.assertEqual(dev_id, task['state'])
        self.assertEqual(7, task['order'])
        self.assertEqual(None, task['parent'])

    def test_move_task_to_new_project(self):
        states = self.get_states()
        r = self.post('/board/t/projects',
                      dict(title='p1', description='', order=1))
        p1id = r.json['updates']['tasks']['adds'][0]['id']
        r = self.post('/board/t/project/' + p1id,
                      dict(title='t1', description='', order=2))
        t1 = r.json['updates']['tasks']['adds'][0]
        r = self.post('/board/t/projects',
                      dict(title='p2', description='', order=3))
        p2id = r.json['updates']['tasks']['adds'][0]['id']
        self.assertEqual(
            dict(updates=
                 dict(generation=self.vars.generation,
                      tasks=dict(adds=[self.vars.task])
                      )
                 ),
            self.put('/board/t/move/' + t1['id'], dict(parent_id=p2id)).json)
        task = self.vars.task
        self.assertEqual(t1['id'], task['id'])
        self.assertEqual(t1['state'], task['state'])
        self.assertEqual(t1['order'], task['order'])
        self.assertEqual(p2id, task['parent'])

    def test_auth(self):
        # unauthenticated users can't get things
        app = self._test_app(None)
        app.get('/', status=401)

        # Add a regular users, which an admin can do:
        admins = ['test@example.com']
        users = admins + ['user@admin.com']
        self.app.put('/site/users', dict(users=users, admins=admins))

        # Now a user can get the board
        app = self._test_app(users[-1])
        app.get('/')
        # But they aren't allowed to do admin functions:
        self.app.put('/site/users',
                     dict(users=users, admins=admins),
                     status=403)
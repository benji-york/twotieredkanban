import bobo

from .apiutil import Sync, post, put

@bobo.scan_class
class Site(Sync):

    def check(self, func):
        base = self.base
        r = base.check(func)
        if r:
            return r
        if base.email not in base.site.admins:
            base.error(403, dict(error="You must be an adminstrator"))

    @post('/boards')
    def post_board(self, name, title, description):
        if name in self.context.boards:
            self.base.error("A board with name %r already exists." % name)
        self.context.add_board(name, title, description)
        return self.response()

    @put('/users')
    def put_users(self, users, admins):
        self.context.update_users(users, admins)
        return self.response()
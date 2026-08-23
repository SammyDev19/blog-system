class User:

    def __init__(self, user_id, username, is_admin=False):
        self.id = user_id
        self.username = username
        self.is_admin = is_admin


class Post:

    def __init__(self, post_id, title, content, user_id, created_at):
        self.id = post_id
        self.title = title
        self.content = content
        self.user_id = user_id
        self.created_at = created_at


class Comment:

    def __init__(self, comment_id, content, user_id, post_id, created_at):
        self.id = comment_id
        self.content = content
        self.user_id = user_id
        self.post_id = post_id
        self.created_at = created_at
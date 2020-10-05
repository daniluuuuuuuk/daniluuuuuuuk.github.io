from json import JSONEncoder


class JSONENcoder(JSONEncoder):

  def default(self, o):
      return o.__dict__ 
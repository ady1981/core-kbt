import json

from common import has_property

# adict = {'a': 1, 'b': 2}
# print(json.dumps(vfilter(lambda k, v: v > 0, adict), indent=2))
# print({'a': 'b'} | {})
member_of = {
  'a': ['a'],
  'b': ['b'],
  'c': ['b', 'c'],
  'd': ['c', 'd']
}

def is_member_of(a, b):
    return a in member_of[b]

print(is_member_of('b', 'd'))
print(has_property('b', 'd', is_member_of, {'a', 'b', 'c', 'd'} - {'b'}))
# has_property(a, b, has_direct_property, rest_items: set = {})

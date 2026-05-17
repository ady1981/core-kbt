import json

from common import has_transitive_property

# adict = {'a': 1, 'b': 2}
# print(json.dumps(vfilter(lambda k, v: v > 0, adict), indent=2))
# print({'a': 'b'} | {})
member_of = {
  'Пользовательский интерфейс': ['Пользовательский интерфейс', 'Интерфейс пользователя'],
  'Интерфейс пользователя': ['Интерфейс пользователя', 'Пользовательский интерфейс', 'Фронтенд'],
  'Фронтенд': ['Фронтенд', 'Пользовательский интерфейс', 'Интерфейс пользователя'],
  'Серверная часть': ['Серверная часть', 'Бэкенд'],
  'Бэкенд': ['Бэкенд', 'Серверная часть'],
  'База данных': ['База данных', 'Хранилище данных'],
  'Хранилище данных': ['Хранилище данных', 'База данных']
}

def is_member_of(a, b):
    return a in member_of[b]

print(is_member_of('b', 'd'))
print(has_transitive_property('b', 'd', is_member_of, {'a', 'b', 'c', 'd'} - {'b'}))
# has_property(a, b, has_direct_property, rest_items: set = {})

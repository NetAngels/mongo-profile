# -* coding: utf-8 -*-
"""
We use db "test" and collection "people" for testing purposes
"""
from unittest import TestCase
from mongoprofile import parse_record, MongoProfiler, DummyMongoProfiler


class ParserTest(TestCase):
    command_cmd = "query test.$cmd ntoreturn:1 command: { drop: \"people\" } reslen:134 bytes:118"
    insert_cmd = "insert test.people"
    update_cmd = "update test.people  query: { name: \"John\" } nscanned:1 fastmod "
    remove_cmd = "remove test.people  query: { name: \"Mary\" }"
    marker_cmd = 'query test.phony_mongoprofile_marker reslen:0 nscanned:1  \nquery: { $query: { text: "hello world" } } nreturned:1 bytes:70'
    query_commands = [
        (
            'query test.people reslen:86 nscanned:1  \nquery: { age: { $gt: 20.0 } }  nreturned:1 bytes:70',
            'test> db.people.find({ age: { $gt: 20.0 } })'
        ),
        (
            'query test.people ntoreturn:1 reslen:199 nscanned:4  \nquery: { $query: { age: { $gt: 20.0 } }, $orderby: { age: -1 } }  nreturned:1 bytes:70',
            'test> db.people.find({ $query: { age: { $gt: 20.0 } }, $orderby: { age: -1 } })'
        ),
    ]

    getmore_cmd = 'getmore test.people cid:5236062738003527185 getMore: { $query: { age: { $gt: 20.0 } } }  bytes:128950 nreturned:1750'

    def testCommandCmd(self):
        record_source = dict(info=self.command_cmd)
        record = parse_record(record_source)
        self.assertEquals(str(record), 'test> db.runCommand({ drop: "people" })')
        self.assertEquals(record['ntoreturn'], 1)
        self.assertEquals(record['reslen'], 134)
        self.assertEquals(record['bytes'], 118)

    def testInsertCmd(self):
        record_source = dict(info=self.insert_cmd)
        record = parse_record(record_source)
        self.assertEquals(str(record), 'test> db.people.insert({...})')

    def testUpdateCmd(self):
        record_source = dict(info=self.update_cmd)
        record = parse_record(record_source)
        self.assertEquals(str(record), 'test> db.people.update({ name: "John" }, {...})')
        self.assertEquals(record['nscanned'], 1)
        self.assertEquals(record['fastmod'], True)

    def testRemoveCmd(self):
        record_source = dict(info=self.remove_cmd)
        record = parse_record(record_source)
        self.assertEquals(str(record), 'test> db.people.remove({ name: "Mary" })')

    def testMarkerCmd(self):
        record_source = dict(info=self.marker_cmd)
        record = parse_record(record_source)
        self.assertEquals(str(record), '==== hello world ====')

    def testQueryCmd(self):
        for cmd, result in self.query_commands:
            record_source = dict(info=cmd)
            record = parse_record(record_source)
            self.assertEquals(str(record), result)

    def testGetMoreCmd(self):
        record_source = dict(info=self.getmore_cmd)
        record = parse_record(record_source)
        self.assertEquals(str(record), 'test> db.people.find({ $query: { age: { $gt: 20.0 } } }) *getmore')


from pymongo import Connection
class MongoProfile(TestCase):

    expected_records = [
        '==== insert ====',
        'test> db.people.insert({...})',
        'test> db.people.insert({...})',
        '==== modification ====',
        'test> db.people.update({ name: "John" }, {...})',
        'test> db.people.remove({ name: "Mary" })',
        '==== search ====',
        'test> db.people.find({ $query: { age: { $gt: 20.0 } } })',
        'test> db.runCommand({ count: "people", query: { age: { $gt: 20.0 } }, fields: null })',
    ]

    def setUp(self):
        self.db = Connection().test

    def testMongoProfile(self):
        profiler = MongoProfiler(self.db)
        self._doQueries(profiler)
        record_info = [str(record) for record in profiler.get_records()]
        for expected, received in zip(self.expected_records, record_info):
            self.assertEquals(expected, received)

    def testDummyMongoProfile(self):
        profiler = DummyMongoProfiler(self.db)
        self._doQueries(profiler)
        self.assertEquals(profiler.get_records(), [])

    def _doQueries(self, profiler):
        with profiler:
            profiler.mark('insert')
            self.db.people.insert(dict(name='John', age=20))
            self.db.people.insert(dict(name='Mary', age=30))
            profiler.mark('modification')
            self.db.people.update({'name': 'John'}, {'age': 21})
            self.db.people.remove({'name': 'Mary'})
            profiler.mark('search')
            list(self.db.people.find({'age': {'$gt': 20.0}}))
            self.db.people.find({'age': {'$gt': 20.0}}).count()

    def tearDown(self):
        self.db.drop_collection('people')

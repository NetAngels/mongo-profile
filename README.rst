mongo-profile
=============

Module **mongoprofile** contains functions and objects to retreive and parse
the output of MongoDB's ``"db.system.profile.find()"``

To get more information about MongoDB profiling, see
http://www.mongodb.org/display/DOCS/Database+Profiler


mongoprofile.mongoprofile
--------------------------

Class `mongoprofile` is a "with"-wrapper around any set of MongoDB queries.
Typical usecase contains three steps:

**Step1. Open connection**::

    >>> from pymongo import Connection
    >>> db = Connection().test

**Step 2. Execute and profile queries**::

    >>> with mongoprofile(db) as profile:
    ...     db.people.insert(dict(name='John', age=20))
    ...     db.people.insert(dict(name='Mary', age=30))
    ...     db.people.update({'name': 'John'}, {'age': 21})
    ...     db.people.remove({'name': 'Mary'})
    ...     list(db.people.find({'age': {'$gt': 20.0}}))
    ...     db.people.find({'age': {'$gt': 20.0}}).count()

**Step3. Get profile info**

As a result, you will get the more or less comprehensive list of dict
subclasses, containing all profile information, including parsed "info". Every
subclass has redefined ``__str__`` method returning the convenient presentation
of request. See the example below to get the point::

    >>> for record in profile:
    ...    print str(record)

    test> db.people.insert({...})
    test> db.people.insert({...})
    test> db.people.update({ name: "John" }, {...})
    test> db.people.remove({ name: "Mary" })
    test> db.people.find({ $query: { age: { $gt: 20.0 } } })
    test> db.runCommand({ count: "people", query: { age: { $gt: 20.0 } }, fields: null })

A few more facts about record objects worth to be known:

- There is a ``record.short_info()`` method returning the one-line string with
  short information about the query.
- Every record class is a subclass of dict, and because of that it's possible
  to get a bunch of ordered information using calls such as
  ``record['millis']``, ``record['ts']``, etc.

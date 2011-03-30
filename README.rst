mongo-profile
=============

Module **mongoprofile** contains functions and objects to retreive and parse
the output of MongoDB's ``"db.system.profile.find()"``

To get more information about MongoDB profiling, see
http://www.mongodb.org/display/DOCS/Database+Profiler


mongoprofile.MongoProfiler
--------------------------

Class `MongoProfiler` is a "with"-wrapper around any set of MongoDB queries.
Typical usecase contains three steps:

**Step1. Open connection**::

    >>> from pymongo import Connection
    >>> db = Connection().test

**Step 2. Execute and profile queries**::

    >>> profiler = MongoProfiler(db)
    >>> with profiler:
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

    >>> for record in profiler.get_records():
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

Markers
````````

The ``MongoProfiler`` class has ``.mark(text)`` method. When ``mark`` is
invoked, mongodb client do the fake query to phony collection just to record
data in log. After the job has ended, these markers will be available as 
`'==== text ===='` records.

Having changed previous example, we get something like this.

Commands::


    >>> profiler = MongoProfiler(db)
    >>> with profiler:
    ...     profiler.mark('insert')
    ...     db.people.insert(dict(name='John', age=20))
    ...     db.people.insert(dict(name='Mary', age=30))
    ...     profiler.mark('search')
    ...     list(db.people.find({'age': {'$gt': 20.0}}))
    ...     db.people.find({'age': {'$gt': 20.0}}).count()


Will lead to the output::

    '==== insert ===='
    test> db.people.insert({...})
    test> db.people.insert({...})
    '==== search ===='
    test> db.people.find({ $query: { age: { $gt: 20.0 } } })
    test> db.runCommand({ count: "people", query: { age: { $gt: 20.0 } }, fields: null })

DummyMongoProfiler
-------------------

It is probable that depending on some circumstances, you want or don't want to
spend extra resources on your query profiling. Stub ``DummyMongoProfiler``
class mocking ``MongoProfiler`` interface can be used for that purpose. Below
is the usage sample with `Django-nonrel`_ in mind::

    >>> from django.conf import settings
    >>> Profiler = settings.DEBUG and MongoProfiler or DummyMongoProfiler
    >>> profiler = Profiler(db)
    >>> with profiler:
    ...     ModelClass.objects.filter(...)
    ...

.. _Django-nonrel: http://www.allbuttonspressed.com/projects/django-nonrel

Miscellaneous remarks
---------------------

Collection `db.system.profile` is capped with a relatively small capacity. If
you want to profile large amount of records at once, it is worth to extend its
size. The following set of commands creates capped collection of 100Mb::

    > db.setProfilingLevel(0)
    > db.system.profile.drop()
    > db.createCollection("system.profile", {capped:true, size:100*1e6})

Command ``db.system.profile.stats()`` shows you the current state of
collection.

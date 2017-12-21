typedef struct _object {
    _PyObject_HEAD_EXTRA
    Py_ssize_t ob_refcnt;
    struct _typeobject *ob_type;
} PyObject;




assert (3, 6) <= sys.version_info < (3, 7) # Valid only in Python 3.6









typedef struct {
    PyObject_HEAD
    Py_ssize_t ma_used;
    uint64_t ma_version_tag;
    PyDictKeysObject *ma_keys;
    PyObject **ma_values;
} PyDictObject;
We can mirror the structure behind the dict this way, plus add some methods that will be useful later:

In [2]:
class DictStruct(PyObjectStruct):
    _fields_ = [("ma_used", py_ssize_t),
                ("ma_version_tag", ctypes.c_uint64),
                ("ma_keys", ctypes.c_void_p),
                ("ma_values", ctypes.c_void_p),
               ]
    
    def __repr__(self):
        return (f"DictStruct(size={self.ma_used}, "
                f"refcount={self.ob_refcnt}, "
                f"version={self.ma_version_tag})")
    
    @classmethod
    def wrap(cls, obj):
        assert isinstance(obj, dict)
        return cls.from_address(id(obj))
As a sanity check, let's make sure our structures match the size in memory of the types they are meant to wrap:

In [3]:
assert object.__basicsize__ == ctypes.sizeof(PyObjectStruct)
assert dict.__basicsize__ == ctypes.sizeof(DictStruct)
With this setup, we can now wrap any dict object to get a look at its internal properties. Here's what this gives for a simple dict:

In [4]:
D = dict(a=1, b=2, c=3)
DictStruct.wrap(D)
Out[4]:
DictStruct(size=3, refcount=1, version=508220)
To convince ourselves further that we're properly wrapping the object, let's make two more explicit references to this dict, add a new key, and make sure the size and reference count reflect this:

In [5]:
D2 = D
D3 = D2
D3['d'] = 5
DictStruct.wrap(D)
Out[5]:
DictStruct(size=4, refcount=3, version=515714)
It seems this is working correctly!

Exploring the Version Number
So what does the version number do? As Brandon explained in his talk, every dict in CPython 3.6 now has a version number that is

globally unique
updated locally whenever a dict is modified
incremented globally whenever any dict is modified
This global value is stored in the pydict_global_version variable in the CPython source. So if we create a bunch of new dicts, we should expect each to have a higher version number than the last:

In [6]:
for i in range(10):
    dct = {}
    print(DictStruct.wrap(dct))
DictStruct(size=0, refcount=1, version=518136)
DictStruct(size=0, refcount=1, version=518152)
DictStruct(size=0, refcount=1, version=518157)
DictStruct(size=0, refcount=1, version=518162)
DictStruct(size=0, refcount=1, version=518167)
DictStruct(size=0, refcount=1, version=518172)
DictStruct(size=0, refcount=1, version=518177)
DictStruct(size=0, refcount=1, version=518182)
DictStruct(size=0, refcount=1, version=518187)
DictStruct(size=0, refcount=1, version=518192)
You might expect these versions to increment by one each time, but the version numbers are affected by the fact that Python uses many dictionaries in the background: among other things, local variables, global variables, and object attributes are all stored as dicts, and creating or modifying any of these results in the global version number being incremented.

Similarly, any time we modify our dict it gets a higher version number:

In [7]:
D = {}
Dwrap = DictStruct.wrap(D)
for i in range(10):
    D[i] = i
    print(Dwrap)
DictStruct(size=1, refcount=1, version=521221)
DictStruct(size=2, refcount=1, version=521254)
DictStruct(size=3, refcount=1, version=521270)
DictStruct(size=4, refcount=1, version=521274)
DictStruct(size=5, refcount=1, version=521278)
DictStruct(size=6, refcount=1, version=521288)
DictStruct(size=7, refcount=1, version=521329)
DictStruct(size=8, refcount=1, version=521403)
DictStruct(size=9, refcount=1, version=521487)
DictStruct(size=10, refcount=1, version=521531)
Monkey-patching Dict
Let's go a step further and monkey-patch the dict object itself with a method that accesses the version directly. Basically, we want to add a get_version method to the dict class that accesses this value.

Our first attempt might look something like this:

In [8]:
dict.get_version = lambda obj: DictStruct.wrap(obj).ma_version_tag
---------------------------------------------------------------------------
TypeError                                 Traceback (most recent call last)
<ipython-input-8-99d51a65c779> in <module>()
----> 1 dict.get_version = lambda obj: DictStruct.wrap(obj).ma_version_tag

TypeError: can't set attributes of built-in/extension type 'dict'
We get an error, because Python protects the attributes of built-in types from this kind of mucking. But never fear! We can get around this with (you guessed it) ctypes!

The attributes and methods of any Python object are stored in its __dict__ attribute, which in Python 3.6 is not a dictionary but a mappingproxy object, which you can think of as a read-only wrapper of the underlying dictionary:

In [9]:
class Foo:
    bar = 4
    
Foo.__dict__
Out[9]:
mappingproxy({'__dict__': <attribute '__dict__' of 'Foo' objects>,
              '__doc__': None,
              '__module__': '__main__',
              '__weakref__': <attribute '__weakref__' of 'Foo' objects>,
              'bar': 4})
In fact, looking at the Python 3.6 mappingproxyobject implementation, we see that it's simply an object with a pointer to an underlying dict.

typedef struct {
    PyObject_HEAD
    PyObject *mapping;
} mappingproxyobject;
Let's write a ctypes structure that exposes this:

In [10]:
import types

class MappingProxyStruct(PyObjectStruct):
    _fields_ = [("mapping", ctypes.POINTER(DictStruct))]
    
    @classmethod
    def wrap(cls, D):
        assert isinstance(D, types.MappingProxyType)
        return cls.from_address(id(D))
    
# Sanity check
assert types.MappingProxyType.__basicsize__ == ctypes.sizeof(MappingProxyStruct)
Now we can use this to get a C-level handle for the underlying dict of any mapping proxy:

In [11]:
proxy = MappingProxyStruct.wrap(dict.__dict__)
proxy.mapping
Out[11]:
<__main__.LP_DictStruct at 0x10667dc80>
And we can pass this handle to functions in the C API in order to modify the dictionary wrapped by a read-only mapping proxy:

In [12]:
def mappingproxy_setitem(obj, key, val):
    """Set an item in a read-only mapping proxy"""
    proxy = MappingProxyStruct.wrap(obj)
    ctypes.pythonapi.PyDict_SetItem(proxy.mapping,
                                    ctypes.py_object(key),
                                    ctypes.py_object(val))
In [13]:
mappingproxy_setitem(dict.__dict__,
                     'get_version',
                     lambda self: DictStruct.wrap(self).ma_version_tag)
Once this is executed, we can call get_version() as a method on any Python dictionary to get the version number:

In [15]:
{}.get_version()
Out[15]:
544453
This kind of monkey patching could be used for any built-in type; for example, we could add a scramble method to strings that randomly chooses upper or lower case for its contents:

In [16]:
import random
mappingproxy_setitem(str.__dict__,
                     'scramble',
                     lambda self: ''.join(random.choice([c.lower(), c.upper()]) for c in self))
In [17]:
'hello world'.scramble()
Out[17]:
'hellO WORLd'
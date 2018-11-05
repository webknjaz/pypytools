import pytest
from pypytools.gc import multihook
from pypytools.gc.multihook import MultiHook, GcHooks

@pytest.fixture
def fakegc(monkeypatch):
    mygc = FakeGc()
    monkeypatch.setattr(multihook, 'gc', mygc)
    return mygc

class FakeGc(object):

    class Hooks(object):
        on_gc_minor = None
        on_gc_collect_step = None
        on_gc_collect = None

    def __init__(self):
        self.hooks = self.Hooks()

    def fire_minor(self, stats):
        self.hooks.on_gc_minor(stats)

    def fire_step(self, stats):
        self.hooks.on_gc_collect_step(stats)

    def fire_collect(self, stats):
        self.hooks.on_gc_collect(stats)


class TestMultiHook:

    def test_add_remove_hook(self, fakegc):
        class A:
            on_gc_minor = 'A minor'
            on_gc_collect_step = 'A step'
            on_gc_collect = 'A collect'

        class B:
            on_gc_minor = 'B minor'

        mh = MultiHook()
        a = A()
        b = B()
        mh.add(a)
        assert mh.minor_callbacks == ['A minor']
        assert mh.collect_step_callbacks == ['A step']
        assert mh.collect_callbacks == ['A collect']

        mh.add(b)
        assert mh.minor_callbacks == ['A minor', 'B minor']
        assert mh.collect_step_callbacks == ['A step']
        assert mh.collect_callbacks == ['A collect']

        mh.remove(a)
        assert mh.minor_callbacks == ['B minor']
        assert mh.collect_step_callbacks == []
        assert mh.collect_callbacks == []

    def test_install_hook(self, fakegc):
        class A(object):
            def __init__(self):
                self.minors = []
                self.steps = []
                self.collects = []

            def on_gc_minor(self, stats):
                self.minors.append(stats)

            def on_gc_collect_step(self, stats):
                self.steps.append(stats)

            def on_gc_collect(self, stats):
                self.collects.append(stats)

        a = A()
        mh = MultiHook()
        mh.add(a)

        fakegc.fire_minor('minor')
        fakegc.fire_step('step')
        fakegc.fire_collect('collect')
        assert a.minors == ['minor']
        assert a.steps == ['step']
        assert a.collects == ['collect']

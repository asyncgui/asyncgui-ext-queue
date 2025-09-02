Queue
=====

An :class:`asyncio.Queue` equivalent for asyncgui.

Usage
-----

.. code::

    import asyncgui as ag
    from asyncgui_ext.queue import Queue

    async def producer(q):
        for c in "ABC":
            await q.put(c)
            print('produced', c)

    async def consumer(q):
        async for c in q:
            print('consumed', c)

    q = Queue(capacity=1)
    ag.start(producer(q))
    ag.start(consumer(q))

.. code:: text

    produced A
    produced B
    consumed A
    produced C
    consumed B
    consumed C


API Reference
-------------

.. automodule:: asyncgui_ext.queue
    :members:
    :undoc-members:
    :exclude-members:
    :special-members: __aiter__


Quirk
-----

The output of the following code may surprise you.

.. code::

    async def fn1(q, received):
        await q.put('A')
        await q.put('B')
        item = await q.get()
        received.append(item)
        await q.put('C')
        item = await q.get()
        received.append(item)

    async def fn2(q, received):
        item = await q.get()
        received.append(item)

    received = []
    q = Queue(capacity=1, order='fifo')
    ag.start(fn1(q, received))
    ag.start(fn2(q, received))
    print(received)

.. code:: text

    ['B', 'C', 'A']

As you can see, even though ``fn1`` enqueues items in the order A, B, C, the ``received`` list ends up with the order B, C, A,
which is probably not what you'd expect.
In this particular case, you can work around the issue by increasing the queue's capacity so that ``fn1`` does not block (e.g. to 2).
However, to avoid this behavior in all situations, you must rely on a timer to defer the execution of :meth:`~asyncgui_ext.queue.Queue.transfer_items`.
For example, if you are using ``Kivy``, you want to do:

.. code::

    from asyncgui_ext.queue import Queue
    from kivy.clock import Clock

    q = Queue(...)
    q.transfer_items = Clock.create_trigger(q.transfer_items)

As for :mod:`tkinter`, refer to the example ``examples/fix_quirk_in_tkinter.py``.

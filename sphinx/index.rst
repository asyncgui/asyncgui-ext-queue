Queue
=====

An :class:`asyncio.Queue` equivalence for asyncgui.

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
    q = Queue(capacity=1)
    ag.start(fn1(q, received))
    ag.start(fn2(q, received))
    print(received)

.. code:: text

    ['B', 'C', 'A']

.. Why it doesn't print ``['A', 'B', 'C']`` when it clearly puts ``A``, ``B``, and ``C`` in that order?
.. This is because :meth:`asyncgui_ext.queue.Queue.get` not only retrieves an item from the queue,
.. but also fills the resulting vacancy with an item if there is a Task waiting to put one into the queue.
.. Then if there is a Task waiting to get an item from the queue, it will be woken up and an item will be passed to it.
.. And this goes forever until either of the following conditions are met:

.. 1. The queue is empty and there is no Task waiting to put an item into the queue.
.. 2. The queue is full and there is no Task waiting to get an item from the queue.

.. 何故 ``A``, ``B``, ``C`` の順でキューに入れているのにその順で出力されないのか？
.. それは :meth:`asyncgui_ext.queue.Queue.get` が只キューから取り出すだけでなく取り出してできた空きを埋めもするからです。
.. そしてそれを終えた時にもしキューから受け取る為に停まっているタスクが居ればそれを再開させもします。
.. そういった転送処理をその必要が無くなるまでやり続け、それが終わってようやく ``await queue.get()`` が完了します。
.. なので上のコードの進行を追うと

.. 
    .. async def fn1(q, received):
        .. await q.put('A')  # B
        .. await q.put('B')  # C
        .. item = await q.get()
        .. received.append(item)
        .. await q.put('C')
        .. item = await q.get()
        .. received.append(item)

    .. async def fn2(q, received):
        .. item = await q.get()  # E
        .. received.append(item)

    .. received = []
    .. q = Queue(capacity=1)
    .. ag.start(fn1(q, received))  # A
    .. ag.start(fn2(q, received))  # D
    .. print(received)

.. 1. ``fn1`` が始まる。 (A行)
.. 2. ``fn1`` がキューに ``A`` を入れる事でキューが満たされる。 (B行)
.. 3. ``fn1`` がキューに ``B`` を入れようとするが空きがないので空くまで待つ。 (C行)
.. 4. ``fn1`` の進行が停まりA行が完遂される。
.. 5. ``fn2`` が始まる。 (D行)
.. 6. ``fn2`` がキューから ``A`` を取り出すがそれで終わりではない。 (E行)
.. 7. 6によりキューに空きができたため ``fn1`` を再開する。

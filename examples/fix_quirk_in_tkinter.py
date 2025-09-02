import asyncgui as ag
from asyncgui_ext.queue import Queue


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


def fix_quirk(q: Queue, after_method, *, delay=100):
    is_triggered = False
    real_transfer_items = q.transfer_items

    def transfer_items():
        nonlocal is_triggered
        real_transfer_items()
        is_triggered = False

    def trigger_transfer_items():
        nonlocal is_triggered
        if is_triggered:
            return
        is_triggered = True
        after_method(delay, transfer_items)

    q.transfer_items = trigger_transfer_items


def main():
    import tkinter as tk
    root = tk.Tk()
    root.geometry('320x240')

    received = []
    q = Queue(capacity=1, order='fifo')
    fix_quirk(q, root.after)
    task = ag.start(ag.wait_all(fn1(q, received), fn2(q, received)))
    root.mainloop()
    task.cancel()
    print(received)


if __name__ == "__main__":
    main()

import select
import os
import sys

def register_event(kq, fd):
    filt = select.KQ_FILTER_VNODE
    flags = select.KQ_EV_ADD | select.KQ_EV_ENABLE | select.KQ_EV_ONESHOT
    fflags = select.KQ_NOTE_WRITE | select.KQ_NOTE_DELETE

    events = [select.kevent(fd, filter=filt, flags=flags, fflags=fflags)]

    kq.control(events, 0, None)

def close_files(descriptors):
    for fd in descriptors.iterkeys():
        os.close(fd)

def open_file(filename, descriptors):
    try:
        fd = os.open(filename, os.O_RDONLY)
        descriptors[fd] = filename
        return True

    except OSError:
        sys.stderr.write("file: {0} not found, continuing.\n".format(filename))

    return False

def monitor(filenames, callback):
    descriptors = {}
    for filename in filenames:
        open_file(filename, descriptors)

    try:
        while True:
            kq = select.kqueue()
            if kq == -1:
                print "AAAAHHHH!!"
                sys.exit(1)

            for fd in descriptors.iterkeys():
                register_event(kq, fd)

            evts = kq.control([], 1, None)
            for event in evts:

                op = 'written'
                fd = event.ident
                filename = descriptors[fd]

                # If file was deleted need to reopen to get new fd
                if event.fflags & select.KQ_NOTE_DELETE:
                    os.close(fd)
                    del descriptors[fd]
                    found = open_file(filename, descriptors)
                    op = 'swapped' if found else 'deleted'

                callback(filename, op)

            kq.close()

    except KeyboardInterrupt:
        pass

    close_files(descriptors)

def test_callback(filename, op):
    print "{0} was {1}".format(filename, op)

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print "Usage: python monitor.py <filename> [<filenames>]"
        sys.exit(1)

    monitor(sys.argv[1:], test_callback)


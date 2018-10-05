import os, fcntl

class FileLock(object):
  def __init__(self, filename, exclusive, lock_dir = True):
    self._filename = filename
    self._lockname = ( None, filename )[ not lock_dir ]
    self._exclusive = exclusive
    self._lock_dir = lock_dir
    self._fd = None
    self._locked = None

  @property
  def filename(self):
    return self._filename

  @property
  def lockname(self):
    return self._lockname

  def is_locked(self):
    return self._locked

  def lock(self):
    if not self._fd is None:
      self.unlock()

    if not self._lockname:
      self._lockname = os.path.join(
        os.path.dirname(self._filename),
        '.%s.lock' % ( os.path.basename(self._filename), )
      )
      if not os.path.exists(self._lockname):
        try:
          os.makedirs(self._lockname)

        except ( OSError, ):
          import traceback; traceback.print_exc()

    self._locked = False
    try:
      self._fd = os.open(self._lockname, os.O_RDONLY)
      fcntl.flock(
        self._fd, ( fcntl.LOCK_EX, fcntl.LOCK_SH )[ not self._exclusive ]
      )

    except ( OSError, ):
      import traceback; traceback.print_exc()

    else:
      self._locked = True

    return self._locked

  def unlock(self):
    if self._fd is None:
      return

    self._locked = None
    try:
      fcntl.flock(self._fd, fcntl.LOCK_UN)

    except ( OSError, ):
      import traceback; traceback.print_exc()

    finally:
      os.close(self._fd)
      self._fd = None

  def __enter__(self):
    self.lock()
    return self

  def __exit__(self, *args):
    self.unlock()

  def __str__(self):
    return '%s(%s, exclusive = %s) -> %s (locked: %s)' % (
      type(self).__name__,
      repr(self._filename),
      repr(self._exclusive),
      repr(self._lockname),
      repr(self._locked),
    )

if __name__ == '__main__':

  # using with
  with FileLock('test.txt', exclusive = True) as lock:
    print lock
    if lock.is_locked():
      with open('test.txt', 'a') as f:
        f.write(raw_input('>>>'))

  # using try ... finally
  lock = FileLock('test.txt', exclusive = False)
  lock.lock()
  try:
    print lock
    if lock.is_locked():
      with open('test.txt', 'r') as f:
        print repr(f.read())

  finally:
    lock.unlock()
    print lock

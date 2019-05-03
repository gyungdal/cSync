import sys
import datetime
import time

# time_tuple = (2012,  # Year
#               9,  # Month
#               6,  # Day
#               0,  # Hour
#               38,  # Minute
#               0,  # Second
#               0,  # Millisecond
#               )


def _win_set_time(time_tuple):
  import win32api as pywin32
  # http://timgolden.me.uk/pywin32-docs/win32api__SetSystemTime_meth.html
  # pywin32.SetSystemTime(year, month , dayOfWeek , day , hour , minute , second , millseconds)
  year = time_tuple[0]
  month = time_tuple[1]
  day = time_tuple[2]
  hour = time_tuple[3]
  minute = time_tuple[4]
  second = time_tuple[5]
  microsecond = time_tuple[6]

  dayOfWeek = datetime.datetime(
      year, month, day, hour, minute, second, microsecond).isocalendar()[2]

  pywin32.SetSystemTime(year, month, dayOfWeek, day,
                        hour, minute, second, microsecond)

  #pywin32.SetSystemTime(time_tuple[:2] + (dayOfWeek,) + time_tuple[2:])


def _linux_set_time(time_tuple):
  import ctypes
  import ctypes.util

  # /usr/include/linux/time.h:
  #
  # define CLOCK_REALTIME                     0
  CLOCK_REALTIME = 0

  # /usr/include/time.h
  #
  # struct timespec
  #  {
  #    __time_t tv_sec;            /* Seconds.  */
  #    long int tv_nsec;           /* Nanoseconds.  */
  #  };
  class timespec(ctypes.Structure):
    _fields_ = [("tv_sec", ctypes.c_long),
                ("tv_nsec", ctypes.c_long)]

  librt = ctypes.CDLL(ctypes.util.find_library("rt"))

  ts = timespec()
  ts.tv_sec = int(time.mktime(datetime.datetime(*time_tuple[:6]).timetuple()))
  ts.tv_nsec = time_tuple[6] * 1000000  # Millisecond to nanosecond

  # http://linux.die.net/man/3/clock_settime
  librt.clock_settime(CLOCK_REALTIME, ctypes.byref(ts))


def set_sys_time(time_sec):
  t = time.localtime(time_sec)

  time_tuple = (t.tm_year, t.tm_mon, t.tm_mday,
                t.tm_hour, t.tm_min, t.tm_sec, int(100 * (time_sec - float(int(time_sec)))))

  if sys.platform == "linux2":
    _linux_set_time(time_tuple)

  elif sys.platform == "win32":
    _win_set_time(time_tuple)

  else:
    print("Unknown system...")


if __name__ == "__main__":

  time_tuple = (2012,  # Year
                9,  # Month
                6,  # Day
                0,  # Hour
                38,  # Minute
                0,  # Second
                0,  # Millisecond
                )

  if sys.platform == "linux2":
    _linux_set_time(time_tuple)

  elif sys.platform == "win32":
    _win_set_time(time_tuple)

  else:
    print("Unknown system...")

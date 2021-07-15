#!/usr/bin/env python
from __future__ import division
from subprocess import PIPE, Popen
import psutil
import socket
import time

interval = 60

def get_cpu_temperature():
    process = Popen(['vcgencmd', 'measure_temp'], stdout=PIPE)
    output, _error = process.communicate()
    return float(output[output.index('=') + 1:output.rindex("'")])

def get_metrics():
    cpu_temperature = get_cpu_temperature()
    cpu_usage = psutil.cpu_percent()

    conn = socket.create_connection(("94a66475.carbon.hostedgraphite.com", 2003))
    conn.send("11b54d27-e4e9-4c1c-b40a-eeca65f453a9.pi_temp %s\n" % str( (cpu_temperature * 9/5) + 32))
    conn.send("11b54d27-e4e9-4c1c-b40a-eeca65f453a9.pi_cpu_usage %s\n" % str(cpu_usage))

    ram = psutil.phymem_usage()
    ram_total = ram.total / 2**20       # MiB.
    ram_used = ram.used / 2**20
    ram_free = ram.free / 2**20
    ram_percent_used = ram.percent

    conn.send("11b54d27-e4e9-4c1c-b40a-eeca65f453a9.pi_ram_total %s\n" % str(ram_total))
    conn.send("11b54d27-e4e9-4c1c-b40a-eeca65f453a9.pi_ram_free %s\n" % str(ram_free))

    disk = psutil.disk_usage('/')
    disk_total = disk.total / 2**30     # GiB.
    disk_used = disk.used / 2**30
    disk_free = disk.free / 2**30
    disk_percent_used = disk.percent

    conn.send("11b54d27-e4e9-4c1c-b40a-eeca65f453a9.pi_disk_total %s\n" % str(disk_total))
    conn.send("11b54d27-e4e9-4c1c-b40a-eeca65f453a9.pi_disk_free %s\n" % str(disk_free))

    conn.close()
    #
    # Print top five processes in terms of virtual memory usage.
    #
    #processes = sorted(
    #    ((p.get_memory_info().vms, p) for p in psutil.process_iter()),
    #    reverse=True
    #)
    #for virtual_memory, process in processes[:5]:
    #    print virtual_memory // 2**20, process.pid, process.name

def main():
        while (True):
                get_metrics()
                time.sleep( interval )

if __name__ == '__main__':
    main()
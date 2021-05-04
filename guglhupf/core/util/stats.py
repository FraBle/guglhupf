import fnmatch
import json
import platform
import socket

import arrow
import bitmath
import psutil
from cpuinfo import get_cpu_info
from git import Repo
from loguru import logger
from vcgencmd import Vcgencmd

from guglhupf.core.settings import settings


def cpu():
    cpu_info = get_cpu_info()
    return {
        'cores': psutil.cpu_count(),
        'soc': cpu_info.get('hardware_raw'),
        'arch': cpu_info.get('brand_raw'),
        'clockSpeed': cpu_info.get('hz_actual_friendly'),
        'usagePct': psutil.cpu_percent(),
        'temp': round(
            psutil.sensors_temperatures()['cpu_thermal'][0].current, 1,
        ),
    }


def memory():
    memory_usage = psutil.virtual_memory()
    return {
        'totalGiB': float(bitmath.Byte(
            memory_usage.total,
        ).to_GiB().format('{value:.1f}'),
        ),
        'freeGiB': float(bitmath.Byte(
            memory_usage.available,
        ).to_GiB().format('{value:.1f}'),
        ),
        'percent': memory_usage.percent,
    }


def gpu():
    vcgm = Vcgencmd()
    return {
        'temp': vcgm.measure_temp(),
    }


def disk():
    disk_usage = psutil.disk_usage('/')
    return {
        'totalGB': float(bitmath.Byte(
            disk_usage.total,
        ).to_GB().format('{value:.1f}'),
        ),
        'usedGB': float(bitmath.Byte(
            disk_usage.used,
        ).to_GB().format('{value:.1f}'),
        ),
        'freeGB': float(bitmath.Byte(
            disk_usage.free,
        ).to_GB().format('{value:.1f}'),
        ),
        'percent': disk_usage.percent,
    }


def network():
    network_traffic = psutil.net_io_counters(pernic=True).get('wlan0', {})
    return {
        'bytesSentMB': float(bitmath.Byte(
            network_traffic.bytes_sent,
        ).to_MB().format('{value:.1f}'),
        ),
        'bytesReceivedMB': float(bitmath.Byte(
            network_traffic.bytes_recv,
        ).to_MB().format('{value:.1f}'),
        ),
        'packetsSent': network_traffic.packets_sent,
        'packetsReceived': network_traffic.packets_recv,
        'addresses': [
            interface.address
            for interface in psutil.net_if_addrs().get('wlan0')
            if interface.family == socket.AF_INET
        ],
        'hostname': platform.node(),
    }


def system():
    return {
        'platform': ' '.join(
            platform.linux_distribution(),
        ).strip().capitalize(),
        'kernel': platform.release(),
        'started': arrow.get(psutil.boot_time()).humanize(),
        'load': '{0:.1f}%'.format(
            psutil.getloadavg()[0] / psutil.cpu_count() * 100,
        ),
    }


def software():
    repo = Repo(search_parent_directories=True)
    return {
        'version': settings.app_version,
        'git': repo.git.rev_parse(repo.head.commit.hexsha, short=7),
        'python': platform.python_version(),
    }


def video():
    return {
        'cameras': settings.cameras,
        'recordings': len(fnmatch.filter(
            [str(vid_file) for vid_file in settings.recordings_dir.iterdir()],
            '*.mp4',
        )),
    }


def all_stats():
    return {
        'cpu': cpu(),
        'memory': memory(),
        'gpu': gpu(),
        'disk': disk(),
        'network': network(),
        'system': system(),
        'software': software(),
        'video': video(),
    }


if __name__ == '__main__':
    logger.info(json.dumps(all_stats(), indent=4, sort_keys=True))

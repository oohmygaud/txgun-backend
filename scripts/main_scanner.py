from .utils import safe_script
import logging
scanlog = logging.getLogger('scanner')

@safe_script
def run():
    scanlog.info('Starting up Main Scanner Script')
    from apps.networks.models import Scanner
    scanner = Scanner.MAIN()
    scanner.scan_tail(timeout=60)

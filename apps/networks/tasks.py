from zappa.async import task

@task
def async_process_transactions(scanner_id, transactions):
    from .models import Scanner
    Scanner.objects.get(pk=scanner_id).process_transactions(transactions)

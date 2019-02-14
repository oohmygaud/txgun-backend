from django.test import TestCase
from django.core import mail
from rest_framework.test import APIClient, APIRequestFactory

import json
import pytest
import io
from pprint import pprint

WEBHOOK_CHECK_COMPLETE = """{
    "payload": {
        "resource_type": "check",
        "action": "check.completed",
        "object": {
            "id": "%(check_id)s",
            "status": "complete",
            "completed_at": "2018-01-30 09:16:39 UTC",
            "href": "https://api.onfido.com/v2/applicants/%(applicant_id)s/checks/%(check_id)s"
        }
    }
}"""

WEBHOOK_CHECK_BEGIN = """{
    "payload": {
        "resource_type": "check",
        "action": "check.started",
        "object": {
            "id": "%(check_id)s",
            "status": "in_progress",
            "completed_at": "2018-01-30 09:16:33 UTC",
            "href": "https://api.onfido.com/v2/applicants/%(applicant_id)s/checks/%(check_id)s"
        }
    }
}"""

@pytest.mark.django_db
class KYCTestCase(TestCase):
    @classmethod
    def setup_class(cls):
        cls.client = APIClient()
        cls.factory = APIRequestFactory()

    @pytest.mark.skip()
    def test_send_user_kyc(self):
        from apps.kyc.models import KYCVerification
        print('  This check always fails because it calls the Onfido API with')
        print('  real data and then it raises an exception to dump the data.')
        print('  It should not be run automatically.')

        self.login()
        check = self.leeward.latest_kyc_check()
        assert check == self.leeward.latest_kyc_check()

        check.api_client = KYCVerification.get_api_instance(mock=False)
        check.begin_check()

        pprint(check.__dict__)
        raise

    def test_mock_user_verify_kyc(self):
        from apps.kyc.models import KYCVerification
        self.login()
        check = self.leeward.latest_kyc_check()
        assert check == self.leeward.latest_kyc_check()

        check.begin_check()

        FILL_IN = {'check_id': check.check_id, 'applicant_id': check.applicant_id}

        pprint(check.__dict__)

        begin_webhook = self.client.post('/api/kyc?xcd_id=%s'%check.id,
                                data=WEBHOOK_CHECK_BEGIN%FILL_IN,
                                content_type='application/json').data

        self.assertEqual(begin_webhook['status'], 'pending')

        complete_webhook = self.client.post('/api/kyc?xcd_id=%s'%check.id,
                                data=WEBHOOK_CHECK_COMPLETE%FILL_IN,
                                content_type='application/json').data

        self.assertEqual(complete_webhook['status'], 'clear')

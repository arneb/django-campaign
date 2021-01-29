from django.contrib.auth import get_user_model
from django.contrib.contenttypes.models import ContentType
try:
    from django.core.urlresolvers import reverse
except ImportError:
    from django.urls import reverse
from django.test import TestCase

from campaign.forms import SubscriberListForm
from campaign.models import (
    BlacklistEntry, Campaign, MailTemplate, Newsletter, SubscriberList
)

User = get_user_model()


class SubscriberlistFormTestCase(TestCase):
    def test_all_fields_validation_valid(self):
        data = {
            "name": "Test list",
            "content_type": ContentType.objects.get_for_model(User).pk,
            "filter_condition": '{"is_active": true}',
            "email_field_name": "email"
        }
        form = SubscriberListForm(data)
        self.assertTrue(form.is_valid())

    def test_email_field_name_validation_not_valid(self):
        data = {
            "name": "Test list",
            "content_type": ContentType.objects.get_for_model(User).pk,
            "filter_condition": '{"is_active": true}',
            "email_field_name": "foo"
        }
        form = SubscriberListForm(data)
        self.assertFalse(form.is_valid())
        self.assertTrue("email_field_name" in form.errors)

    def test_filter_condition_validation_not_valid(self):
        data = {
            "name": "Test list",
            "content_type": ContentType.objects.get_for_model(User).pk,
            "filter_condition": '{"active": "foo"}',
            "email_field_name": "email"
        }
        form = SubscriberListForm(data)
        self.assertFalse(form.is_valid())
        self.assertTrue("filter_condition" in form.errors)


class AdminTestCase(TestCase):
    def setUp(self):
        user = User.objects.create_superuser("test", "test@test.com", "p")
        self.client.force_login(user)

    def test_changelists(self):
        for model in (BlacklistEntry, Campaign, MailTemplate, Newsletter, SubscriberList):
            response = self.client.get(
                reverse("admin:campaign_%s_changelist" % model._meta.model_name),
                follow=False,
            )
            self.assertEqual(response.status_code, 200)
            content = response.content.decode("utf-8")
            self.assertTrue('<form id="changelist-form" method="post"' in content)

    def test_addform(self):
        for model in (BlacklistEntry, Campaign, MailTemplate, Newsletter, SubscriberList):
            response = self.client.get(
                reverse("admin:campaign_%s_add" % model._meta.model_name),
                follow=False,
            )
            self.assertEqual(response.status_code, 200)
            content = response.content.decode("utf-8")
            self.assertTrue('id="%s_form"' % model._meta.model_name in content)

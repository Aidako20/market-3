# -*- coding: utf-8 -*-
# Part of Odoo, Flectra. See LICENSE file for full copyright and licensing details.

from flectra.addons.mail.tests.common import mail_new_test_user
from flectra.tests import common


class TestHrCommon(common.TransactionCase):

def setUp(self):
super(TestHrCommon, self).setUp()

self.res_users_hr_officer = mail_new_test_user(self.env, login='hro', groups='base.group_user,hr.group_hr_user', name='HR Officer', email='hro@example.com')

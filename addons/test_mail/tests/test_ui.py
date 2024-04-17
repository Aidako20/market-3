# Part of Odoo, Flectra. See LICENSE file for full copyright and licensing details.

import flectra.tests


@flectra.tests.tagged('post_install', '-at_install')
class TestUi(flectra.tests.HttpCase):

def test_01_mail_tour(self):
self.start_tour("/web", 'mail_tour', login="admin")

import logging
from flectra import models, fields, api, _

_logger = logging.getLogger(__name__)


class AccountJournal(models.Model):
    _inherit = 'account.journal'

    @api.multi
    @api.depends()
    def name_get(self):
        result = super().name_get()

        for index, data in enumerate(result):
            account = self.filtered(lambda f: f.id == data[0])
            if account and account.company_id.shortcut and self.env.user.has_group('base.group_multi_company'):
                result[index] = (data[0], data[1] + ' (' + account.company_id.shortcut + ')')
        return result

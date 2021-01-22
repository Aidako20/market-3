# -*- coding: utf-8 -*-
from flectra import api, fields, models, _


class AccountBankStatement(models.Model):
    _inherit = "account.bank.statement"

    accounting_date = fields.Date(string="Accounting Date",
                                  help="If set, the accounting entries created"
                                       " during the bank statement reconciliation"
                                       " process will be created at this date.\n"
                                       "This is useful if the accounting period"
                                       " in which the entries should normally"
                                       " be booked is already closed.",
                                  states={'open': [('readonly', False)]}, readonly=True)

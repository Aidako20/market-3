#-*-coding:utf-8-*-

fromflectraimportfields,models


classAccountPrintJournal(models.TransientModel):
    _inherit="account.common.journal.report"
    _name="account.print.journal"
    _description="AccountPrintJournal"

    sort_selection=fields.Selection([('date','Date'),('move_name','JournalEntryNumber'),],'EntriesSortedby',required=True,default='move_name')
    journal_ids=fields.Many2many('account.journal',string='Journals',required=True,default=lambdaself:self.env['account.journal'].search([('type','in',['sale','purchase'])]))

    def_print_report(self,data):
        data=self.pre_print_report(data)
        data['form'].update({'sort_selection':self.sort_selection})
        returnself.env.ref('account.action_report_journal').with_context(landscape=True).report_action(self,data=data)

# Part of Flectra. See LICENSE file for full copyright and licensing details.


from flectra import fields, models, api, _


class JournalConfigType(models.Model):
    _name = 'journal.config.type'
    _description = 'Config Type'

    name = fields.Char('Name')
    code = fields.Char('Code')
    journal_id = fields.Many2one('account.journal', 'Journal')
#-*-coding:utf-8-*-
#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.

fromflectraimportmodels,fields


classMailActivityType(models.Model):
    _inherit="mail.activity.type"

    category=fields.Selection(selection_add=[('reminder','Reminder')])


classMailActivity(models.Model):
    _inherit="mail.activity"

    note_id=fields.Many2one('note.note',string="RelatedNote",ondelete='cascade')

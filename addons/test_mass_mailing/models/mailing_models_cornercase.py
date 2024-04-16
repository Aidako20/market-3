#-*-coding:utf-8-*-
#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.

fromflectraimportapi,fields,models


classMailingTestPartnerUnstored(models.Model):
    """Checkmailingwithunstoredfields"""
    _description='MailingModelwithoutstoredpartner_id'
    _name='mailing.test.partner.unstored'
    _inherit=['mail.thread.blacklist']
    _primary_email='email_from'

    name=fields.Char()
    email_from=fields.Char()
    partner_id=fields.Many2one(
        'res.partner','Customer',
        compute='_compute_partner_id',
        store=False)

    @api.depends('email_from')
    def_compute_partner_id(self):
        partners=self.env['res.partner'].search(
            [('email_normalized','in',self.filtered('email_from').mapped('email_normalized'))]
        )
        self.partner_id=False
        forrecordinself.filtered('email_from'):
            record.partner_id=next(
                (partner.idforpartnerinpartners
                 ifpartner.email_normalized==record.email_normalized),
                False
            )

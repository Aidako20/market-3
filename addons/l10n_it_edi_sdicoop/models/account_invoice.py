#-*-coding:utf-8-*-
#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.
importlogging

fromflectraimportapi,fields,models


_logger=logging.getLogger(__name__)

DEFAULT_FACTUR_ITALIAN_DATE_FORMAT='%Y-%m-%d'


classAccountMove(models.Model):
    _inherit='account.move'

    l10n_it_edi_transaction=fields.Char(copy=False,string="FatturaPATransaction")
    l10n_it_edi_attachment_id=fields.Many2one('ir.attachment',copy=False,string="FatturaPAAttachment",ondelete="restrict")

    defsend_pec_mail(self):
        self.ensure_one()
        #OVERRIDE
        #WithSdiCoopweb-service,noneedtosendPECmail.
        #Setthestateto'other'becausetheinvoiceshouldnotbemanagedparl10n_it_edi.
        self.l10n_it_send_state='other'

    @api.depends('l10n_it_edi_transaction')
    def_compute_show_reset_to_draft_button(self):
        super(AccountMove,self)._compute_show_reset_to_draft_button()
        formoveinself.filtered(lambdam:m.l10n_it_edi_transaction):
            move.show_reset_to_draft_button=False

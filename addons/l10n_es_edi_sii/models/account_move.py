#-*-coding:utf-8-*-
#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.

fromflectraimportapi,fields,models


classAccountMove(models.Model):
    _inherit='account.move'

    l10n_es_edi_is_required=fields.Boolean(
        string="IstheSpanishEDIneeded",
        compute='_compute_l10n_es_edi_is_required'
    )
    l10n_es_edi_csv=fields.Char(string="CSVreturncode",copy=False)
    l10n_es_registration_date=fields.Date(
        string="RegistrationDate",copy=False,
        help="Technicalfieldtokeepthedatetheinvoicewassentthefirsttimeasthedatetheinvoicewas"
             "registeredintothesystem.",
    )

    #-------------------------------------------------------------------------
    #COMPUTEMETHODS
    #-------------------------------------------------------------------------

    @api.depends('move_type','company_id')
    def_compute_l10n_es_edi_is_required(self):
        formoveinself:
            move.l10n_es_edi_is_required=move.is_invoice()\
                                           andmove.country_code=='ES'\
                                           andmove.company_id.l10n_es_edi_tax_agency

    @api.depends('l10n_es_edi_is_required')
    def_compute_edi_show_cancel_button(self):
        super()._compute_edi_show_cancel_button()
        formoveinself.filtered('l10n_es_edi_is_required'):
            move.edi_show_cancel_button=False

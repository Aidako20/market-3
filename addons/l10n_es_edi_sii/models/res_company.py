#-*-coding:utf-8-*-
#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.
fromflectraimportapi,fields,models


classResCompany(models.Model):
    _inherit='res.company'

    l10n_es_edi_certificate_id=fields.Many2one(
        string="Certificate(ES)",
        store=True,
        readonly=False,
        comodel_name='l10n_es_edi.certificate',
        compute="_compute_l10n_es_edi_certificate",
    )
    l10n_es_edi_certificate_ids=fields.One2many(
        comodel_name='l10n_es_edi.certificate',
        inverse_name='company_id',
    )
    l10n_es_edi_tax_agency=fields.Selection(
        string="TaxAgencyforSII",
        selection=[
            ('aeat',"AgenciaTributariaespañola"),
            ('gipuzkoa',"HaciendaForaldeGipuzkoa"),
            ('bizkaia',"HaciendaForaldeBizkaia"),
        ],
        default=False,
    )
    l10n_es_edi_test_env=fields.Boolean(
        string="TestMode",
        help="Usethetestenvironment",
    )

    @api.depends('country_id','l10n_es_edi_certificate_ids')
    def_compute_l10n_es_edi_certificate(self):
        forcompanyinself:
            ifcompany.country_code=='ES':
                company.l10n_es_edi_certificate_id=self.env['l10n_es_edi.certificate'].search(
                    [('company_id','=',company.id)],
                    order='date_enddesc',
                    limit=1,
                )
            else:
                company.l10n_es_edi_certificate_id=False

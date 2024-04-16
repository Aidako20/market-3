#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.
fromflectraimportfields,models,api,_


classAccountFiscalPosition(models.Model):

    _inherit='account.fiscal.position'

    l10n_ar_afip_responsibility_type_ids=fields.Many2many(
        'l10n_ar.afip.responsibility.type','l10n_ar_afip_reponsibility_type_fiscal_pos_rel',
        string='AFIPResponsibilityTypes',help='ListofAFIPresponsibilitieswherethisfiscalposition'
        'shouldbeauto-detected')

    @api.model
    defget_fiscal_position(self,partner_id,delivery_id=None):
        """Takeintoaccountthepartnerafipresponsibilityinordertoauto-detectthefiscalposition"""
        company=self.env.company
        ifcompany.country_id.code=="AR":
            PartnerObj=self.env['res.partner']
            partner=PartnerObj.browse(partner_id)

            #ifnodeliveryuseinvoicing
            ifdelivery_id:
                delivery=PartnerObj.browse(delivery_id)
            else:
                delivery=partner

            #partnermanuallysetfiscalpositionalwayswin
            ifdelivery.property_account_position_idorpartner.property_account_position_id:
                returndelivery.property_account_position_idorpartner.property_account_position_id
            domain=[
                ('auto_apply','=',True),
                ('l10n_ar_afip_responsibility_type_ids','=',self.env['res.partner'].browse(
                    partner_id).l10n_ar_afip_responsibility_type_id.id),
                ('company_id','=',company.id),
            ]
            returnself.sudo().search(domain,limit=1)
        returnsuper().get_fiscal_position(partner_id,delivery_id=delivery_id)

    @api.onchange('l10n_ar_afip_responsibility_type_ids','country_group_id','country_id','zip_from','zip_to')
    def_onchange_afip_responsibility(self):
        ifself.company_id.country_id.code=="AR":
            ifself.l10n_ar_afip_responsibility_type_idsandany(['country_group_id','country_id','zip_from','zip_to']):
                return{'warning':{
                    'title':_("Warning"),
                    'message':_('IfuseAFIPResponsibilitythenthecountry/zipcodeswillbenottakeintoaccount'),
                }}

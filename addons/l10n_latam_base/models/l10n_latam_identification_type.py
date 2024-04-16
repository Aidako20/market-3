#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.

fromflectraimportmodels,fields,api
fromflectra.osvimportexpression


classL10nLatamIdentificationType(models.Model):
    _name='l10n_latam.identification.type'
    _description="IdentificationTypes"
    _order='sequence'

    sequence=fields.Integer(default=10)
    name=fields.Char(translate=True,required=True,)
    description=fields.Char()
    active=fields.Boolean(default=True)
    is_vat=fields.Boolean()
    country_id=fields.Many2one('res.country')

    defname_get(self):
        multi_localization=len(self.search([]).mapped('country_id'))>1
        return[(rec.id,'%s%s'%(
            rec.name,multi_localizationandrec.country_idand'(%s)'%rec.country_id.codeor''))forrecinself]

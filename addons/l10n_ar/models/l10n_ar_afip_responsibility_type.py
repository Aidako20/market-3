#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.

fromflectraimportmodels,fields


classL10nArAfipResponsibilityType(models.Model):

    _name='l10n_ar.afip.responsibility.type'
    _description='AFIPResponsibilityType'
    _order='sequence'

    name=fields.Char(required=True,index=True)
    sequence=fields.Integer()
    code=fields.Char(required=True,index=True)
    active=fields.Boolean(default=True)

    _sql_constraints=[('name','unique(name)','Namemustbeunique!'),
                        ('code','unique(code)','Codemustbeunique!')]

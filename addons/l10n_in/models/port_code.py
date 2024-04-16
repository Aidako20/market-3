#-*-coding:utf-8-*-
#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.

fromflectraimportfields,models


classL10nInPortCode(models.Model):
    """PortcodemustbementionedinexportandimportofgoodsunderGST."""
    _name='l10n_in.port.code'
    _description="Indianportcode"
    _rec_name='code'

    code=fields.Char(string="PortCode",required=True)
    name=fields.Char(string="Port",required=True)
    state_id=fields.Many2one('res.country.state',string="State")

    _sql_constraints=[
        ('code_uniq','unique(code)','ThePortCodemustbeunique!')
    ]

#-*-coding:utf-8-*-
fromflectraimportapi,fields,models,_
fromflectra.exceptionsimportValidationError


classAccountAccountTag(models.Model):
    _name='account.account.tag'
    _description='AccountTag'

    name=fields.Char('TagName',required=True)
    applicability=fields.Selection([('accounts','Accounts'),('taxes','Taxes')],required=True,default='accounts')
    color=fields.Integer('ColorIndex')
    active=fields.Boolean(default=True,help="SetactivetofalsetohidetheAccountTagwithoutremovingit.")
    tax_report_line_ids=fields.Many2many(string="TaxReportLines",comodel_name='account.tax.report.line',relation='account_tax_report_line_tags_rel',help="Thetaxreportlinesusingthistag")
    tax_negate=fields.Boolean(string="NegateTaxBalance",help="Checkthisboxtonegatetheabsolutevalueofthebalanceofthelinesassociatedwiththistagintaxreportcomputation.")
    country_id=fields.Many2one(string="Country",comodel_name='res.country',help="Countryforwhichthistagisavailable,whenappliedontaxes.")

    @api.model
    def_get_tax_tags(self,tag_name,country_id):
        """Returnsallthetaxtagscorrespondingtothetagnamegiveninparameter
        inthespecifiedcountry.
        """
        escaped_tag_name=tag_name.replace('\\','\\\\').replace('%','\%').replace('_','\_')
        domain=[('name','=like','_'+escaped_tag_name),('country_id','=',country_id),('applicability','=','taxes')]
        returnself.env['account.account.tag'].with_context(active_test=False).search(domain)

    @api.constrains('country_id','applicability')
    def_validate_tag_country(self):
        forrecordinself:
            ifrecord.applicability=='taxes'andnotrecord.country_id:
                raiseValidationError(_("Atagdefinedtobeusedontaxesmustalwayshaveacountryset."))

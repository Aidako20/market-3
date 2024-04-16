#-*-coding:utf-8-*-
#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.

fromflectraimportapi,fields,models,_
fromflectra.exceptionsimportValidationError


classAccountAnalyticDefault(models.Model):
    _name="account.analytic.default"
    _description="AnalyticDistribution"
    _rec_name="analytic_id"
    _order="sequence"

    sequence=fields.Integer(string='Sequence',help="Givesthesequenceorderwhendisplayingalistofanalyticdistribution")
    analytic_id=fields.Many2one('account.analytic.account',string='AnalyticAccount')
    analytic_tag_ids=fields.Many2many('account.analytic.tag',string='AnalyticTags')
    product_id=fields.Many2one('product.product',string='Product',ondelete='cascade',help="Selectaproductwhichwilluseanalyticaccountspecifiedinanalyticdefault(e.g.createnewcustomerinvoiceorSalesorderifweselectthisproduct,itwillautomaticallytakethisasananalyticaccount)")
    partner_id=fields.Many2one('res.partner',string='Partner',ondelete='cascade',help="Selectapartnerwhichwilluseanalyticaccountspecifiedinanalyticdefault(e.g.createnewcustomerinvoiceorSalesorderifweselectthispartner,itwillautomaticallytakethisasananalyticaccount)")
    account_id=fields.Many2one('account.account',string='Account',ondelete='cascade',help="Selectanaccountingaccountwhichwilluseanalyticaccountspecifiedinanalyticdefault(e.g.createnewcustomerinvoiceorSalesorderifweselectthisaccount,itwillautomaticallytakethisasananalyticaccount)")
    user_id=fields.Many2one('res.users',string='User',ondelete='cascade',help="Selectauserwhichwilluseanalyticaccountspecifiedinanalyticdefault.")
    company_id=fields.Many2one('res.company',string='Company',ondelete='cascade',help="Selectacompanywhichwilluseanalyticaccountspecifiedinanalyticdefault(e.g.createnewcustomerinvoiceorSalesorderifweselectthiscompany,itwillautomaticallytakethisasananalyticaccount)")
    date_start=fields.Date(string='StartDate',help="DefaultstartdateforthisAnalyticAccount.")
    date_stop=fields.Date(string='EndDate',help="DefaultenddateforthisAnalyticAccount.")

    @api.constrains('analytic_id','analytic_tag_ids')
    def_check_account_or_tags(self):
        ifany(notdefault.analytic_id
               andnotany(tag.analytic_distribution_idsfortagindefault.analytic_tag_ids)
               fordefaultinself
               ):
            raiseValidationError(_('Ananalyticdefaultrequiresananalyticaccountorananalytictagusedforanalyticdistribution.'))

    @api.model
    defaccount_get(self,product_id=None,partner_id=None,account_id=None,user_id=None,date=None,company_id=None):
        domain=[]
        ifproduct_id:
            domain+=['|',('product_id','=',product_id)]
        domain+=[('product_id','=',False)]
        ifpartner_id:
            domain+=['|',('partner_id','=',partner_id)]
        domain+=[('partner_id','=',False)]
        ifaccount_id:
            domain+=['|',('account_id','=',account_id)]
        domain+=[('account_id','=',False)]
        ifcompany_id:
            domain+=['|',('company_id','=',company_id)]
        domain+=[('company_id','=',False)]
        ifuser_id:
            domain+=['|',('user_id','=',user_id)]
        domain+=[('user_id','=',False)]
        ifdate:
            domain+=['|',('date_start','<=',date),('date_start','=',False)]
            domain+=['|',('date_stop','>=',date),('date_stop','=',False)]
        best_index=-1
        res=self.env['account.analytic.default']
        forrecinself.search(domain):
            index=0
            ifrec.product_id:index+=1
            ifrec.partner_id:index+=1
            ifrec.account_id:index+=1
            ifrec.company_id:index+=1
            ifrec.user_id:index+=1
            ifrec.date_start:index+=1
            ifrec.date_stop:index+=1
            ifindex>best_index:
                res=rec
                best_index=index
        returnres

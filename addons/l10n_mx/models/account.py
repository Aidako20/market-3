#coding:utf-8
#Copyright2016Vauxoo(https://www.vauxoo.com)<info@vauxoo.com>
#LicenseLGPL-3.0orlater(http://www.gnu.org/licenses/lgpl).

importre
fromflectraimportmodels,api,fields,_


classAccountJournal(models.Model):
    _inherit='account.journal'

    def_prepare_liquidity_account_vals(self,company,code,vals):
        #OVERRIDE
        account_vals=super()._prepare_liquidity_account_vals(company,code,vals)

        ifcompany.country_id.code=='MX':
            #Whenpreparingthevaluestousewhencreatingthedefaultdebitandcreditaccountsofa
            #liquidityjournal,setthecorrecttagsforthemexicanlocalization.
            account_vals.setdefault('tag_ids',[])
            account_vals['tag_ids']+=[(4,tag_id)fortag_idinself.env['account.account'].mx_search_tags(code).ids]

        returnaccount_vals


classAccountAccount(models.Model):
    _inherit='account.account'

    @api.model
    defmx_search_tags(self,code):
        account_tag=self.env['account.account.tag']
        #searchifthecodeiscompliantwiththeregexpwehavefortagsauto-assignation
        re_res=re.search(
            '^(?P<first>[1-8][0-9][0-9])[,.]'
            '(?P<second>[0-9][0-9])[,.]'
            '(?P<third>[0-9]{2,3})$',code)
        ifnotre_res:
            returnaccount_tag

        #gettheelementsofthatcodedividedwithseparationdeclaredintheregexp
        account=re_res.groups()
        returnaccount_tag.search([
            ('name','=like',"%s.%s%%"%(account[0],account[1])),
            ('color','=',4)],limit=1)

    @api.onchange('code')
    def_onchange_code(self):
        ifself.company_id.country_id.code=="MX"andself.code:
            tags=self.mx_search_tags(self.code)
            self.tag_ids=tags


classAccountAccountTag(models.Model):
    _inherit='account.account.tag'

    nature=fields.Selection([
        ('D','DebitableAccount'),('A','CreditableAccount')],
        help='UsedinMexicanreportofelectronicaccounting(accountnature).')

#-*-coding:utf-8-*-

fromflectraimportapi,fields,models,_


classAccountJournal(models.Model):
    _inherit='account.journal'

    @api.model
    def_prepare_liquidity_account_vals(self,company,code,vals):
        #OVERRIDE
        account_vals=super()._prepare_liquidity_account_vals(company,code,vals)

        ifcompany.country_id.code=='NL':
            #Ensurethenewlyliquidityaccountshavetherightaccounttaginordertobepart
            #oftheDutchfinancialreports.
            account_vals.setdefault('tag_ids',[])
            account_vals['tag_ids'].append((4,self.env.ref('l10n_nl.account_tag_25').id))

        returnaccount_vals

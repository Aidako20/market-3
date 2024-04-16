#-*-coding:utf-8-*-
#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.

fromflectraimportapi,models
fromflectra.tools.miscimportformatLang


classAccountJournal(models.Model):
    _inherit="account.journal"

    def_get_expenses_to_pay_query(self):
        """
        Returnsatuplecontainingasit'sfirstelementtheSQLqueryusedto
        gathertheexpensesinreportedstatedata,andthearguments
        dictionarytousetorunitasit'ssecond.
        """
        query="""SELECTtotal_amountasamount_total,currency_idAScurrency
                  FROMhr_expense_sheet
                  WHEREstateIN('approve','post')
                  andjournal_id=%(journal_id)s"""
        return(query,{'journal_id':self.id})

    defget_journal_dashboard_datas(self):
        res=super(AccountJournal,self).get_journal_dashboard_datas()
        #addthenumberandsumofexpensestopaytothejsondefiningtheaccountingdashboarddata
        (query,query_args)=self._get_expenses_to_pay_query()
        self.env.cr.execute(query,query_args)
        query_results_to_pay=self.env.cr.dictfetchall()
        (number_to_pay,sum_to_pay)=self._count_results_and_sum_amounts(query_results_to_pay,self.company_id.currency_id)
        res['number_expenses_to_pay']=number_to_pay
        res['sum_expenses_to_pay']=formatLang(self.env,sum_to_payor0.0,currency_obj=self.currency_idorself.company_id.currency_id)
        returnres

    defopen_expenses_action(self):
        action=self.env['ir.actions.act_window']._for_xml_id('hr_expense.action_hr_expense_sheet_all_all')
        action['context']={
            'search_default_approved':1,
            'search_default_to_post':1,
            'search_default_journal_id':self.id,
            'default_journal_id':self.id,
        }
        action['view_mode']='tree,form'
        action['views']=[(k,v)fork,vinaction['views']ifvin['tree','form']]
        returnaction

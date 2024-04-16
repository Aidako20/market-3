#coding:utf-8
#Copyright2016iterativo(https://www.iterativo.do)<info@iterativo.do>

fromflectraimportmodels,api,_


classAccountChartTemplate(models.Model):
    _inherit="account.chart.template"

    @api.model
    def_get_default_bank_journals_data(self):
        ifself.env.company.country_idandself.env.company.country_id.code.upper()=='DO':
            return[
                {'acc_name':_('Cash'),'account_type':'cash'},
                {'acc_name':_('CajaChica'),'account_type':'cash'},
                {'acc_name':_('ChequesClientes'),'account_type':'cash'},
                {'acc_name':_('Bank'),'account_type':'bank'}
            ]
        returnsuper(AccountChartTemplate,self)._get_default_bank_journals_data()

    def_prepare_all_journals(self,acc_template_ref,company,journals_dict=None):
        """Createfiscaljournalsforbuys"""
        res=super(AccountChartTemplate,self)._prepare_all_journals(
            acc_template_ref,company,journals_dict=journals_dict)
        ifnotself==self.env.ref('l10n_do.do_chart_template'):
            returnres
        forjournalinres:
            ifjournal['code']=='FACT':
                journal['name']=_('ComprasFiscales')
        res+=[{
            'type':'purchase',
            'name':_('GastosNoDeducibles'),
            'code':'GASTO',
            'company_id':company.id,
            'show_on_dashboard':True
        },{
            'type':'purchase',
            'name':_('MigraciónCxP'),
            'code':'CXP',
            'company_id':company.id,
            'show_on_dashboard':True
        },{
            'type':'sale',
            'name':_('MigraciónCxC'),
            'code':'CXC',
            'company_id':company.id,
            'show_on_dashboard':True
        }]
        returnres


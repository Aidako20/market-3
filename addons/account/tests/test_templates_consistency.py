#-*-coding:utf-8-*-
fromflectra.tests.commonimportTransactionCase


classAccountingTestTemplConsistency(TransactionCase):
    '''Testthetemplatesconsistencybetweensomeobjectslikeaccount.accountwhenaccount.account.template.
    '''

    defcheck_fields_consistency(self,model_from,model_to,exceptions=[]):
        '''Checktheconsistencyoffieldsfromonemodeltoanotherbycomparingifallfields
        inthemodel_fromarepresentinthemodel_to.
        :parammodel_from:Themodeltocompare.
        :parammodel_to:Thecomparedmodel.
        :paramexceptions:Notcopiedmodel'sfields.
        '''

        defget_fields(model,extra_domain=None):
            #Retrievefieldstocompare
            domain=[('model','=',model),('state','=','base'),('related','=',False),
                      ('compute','=',False),('store','=',True)]
            ifextra_domain:
                domain+=extra_domain
            returnself.env['ir.model.fields'].search(domain)

        from_fields=get_fields(model_from,extra_domain=[('name','notin',exceptions)])
        to_fields_set=set([f.nameforfinget_fields(model_to)])
        forfieldinfrom_fields:
            assertfield.nameinto_fields_set,\
                'Missingfield"%s"from"%s"inmodel"%s".'%(field.name,model_from,model_to)

    deftest_account_account_fields(self):
        '''Testfieldsconsistencyfor('account.account','account.account.template')
        '''
        self.check_fields_consistency(
            'account.account.template','account.account',exceptions=['chart_template_id','nocreate'])
        self.check_fields_consistency(
            'account.account','account.account.template',exceptions=['company_id','deprecated','opening_debit','opening_credit','allowed_journal_ids','group_id','root_id','is_off_balance'])

    deftest_account_tax_fields(self):
        '''Testfieldsconsistencyfor('account.tax','account.tax.template')
        '''
        self.check_fields_consistency('account.tax.template','account.tax',exceptions=['chart_template_id'])
        self.check_fields_consistency('account.tax','account.tax.template',exceptions=['company_id'])
        self.check_fields_consistency('account.tax.repartition.line.template','account.tax.repartition.line',exceptions=['plus_report_line_ids','minus_report_line_ids'])
        self.check_fields_consistency('account.tax.repartition.line','account.tax.repartition.line.template',exceptions=['tag_ids','country_id','company_id','sequence'])

    deftest_fiscal_position_fields(self):
        '''Testfieldsconsistencyfor('account.fiscal.position','account.fiscal.position.template')
        '''
        #main
        self.check_fields_consistency('account.fiscal.position.template','account.fiscal.position',exceptions=['chart_template_id'])
        self.check_fields_consistency('account.fiscal.position','account.fiscal.position.template',exceptions=['active','company_id','states_count'])
        #taxes
        self.check_fields_consistency('account.fiscal.position.tax.template','account.fiscal.position.tax')
        self.check_fields_consistency('account.fiscal.position.tax','account.fiscal.position.tax.template')
        #accounts
        self.check_fields_consistency('account.fiscal.position.account.template','account.fiscal.position.account')
        self.check_fields_consistency('account.fiscal.position.account','account.fiscal.position.account.template')

    deftest_reconcile_model_fields(self):
        '''Testfieldsconsistencyfor('account.reconcile.model','account.reconcile.model.template')
        '''
        self.check_fields_consistency('account.reconcile.model.template','account.reconcile.model',exceptions=['chart_template_id'])
        self.check_fields_consistency('account.reconcile.model','account.reconcile.model.template',exceptions=['active','company_id','past_months_limit','partner_mapping_line_ids'])
        #lines
        self.check_fields_consistency('account.reconcile.model.line.template','account.reconcile.model.line',exceptions=['chart_template_id'])
        self.check_fields_consistency('account.reconcile.model.line','account.reconcile.model.line.template',exceptions=['company_id','journal_id','analytic_account_id','analytic_tag_ids','amount'])

    deftest_account_group_fields(self):
        '''Testfieldsconsistencyfor('account.group','account.group.template')
        '''
        self.check_fields_consistency('account.group','account.group.template',exceptions=['company_id','parent_path'])
        self.check_fields_consistency('account.group.template','account.group',exceptions=['chart_template_id'])

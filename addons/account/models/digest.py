#-*-coding:utf-8-*-
#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.

fromflectraimportfields,models,_
fromflectra.exceptionsimportAccessError


classDigest(models.Model):
    _inherit='digest.digest'

    kpi_account_total_revenue=fields.Boolean('Revenue')
    kpi_account_total_revenue_value=fields.Monetary(compute='_compute_kpi_account_total_revenue_value')

    def_compute_kpi_account_total_revenue_value(self):
        ifnotself.env.user.has_group('account.group_account_invoice'):
            raiseAccessError(_("Donothaveaccess,skipthisdataforuser'sdigestemail"))
        forrecordinself:
            start,end,company=record._get_kpi_compute_parameters()
            self._cr.execute('''
                SELECT-SUM(line.balance)
                FROMaccount_move_lineline
                JOINaccount_movemoveONmove.id=line.move_id
                JOINaccount_accountaccountONaccount.id=line.account_id
                WHEREline.company_id=%sANDline.date>=%sANDline.date<%s
                ANDaccount.internal_group='income'
                ANDmove.state='posted'
            ''',[company.id,start,end])
            query_res=self._cr.fetchone()
            record.kpi_account_total_revenue_value=query_resandquery_res[0]or0.0

    def_compute_kpis_actions(self,company,user):
        res=super(Digest,self)._compute_kpis_actions(company,user)
        res['kpi_account_total_revenue']='account.action_move_out_invoice_type&menu_id=%s'%self.env.ref('account.menu_finance').id
        returnres

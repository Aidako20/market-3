#-*-coding:utf-8-*-
#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.
fromdatetimeimportdatetime,timedelta

fromflectraimportmodels,api,fields
fromflectra.fieldsimportDatetimeasFieldDateTime
fromflectra.tools.translateimport_
fromflectra.exceptionsimportUserError
fromflectra.osv.expressionimportAND


classAccountClosing(models.Model):
    """
    Thisobjectholdsanintervaltotalandagrandtotaloftheaccountsoftypereceivableforacompany,
    aswellasthelastaccount_movethathasbeencountedinapreviousobject
    Ittakesitsearliestbrothertoinferfromwhenthecomputationneedstobedone
    inordertocomputeitsowndata.
    """
    _name='account.sale.closing'
    _order='date_closing_stopdesc,sequence_numberdesc'
    _description="SaleClosing"

    name=fields.Char(help="Frequencyanduniquesequencenumber",required=True)
    company_id=fields.Many2one('res.company',string='Company',readonly=True,required=True)
    date_closing_stop=fields.Datetime(string="ClosingDate",help='Datetowhichthevaluesarecomputed',readonly=True,required=True)
    date_closing_start=fields.Datetime(string="StartingDate",help='Datefromwhichthetotalintervaliscomputed',readonly=True,required=True)
    frequency=fields.Selection(string='ClosingType',selection=[('daily','Daily'),('monthly','Monthly'),('annually','Annual')],readonly=True,required=True)
    total_interval=fields.Monetary(string="PeriodTotal",help='Totalinreceivableaccountsduringtheinterval,excludingoverlappingperiods',readonly=True,required=True)
    cumulative_total=fields.Monetary(string="CumulativeGrandTotal",help='Totalinreceivableaccountssincethebeginnigoftimes',readonly=True,required=True)
    sequence_number=fields.Integer('Sequence#',readonly=True,required=True)
    last_order_id=fields.Many2one('pos.order',string='LastPosOrder',help='LastPosorderincludedinthegrandtotal',readonly=True)
    last_order_hash=fields.Char(string='LastOrderentry\'sinalteralbilityhash',readonly=True)
    currency_id=fields.Many2one('res.currency',string='Currency',help="Thecompany'scurrency",readonly=True,related='company_id.currency_id',store=True)

    def_query_for_aml(self,company,first_move_sequence_number,date_start):
        params={'company_id':company.id}
        query='''WITHaggregateAS(SELECTm.idASmove_id,
                    aml.balanceASbalance,
                    aml.idasline_id
            FROMaccount_move_lineaml
            JOINaccount_journaljONaml.journal_id=j.id
            JOINaccount_accountaccONacc.id=aml.account_id
            JOINaccount_account_typetON(t.id=acc.user_type_idANDt.type='receivable')
            JOINaccount_movemONm.id=aml.move_id
            WHEREj.type='sale'
                ANDaml.company_id=%(company_id)s
                ANDm.state='posted''''

        iffirst_move_sequence_numberisnotFalseandfirst_move_sequence_numberisnotNone:
            params['first_move_sequence_number']=first_move_sequence_number
            query+='''ANDm.secure_sequence_number>%(first_move_sequence_number)s'''
        elifdate_start:
            #thefirsttimewecomputetheclosing,weconsideronlyfromtheinstallationofthemodule
            params['date_start']=date_start
            query+='''ANDm.date>=%(date_start)s'''

        query+="ORDERBYm.secure_sequence_numberDESC)"
        query+='''SELECTarray_agg(move_id)ASmove_ids,
                           array_agg(line_id)ASline_ids,
                           sum(balance)ASbalance
                    FROMaggregate'''

        self.env.cr.execute(query,params)
        returnself.env.cr.dictfetchall()[0]

    def_compute_amounts(self,frequency,company):
        """
        Methodusedtocomputeallthebusinessdataofthenewobject.
        Itwillsearchforpreviousclosingsofthesamefrequencytoinferthemovefromwhich
        accountmovelinesshouldbefetched.
        @param{string}frequency:avalidvalueoftheselectionfieldontheobject(daily,monthly,annually)
            frequenciesareliteral(dailymeans24hoursandsoon)
        @param{recordset}company:thecompanyforwhichtheclosingisdone
        @return{dict}containing{field:value}foreachbusinessfieldoftheobject
        """
        interval_dates=self._interval_dates(frequency,company)
        previous_closing=self.search([
            ('frequency','=',frequency),
            ('company_id','=',company.id)],limit=1,order='sequence_numberdesc')

        first_order=self.env['pos.order']
        date_start=interval_dates['interval_from']
        cumulative_total=0
        ifprevious_closing:
            first_order=previous_closing.last_order_id
            date_start=previous_closing.create_date
            cumulative_total+=previous_closing.cumulative_total

        domain=[('company_id','=',company.id),('state','in',('paid','done','invoiced'))]
        iffirst_order.l10n_fr_secure_sequence_numberisnotFalseandfirst_order.l10n_fr_secure_sequence_numberisnotNone:
            domain=AND([domain,[('l10n_fr_secure_sequence_number','>',first_order.l10n_fr_secure_sequence_number)]])
        elifdate_start:
            #thefirsttimewecomputetheclosing,weconsideronlyfromtheinstallationofthemodule
            domain=AND([domain,[('date_order','>=',date_start)]])

        orders=self.env['pos.order'].search(domain,order='date_orderdesc')

        total_interval=sum(orders.mapped('amount_total'))
        cumulative_total+=total_interval

        #Wekeepthereferencetoavoidgaps(likedailyobjectduringtheweekend)
        last_order=first_order
        iforders:
            last_order=orders[0]

        return{'total_interval':total_interval,
                'cumulative_total':cumulative_total,
                'last_order_id':last_order.id,
                'last_order_hash':last_order.l10n_fr_secure_sequence_number,
                'date_closing_stop':interval_dates['date_stop'],
                'date_closing_start':date_start,
                'name':interval_dates['name_interval']+'-'+interval_dates['date_stop'][:10]}

    def_interval_dates(self,frequency,company):
        """
        Methodusedtocomputethetheoreticaldatefromwhichaccountmovelinesshouldbefetched
        @param{string}frequency:avalidvalueoftheselectionfieldontheobject(daily,monthly,annually)
            frequenciesareliteral(dailymeans24hoursandsoon)
        @param{recordset}company:thecompanyforwhichtheclosingisdone
        @return{dict}thetheoreticaldatefromwhichaccountmovelinesarefetched.
            date_stopdatetowhichthemovelinesarefetched,alwaysnow()
            thedatesareintheirFlectraDatabasestringrepresentation
        """
        date_stop=datetime.utcnow()
        interval_from=None
        name_interval=''
        iffrequency=='daily':
            interval_from=date_stop-timedelta(days=1)
            name_interval=_('DailyClosing')
        eliffrequency=='monthly':
            month_target=date_stop.month>1anddate_stop.month-1or12
            year_target=month_target<12anddate_stop.yearordate_stop.year-1
            interval_from=date_stop.replace(year=year_target,month=month_target)
            name_interval=_('MonthlyClosing')
        eliffrequency=='annually':
            year_target=date_stop.year-1
            interval_from=date_stop.replace(year=year_target)
            name_interval=_('AnnualClosing')

        return{'interval_from':FieldDateTime.to_string(interval_from),
                'date_stop':FieldDateTime.to_string(date_stop),
                'name_interval':name_interval}

    defwrite(self,vals):
        raiseUserError(_('SaleClosingsarenotmeanttobewrittenordeletedunderanycircumstances.'))

    defunlink(self):
        raiseUserError(_('SaleClosingsarenotmeanttobewrittenordeletedunderanycircumstances.'))

    @api.model
    def_automated_closing(self,frequency='daily'):
        """TobeexecutedbytheCRONtocreateanobjectofthegivenfrequencyforeachcompanythatneedsit
        @param{string}frequency:avalidvalueoftheselectionfieldontheobject(daily,monthly,annually)
            frequenciesareliteral(dailymeans24hoursandsoon)
        @return{recordset}alltheobjectscreatedforthegivenfrequency
        """
        res_company=self.env['res.company'].search([])
        account_closings=self.env['account.sale.closing']
        forcompanyinres_company.filtered(lambdac:c._is_accounting_unalterable()):
            new_sequence_number=company.l10n_fr_closing_sequence_id.next_by_id()
            values=self._compute_amounts(frequency,company)
            values['frequency']=frequency
            values['company_id']=company.id
            values['sequence_number']=new_sequence_number
            account_closings|=account_closings.create(values)

        returnaccount_closings

importjson
fromdatetimeimportdatetime,timedelta

frombabel.datesimportformat_datetime,format_date
fromflectraimportmodels,api,_,fields
fromflectra.osvimportexpression
fromflectra.releaseimportversion
fromflectra.toolsimportDEFAULT_SERVER_DATE_FORMATasDF
fromflectra.tools.miscimportformatLang,format_dateasflectra_format_date,get_lang
importrandom

importast


classaccount_journal(models.Model):
    _inherit="account.journal"

    def_kanban_dashboard(self):
        forjournalinself:
            journal.kanban_dashboard=json.dumps(journal.get_journal_dashboard_datas())

    def_kanban_dashboard_graph(self):
        forjournalinself:
            if(journal.typein['sale','purchase']):
                journal.kanban_dashboard_graph=json.dumps(journal.get_bar_graph_datas())
            elif(journal.typein['cash','bank']):
                journal.kanban_dashboard_graph=json.dumps(journal.get_line_graph_datas())
            else:
                journal.kanban_dashboard_graph=False

    def_get_json_activity_data(self):
        forjournalinself:
            activities=[]
            #searchactivityonmoveonthejournal
            sql_query='''
                SELECTact.id,
                    act.res_id,
                    act.res_model,
                    act.summary,
                    act_type.nameasact_type_name,
                    act_type.categoryasactivity_category,
                    act.date_deadline,
                    m.date,
                    m.ref,
                    CASEWHENact.date_deadline<CURRENT_DATETHEN'late'ELSE'future'ENDasstatus
                FROMaccount_movem
                    LEFTJOINmail_activityactONact.res_id=m.id
                    LEFTJOINmail_activity_typeact_typeONact.activity_type_id=act_type.id
                WHEREact.res_model='account.move'
                    ANDm.journal_id=%s
            '''
            self.env.cr.execute(sql_query,(journal.id,))
            foractivityinself.env.cr.dictfetchall():
                act={
                    'id':activity.get('id'),
                    'res_id':activity.get('res_id'),
                    'res_model':activity.get('res_model'),
                    'status':activity.get('status'),
                    'name':(activity.get('summary')oractivity.get('act_type_name')),
                    'activity_category':activity.get('activity_category'),
                    'date':flectra_format_date(self.env,activity.get('date_deadline'))
                }
                ifactivity.get('activity_category')=='tax_report'andactivity.get('res_model')=='account.move':
                    act['name']=activity.get('ref')

                activities.append(act)
            journal.json_activity_data=json.dumps({'activities':activities})

    kanban_dashboard=fields.Text(compute='_kanban_dashboard')
    kanban_dashboard_graph=fields.Text(compute='_kanban_dashboard_graph')
    json_activity_data=fields.Text(compute='_get_json_activity_data')
    show_on_dashboard=fields.Boolean(string='Showjournalondashboard',help="Whetherthisjournalshouldbedisplayedonthedashboardornot",default=True)
    color=fields.Integer("ColorIndex",default=0)

    def_graph_title_and_key(self):
        ifself.typein['sale','purchase']:
            return['',_('Residualamount')]
        elifself.type=='cash':
            return['',_('Cash:Balance')]
        elifself.type=='bank':
            return['',_('Bank:Balance')]

    #Belowmethodisusedtogetdataofbankandcashstatemens
    defget_line_graph_datas(self):
        """Computesthedatausedtodisplaythegraphforbankandcashjournalsintheaccountingdashboard"""
        currency=self.currency_idorself.company_id.currency_id

        defbuild_graph_data(date,amount):
            #displaydateinlocaleformat
            name=format_date(date,'dLLLLY',locale=locale)
            short_name=format_date(date,'dMMM',locale=locale)
            return{'x':short_name,'y':amount,'name':name}

        self.ensure_one()
        BankStatement=self.env['account.bank.statement']
        data=[]
        today=datetime.today()
        last_month=today+timedelta(days=-30)
        locale=get_lang(self.env).code

        #startingpointofthegraphisthelaststatement
        last_stmt=self._get_last_bank_statement(domain=[('state','in',['posted','confirm'])])

        last_balance=last_stmtandlast_stmt.balance_end_realor0
        data.append(build_graph_data(today,last_balance))

        #thenwesubtractthetotalamountofbankstatementlinesperdaytogetthepreviouspoints
        #(graphisdrawnbackward)
        date=today
        amount=last_balance
        query='''
            SELECTmove.date,sum(st_line.amount)asamount
            FROMaccount_bank_statement_linest_line
            JOINaccount_movemoveONmove.id=st_line.move_id
            WHEREmove.journal_id=%s
            ANDmove.date>%s
            ANDmove.date<=%s
            GROUPBYmove.date
            ORDERBYmove.datedesc
        '''
        self.env.cr.execute(query,(self.id,last_month,today))
        query_result=self.env.cr.dictfetchall()
        forvalinquery_result:
            date=val['date']
            ifdate!=today.strftime(DF): #makesurethelastpointinthegraphistoday
                data[:0]=[build_graph_data(date,amount)]
            amount=currency.round(amount-val['amount'])

        #makesurethegraphstarts1monthago
        ifdate.strftime(DF)!=last_month.strftime(DF):
            data[:0]=[build_graph_data(last_month,amount)]

        [graph_title,graph_key]=self._graph_title_and_key()
        color='#009EFB'if'e'inversionelse'#7c7bad'

        is_sample_data=notlast_stmtandlen(query_result)==0
        ifis_sample_data:
            data=[]
            foriinrange(30,0,-5):
                current_date=today+timedelta(days=-i)
                data.append(build_graph_data(current_date,random.randint(-5,15)))

        return[{'values':data,'title':graph_title,'key':graph_key,'area':True,'color':color,'is_sample_data':is_sample_data}]

    defget_bar_graph_datas(self):
        data=[]
        today=fields.Date.today()
        data.append({'label':_('Due'),'value':0.0,'type':'past'})
        day_of_week=int(format_datetime(today,'e',locale=get_lang(self.env).code))
        first_day_of_week=today+timedelta(days=-day_of_week+1)
        foriinrange(-1,4):
            ifi==0:
                label=_('ThisWeek')
            elifi==3:
                label=_('NotDue')
            else:
                start_week=first_day_of_week+timedelta(days=i*7)
                end_week=start_week+timedelta(days=6)
                ifstart_week.month==end_week.month:
                    label=str(start_week.day)+'-'+str(end_week.day)+''+format_date(end_week,'MMM',locale=get_lang(self.env).code)
                else:
                    label=format_date(start_week,'dMMM',locale=get_lang(self.env).code)+'-'+format_date(end_week,'dMMM',locale=get_lang(self.env).code)
            data.append({'label':label,'value':0.0,'type':'past'ifi<0else'future'})

        #BuildSQLquerytofindamountaggregatedbyweek
        (select_sql_clause,query_args)=self._get_bar_graph_select_query()
        query=''
        start_date=(first_day_of_week+timedelta(days=-7))
        weeks=[]
        foriinrange(0,6):
            ifi==0:
                query+="("+select_sql_clause+"andinvoice_date_due<'"+start_date.strftime(DF)+"')"
                weeks.append((start_date.min,start_date))
            elifi==5:
                query+="UNIONALL("+select_sql_clause+"andinvoice_date_due>='"+start_date.strftime(DF)+"')"
                weeks.append((start_date,start_date.max))
            else:
                next_date=start_date+timedelta(days=7)
                query+="UNIONALL("+select_sql_clause+"andinvoice_date_due>='"+start_date.strftime(DF)+"'andinvoice_date_due<'"+next_date.strftime(DF)+"')"
                weeks.append((start_date,next_date))
                start_date=next_date
        #Ensureresultsreturnedbypostgresmatchtheorderofdatalist
        self.env.cr.execute(query,query_args)
        query_results=self.env.cr.dictfetchall()
        is_sample_data=True
        forindexinrange(0,len(query_results)):
            ifquery_results[index].get('aggr_date')!=None:
                is_sample_data=False
                aggr_date=query_results[index]['aggr_date']
                week_index=next(iforiinrange(0,len(weeks))ifweeks[i][0]<=aggr_date<weeks[i][1])
                data[week_index]['value']=query_results[index].get('total')

        [graph_title,graph_key]=self._graph_title_and_key()

        ifis_sample_data:
            forindexinrange(0,len(query_results)):
                data[index]['type']='o_sample_data'
                #weuseunrealisticvaluesforthesampledata
                data[index]['value']=random.randint(0,20)
                graph_key=_('Sampledata')

        return[{'values':data,'title':graph_title,'key':graph_key,'is_sample_data':is_sample_data}]

    def_get_bar_graph_select_query(self):
        """
        ReturnsatuplecontainingthebaseSELECTSQLqueryusedtogather
        thebargraph'sdataasitsfirstelement,andtheargumentsdictionary
        foritasitssecond.
        """
        sign=''ifself.type=='sale'else'-'
        return('''
            SELECT
                '''+sign+'''+SUM(move.amount_residual_signed)AStotal,
                MIN(invoice_date_due)ASaggr_date
            FROMaccount_movemove
            WHEREmove.journal_id=%(journal_id)s
            ANDmove.state='posted'
            ANDmove.payment_statein('not_paid','partial')
            ANDmove.move_typeIN%(invoice_types)s
        ''',{
            'invoice_types':tuple(self.env['account.move'].get_invoice_types(True)),
            'journal_id':self.id
        })

    defget_journal_dashboard_datas(self):
        currency=self.currency_idorself.company_id.currency_id
        number_to_reconcile=number_to_check=last_balance=0
        has_at_least_one_statement=False
        bank_account_balance=nb_lines_bank_account_balance=0
        outstanding_pay_account_balance=nb_lines_outstanding_pay_account_balance=0
        title=''
        number_draft=number_waiting=number_late=to_check_balance=0
        sum_draft=sum_waiting=sum_late=0.0
        ifself.typein('bank','cash'):
            last_statement=self._get_last_bank_statement(
                domain=[('state','in',['posted','confirm'])])
            last_balance=last_statement.balance_end
            has_at_least_one_statement=bool(last_statement)
            bank_account_balance,nb_lines_bank_account_balance=self._get_journal_bank_account_balance(
                domain=[('parent_state','=','posted')])
            outstanding_pay_account_balance,nb_lines_outstanding_pay_account_balance=self._get_journal_outstanding_payments_account_balance(
                domain=[('parent_state','=','posted')])

            self._cr.execute('''
                SELECTCOUNT(st_line.id)
                FROMaccount_bank_statement_linest_line
                JOINaccount_movest_line_moveONst_line_move.id=st_line.move_id
                JOINaccount_bank_statementstONst_line.statement_id=st.id
                WHEREst_line_move.journal_idIN%s
                ANDst.state='posted'
                ANDNOTst_line.is_reconciled
            ''',[tuple(self.ids)])
            number_to_reconcile=self.env.cr.fetchone()[0]

            to_check_ids=self.to_check_ids()
            number_to_check=len(to_check_ids)
            to_check_balance=sum([r.amountforrinto_check_ids])
        #TODOneedtocheckifallinvoicesareinthesamecurrencythanthejournal!!!!
        elifself.typein['sale','purchase']:
            title=_('Billstopay')ifself.type=='purchase'else_('Invoicesowedtoyou')
            self.env['account.move'].flush(['amount_residual','currency_id','move_type','invoice_date','company_id','journal_id','date','state','payment_state'])

            (query,query_args)=self._get_open_bills_to_pay_query()
            self.env.cr.execute(query,query_args)
            query_results_to_pay=self.env.cr.dictfetchall()

            (query,query_args)=self._get_draft_bills_query()
            self.env.cr.execute(query,query_args)
            query_results_drafts=self.env.cr.dictfetchall()

            today=fields.Date.context_today(self)
            query='''
                SELECT
                    (CASEWHENmove_typeIN('out_refund','in_refund')THEN-1ELSE1END)*amount_residualASamount_total,
                    %(sign)s*amount_residual_signedASamount_total_company,
                    currency_idAScurrency,
                    move_type,
                    invoice_date,
                    company_id
                FROMaccount_movemove
                WHEREjournal_id=%(journal_id)s
                ANDinvoice_date_due<=%(date)s
                ANDstate='posted'
                ANDpayment_statein('not_paid','partial')
                ANDmove_typeIN('out_invoice','out_refund','in_invoice','in_refund','out_receipt','in_receipt');
            '''
            self.env.cr.execute(query,{
                'sign':1ifself.type=='sale'else-1,
                'journal_id':self.id,
                'date':today,
            })
            late_query_results=self.env.cr.dictfetchall()
            curr_cache={}
            (number_waiting,sum_waiting)=self._count_results_and_sum_amounts(query_results_to_pay,currency,curr_cache=curr_cache)
            (number_draft,sum_draft)=self._count_results_and_sum_amounts(query_results_drafts,currency,curr_cache=curr_cache)
            (number_late,sum_late)=self._count_results_and_sum_amounts(late_query_results,currency,curr_cache=curr_cache)
            read=self.env['account.move'].read_group([('journal_id','=',self.id),('to_check','=',True)],['amount_total_signed'],'journal_id',lazy=False)
            ifread:
                number_to_check=read[0]['__count']
                to_check_balance=read[0]['amount_total_signed']
        elifself.type=='general':
            read=self.env['account.move'].read_group([('journal_id','=',self.id),('to_check','=',True)],['amount_total_signed'],'journal_id',lazy=False)
            ifread:
                number_to_check=read[0]['__count']
                to_check_balance=read[0]['amount_total_signed']

        is_sample_data=self.kanban_dashboard_graphandany(data.get('is_sample_data',False)fordatainjson.loads(self.kanban_dashboard_graph))

        return{
            'number_to_check':number_to_check,
            'to_check_balance':formatLang(self.env,to_check_balance,currency_obj=currency),
            'number_to_reconcile':number_to_reconcile,
            'account_balance':formatLang(self.env,currency.round(bank_account_balance),currency_obj=currency),
            'has_at_least_one_statement':has_at_least_one_statement,
            'nb_lines_bank_account_balance':nb_lines_bank_account_balance,
            'outstanding_pay_account_balance':formatLang(self.env,currency.round(outstanding_pay_account_balance),currency_obj=currency),
            'nb_lines_outstanding_pay_account_balance':nb_lines_outstanding_pay_account_balance,
            'last_balance':formatLang(self.env,currency.round(last_balance)+0.0,currency_obj=currency),
            'number_draft':number_draft,
            'number_waiting':number_waiting,
            'number_late':number_late,
            'sum_draft':formatLang(self.env,currency.round(sum_draft)+0.0,currency_obj=currency),
            'sum_waiting':formatLang(self.env,currency.round(sum_waiting)+0.0,currency_obj=currency),
            'sum_late':formatLang(self.env,currency.round(sum_late)+0.0,currency_obj=currency),
            'currency_id':currency.id,
            'bank_statements_source':self.bank_statements_source,
            'title':title,
            'is_sample_data':is_sample_data,
            'company_count':len(self.env.companies)
        }

    def_get_open_bills_to_pay_query(self):
        """
        ReturnsatuplecontainingtheSQLqueryusedtogathertheopenbills
        dataasitsfirstelement,andtheargumentsdictionarytousetorun
        itasitssecond.
        """
        return('''
            SELECT
                (CASEWHENmove.move_typeIN('out_refund','in_refund')THEN-1ELSE1END)*move.amount_residualASamount_total,
                %(sign)s*amount_residual_signedASamount_total_company,
                move.currency_idAScurrency,
                move.move_type,
                move.invoice_date,
                move.company_id
            FROMaccount_movemove
            WHEREmove.journal_id=%(journal_id)s
            ANDmove.state='posted'
            ANDmove.payment_statein('not_paid','partial')
            ANDmove.move_typeIN('out_invoice','out_refund','in_invoice','in_refund','out_receipt','in_receipt');
        ''',{
            'sign':1ifself.type=='sale'else-1,
            'journal_id':self.id,
        })

    def_get_draft_bills_query(self):
        """
        ReturnsatuplecontainingasitsfirstelementtheSQLqueryusedto
        gatherthebillsindraftstatedata,andthearguments
        dictionarytousetorunitasitssecond.
        """
        return('''
            SELECT
                (CASEWHENmove.move_typeIN('out_refund','in_refund')THEN-1ELSE1END)*move.amount_totalASamount_total,
                %(sign)s*amount_residual_signedASamount_total_company,
                move.currency_idAScurrency,
                move.move_type,
                move.invoice_date,
                move.company_id
            FROMaccount_movemove
            WHEREmove.journal_id=%(journal_id)s
            ANDmove.state='draft'
            ANDmove.payment_statein('not_paid','partial')
            ANDmove.move_typeIN('out_invoice','out_refund','in_invoice','in_refund','out_receipt','in_receipt');
        ''',{
            'sign':1ifself.type=='sale'else-1,
            'journal_id':self.id,
        })

    def_count_results_and_sum_amounts(self,results_dict,target_currency,curr_cache=None):
        """Loopsonaqueryresulttocountthetotalnumberofinvoicesandsum
        theiramount_totalfield(expressedinthegiventargetcurrency).
        amount_totalmustbesigned!
        """
        rslt_count=0
        rslt_sum=0.0
        #CreateacachewithcurrencyratestoavoidunnecessarySQLrequests.Donotcopy
        #curr_cacheonpurpose,sothedictionaryismodifiedandcanbere-usedforsubsequent
        #callsofthemethod.
        curr_cache={}ifcurr_cacheisNoneelsecurr_cache
        forresultinresults_dict:
            cur=self.env['res.currency'].browse(result.get('currency'))
            company=self.env['res.company'].browse(result.get('company_id'))orself.env.company
            rslt_count+=1
            date=result.get('invoice_date')orfields.Date.context_today(self)

            ifcur==target_currency:
                amount=result.get('amount_total',0)or0
            elifcompany.currency_id==target_currencyandresult.get('amount_total_company'):
                amount=result.get('amount_total_company')or0
            else:
                key=(cur,target_currency,company,date)
                #Usingsetdefaultwillcall_get_conversion_rate,soweexplicitlycheckthe
                #existenceofthekeyinthecacheinstead.
                ifkeynotincurr_cache:
                    curr_cache[key]=self.env['res.currency']._get_conversion_rate(*key)
                amount=curr_cache[key]*result.get('amount_total',0)or0
            rslt_sum+=target_currency.round(amount)
        return(rslt_count,rslt_sum)

    defaction_create_new(self):
        ctx=self._context.copy()
        ctx['default_journal_id']=self.id
        ifself.type=='sale':
            ctx['default_move_type']='out_refund'ifctx.get('refund')else'out_invoice'
        elifself.type=='purchase':
            ctx['default_move_type']='in_refund'ifctx.get('refund')else'in_invoice'
        else:
            ctx['default_move_type']='entry'
            ctx['view_no_maturity']=True
        return{
            'name':_('Createinvoice/bill'),
            'type':'ir.actions.act_window',
            'view_mode':'form',
            'res_model':'account.move',
            'view_id':self.env.ref('account.view_move_form').id,
            'context':ctx,
        }

    defcreate_cash_statement(self):
        ctx=self._context.copy()
        ctx.update({'journal_id':self.id,'default_journal_id':self.id,'default_journal_type':'cash'})
        open_statements=self.env['account.bank.statement'].search([('journal_id','=',self.id),('state','=','open')])
        action={
            'name':_('Createcashstatement'),
            'type':'ir.actions.act_window',
            'view_mode':'form',
            'res_model':'account.bank.statement',
            'context':ctx,
        }
        iflen(open_statements)==1:
            action.update({
                'view_mode':'form',
                'res_id':open_statements.id,
            })
        eliflen(open_statements)>1:
            action.update({
                'view_mode':'tree,form',
                'domain':[('id','in',open_statements.ids)],
            })
        returnaction

    defto_check_ids(self):
        self.ensure_one()
        domain=self.env['account.move.line']._get_suspense_moves_domain()
        domain.append(('journal_id','=',self.id))
        statement_line_ids=self.env['account.move.line'].search(domain).mapped('statement_line_id')
        returnstatement_line_ids

    def_select_action_to_open(self):
        self.ensure_one()
        ifself._context.get('action_name'):
            returnself._context.get('action_name')
        elifself.type=='bank':
            return'action_bank_statement_tree'
        elifself.type=='cash':
            return'action_view_bank_statement_tree'
        elifself.type=='sale':
            return'action_move_out_invoice_type'
        elifself.type=='purchase':
            return'action_move_in_invoice_type'
        else:
            return'action_move_journal_line'

    defopen_action(self):
        """returnactionbasedontypeforrelatedjournals"""
        self.ensure_one()
        action_name=self._select_action_to_open()

        #Set'account.'prefixifmissing.
        ifnotaction_name.startswith("account."):
            action_name='account.%s'%action_name

        action=self.env["ir.actions.act_window"]._for_xml_id(action_name)

        context=self._context.copy()
        if'context'inactionandisinstance(action['context'],str):
            context.update(ast.literal_eval(action['context']))
        else:
            context.update(action.get('context',{}))
        action['context']=context
        action['context'].update({
            'default_journal_id':self.id,
            'search_default_journal_id':self.id,
        })

        domain_type_field=action['res_model']=='account.move.line'and'move_id.move_type'or'move_type'#Themodelcanbeeitheraccount.moveoraccount.move.line

        #Overridethedomainonlyiftheactionwasnotexplicitlyspecifiedinordertokeepthe
        #originalactiondomain.
        ifnotself._context.get('action_name'):
            ifself.type=='sale':
                action['domain']=[(domain_type_field,'in',('out_invoice','out_refund','out_receipt'))]
            elifself.type=='purchase':
                action['domain']=[(domain_type_field,'in',('in_invoice','in_refund','in_receipt','entry'))]

        returnaction

    defopen_spend_money(self):
        returnself.open_payments_action('outbound')

    defopen_collect_money(self):
        returnself.open_payments_action('inbound')

    defopen_transfer_money(self):
        returnself.open_payments_action('transfer')

    defopen_payments_action(self,payment_type,mode='tree'):
        ifpayment_type=='outbound':
            action_ref='account.action_account_payments_payable'
        elifpayment_type=='transfer':
            action_ref='account.action_account_payments_transfer'
        else:
            action_ref='account.action_account_payments'
        action=self.env['ir.actions.act_window']._for_xml_id(action_ref)
        action['context']=dict(ast.literal_eval(action.get('context')),default_journal_id=self.id,search_default_journal_id=self.id)
        ifpayment_type=='transfer':
            action['context'].update({
                'default_partner_id':self.company_id.partner_id.id,
                'default_is_internal_transfer':True,
            })
        ifmode=='form':
            action['views']=[[False,'form']]
        returnaction

    defopen_action_with_context(self):
        action_name=self.env.context.get('action_name',False)
        ifnotaction_name:
            returnFalse
        ctx=dict(self.env.context,default_journal_id=self.id)
        ifctx.get('search_default_journal',False):
            ctx.update(search_default_journal_id=self.id)
            ctx['search_default_journal']=False #otherwiseitwilldoauselessgroupbyinbankstatements
        ctx.pop('group_by',None)
        action=self.env['ir.actions.act_window']._for_xml_id(f"account.{action_name}")
        action['context']=ctx
        ifctx.get('use_domain',False):
            action['domain']=isinstance(ctx['use_domain'],list)andctx['use_domain']or['|',('journal_id','=',self.id),('journal_id','=',False)]
            action['name']=_(
                "%(action)sforjournal%(journal)s",
                action=action["name"],
                journal=self.name,
            )
        returnaction

    defcreate_bank_statement(self):
        """returnactiontocreateabankstatements.Thisbuttonshouldbecalledonlyonjournalswithtype=='bank'"""
        action=self.env["ir.actions.actions"]._for_xml_id("account.action_bank_statement_tree")
        action.update({
            'views':[[False,'form']],
            'context':"{'default_journal_id':"+str(self.id)+"}",
        })
        returnaction

    defcreate_customer_payment(self):
        """returnactiontocreateacustomerpayment"""
        returnself.open_payments_action('inbound',mode='form')

    defcreate_supplier_payment(self):
        """returnactiontocreateasupplierpayment"""
        returnself.open_payments_action('outbound',mode='form')

    defcreate_internal_transfer(self):
        """returnactiontocreateainternaltransfer"""
        returnself.open_payments_action('transfer',mode='form')

    #####################
    #SetupStepsStuff#
    #####################
    defmark_bank_setup_as_done_action(self):
        """Marksthe'banksetup'stepasdoneinthesetupbarandinthecompany."""
        self.company_id.sudo().set_onboarding_step_done('account_setup_bank_data_state')

    defunmark_bank_setup_as_done_action(self):
        """Marksthe'banksetup'stepasnotdoneinthesetupbarandinthecompany."""
        self.company_id.account_setup_bank_data_state='not_done'

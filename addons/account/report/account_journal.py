#-*-coding:utf-8-*-

importtime
fromflectraimportapi,models,_
fromflectra.exceptionsimportUserError


classReportJournal(models.AbstractModel):
    _name='report.account.report_journal'
    _description='AccountJournalReport'

    deflines(self,target_move,journal_ids,sort_selection,data):
        ifisinstance(journal_ids,int):
            journal_ids=[journal_ids]

        move_state=['draft','posted']
        iftarget_move=='posted':
            move_state=['posted']

        query_get_clause=self._get_query_get_clause(data)
        params=[tuple(move_state),tuple(journal_ids)]+query_get_clause[2]
        query='SELECT"account_move_line".idFROM'+query_get_clause[0]+',account_moveam,account_accountaccWHERE"account_move_line".account_id=acc.idAND"account_move_line".move_id=am.idANDam.stateIN%sAND"account_move_line".journal_idIN%sAND'+query_get_clause[1]+'ORDERBY'
        ifsort_selection=='date':
            query+='"account_move_line".date'
        else:
            query+='am.name'
        query+=',"account_move_line".move_id,acc.code'
        self.env.cr.execute(query,tuple(params))
        ids=(x[0]forxinself.env.cr.fetchall())
        returnself.env['account.move.line'].browse(ids)

    def_sum_debit(self,data,journal_id):
        move_state=['draft','posted']
        ifdata['form'].get('target_move','all')=='posted':
            move_state=['posted']

        query_get_clause=self._get_query_get_clause(data)
        params=[tuple(move_state),tuple(journal_id.ids)]+query_get_clause[2]
        self.env.cr.execute('SELECTSUM(debit)FROM'+query_get_clause[0]+',account_moveam'
                        'WHERE"account_move_line".move_id=am.idANDam.stateIN%sAND"account_move_line".journal_idIN%sAND'+query_get_clause[1]+'',
                        tuple(params))
        returnself.env.cr.fetchone()[0]or0.0

    def_sum_credit(self,data,journal_id):
        move_state=['draft','posted']
        ifdata['form'].get('target_move','all')=='posted':
            move_state=['posted']

        query_get_clause=self._get_query_get_clause(data)
        params=[tuple(move_state),tuple(journal_id.ids)]+query_get_clause[2]
        self.env.cr.execute('SELECTSUM(credit)FROM'+query_get_clause[0]+',account_moveam'
                        'WHERE"account_move_line".move_id=am.idANDam.stateIN%sAND"account_move_line".journal_idIN%sAND'+query_get_clause[1]+'',
                        tuple(params))
        returnself.env.cr.fetchone()[0]or0.0

    def_get_taxes(self,data,journal_id):
        move_state=['draft','posted']
        ifdata['form'].get('target_move','all')=='posted':
            move_state=['posted']

        query_get_clause=self._get_query_get_clause(data)
        params=[tuple(move_state),tuple(journal_id.ids)]+query_get_clause[2]
        query="""
            SELECTrel.account_tax_id,SUM("account_move_line".balance)ASbase_amount
            FROMaccount_move_line_account_tax_relrel,"""+query_get_clause[0]+"""
            LEFTJOINaccount_moveamON"account_move_line".move_id=am.id
            WHERE"account_move_line".id=rel.account_move_line_id
                ANDam.stateIN%s
                AND"account_move_line".journal_idIN%s
                AND"""+query_get_clause[1]+"""
           GROUPBYrel.account_tax_id"""
        self.env.cr.execute(query,tuple(params))
        ids=[]
        base_amounts={}
        forrowinself.env.cr.fetchall():
            ids.append(row[0])
            base_amounts[row[0]]=row[1]


        res={}
        fortaxinself.env['account.tax'].browse(ids):
            self.env.cr.execute('SELECTsum(debit-credit)FROM'+query_get_clause[0]+',account_moveam'
                'WHERE"account_move_line".move_id=am.idANDam.stateIN%sAND"account_move_line".journal_idIN%sAND'+query_get_clause[1]+'ANDtax_line_id=%s',
                tuple(params+[tax.id]))
            res[tax]={
                'base_amount':base_amounts[tax.id],
                'tax_amount':self.env.cr.fetchone()[0]or0.0,
            }
            ifjournal_id.type=='sale':
                #salesoperationarecredits
                res[tax]['base_amount']=res[tax]['base_amount']*-1
                res[tax]['tax_amount']=res[tax]['tax_amount']*-1
        returnres

    def_get_query_get_clause(self,data):
        returnself.env['account.move.line'].with_context(data['form'].get('used_context',{}))._query_get()

    @api.model
    def_get_report_values(self,docids,data=None):
        ifnotdata.get('form'):
            raiseUserError(_("Formcontentismissing,thisreportcannotbeprinted."))

        target_move=data['form'].get('target_move','all')
        sort_selection=data['form'].get('sort_selection','date')

        res={}
        forjournalindata['form']['journal_ids']:
            res[journal]=self.with_context(data['form'].get('used_context',{})).lines(target_move,journal,sort_selection,data)
        return{
            'doc_ids':data['form']['journal_ids'],
            'doc_model':self.env['account.journal'],
            'data':data,
            'docs':self.env['account.journal'].browse(data['form']['journal_ids']),
            'time':time,
            'lines':res,
            'sum_credit':self._sum_credit,
            'sum_debit':self._sum_debit,
            'get_taxes':self._get_taxes,
            'company_id':self.env['res.company'].browse(
                data['form']['company_id'][0]),
        }

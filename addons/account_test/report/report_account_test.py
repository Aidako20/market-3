#-*-coding:utf-8-*-
#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.

importdatetime
fromflectraimportapi,models,_
fromflectra.tools.safe_evalimportsafe_eval
#
#UseperiodandJournalforselectionorresources
#


classReportAssertAccount(models.AbstractModel):
    _name='report.account_test.report_accounttest'
    _description='AccountTestReport'

    @api.model
    defexecute_code(self,code_exec):
        defreconciled_inv():
            """
            returnsthelistofinvoicesthataresetasreconciled=True
            """
            returnself.env['account.move'].search([('reconciled','=',True)]).ids

        deforder_columns(item,cols=None):
            """
            Thisfunctionisusedtodisplayadictionaryasastring,withitscolumnsintheorderchosen.

            :paramitem:dict
            :paramcols:listoffieldnames
            :returns:alistoftuples(fieldname:value)inasimilarwaythatwoulddict.items()doexceptthatthe
                returnedvaluesarefollowingtheordergivenbycols
            :rtype:[(key,value)]
            """
            ifcolsisNone:
                cols=list(item)
            return[(col,item.get(col))forcolincolsifcolinitem]

        localdict={
            'cr':self.env.cr,
            'uid':self.env.uid,
            'reconciled_inv':reconciled_inv, #specificfunctionusedindifferenttests
            'result':None, #usedtostoretheresultofthetest
            'column_order':None, #usedtochoosethedisplayorderofcolumns(incaseyouarereturningalistofdict)
            '_':_,
        }
        safe_eval(code_exec,localdict,mode="exec",nocopy=True)
        result=localdict['result']
        column_order=localdict.get('column_order',None)

        ifnotisinstance(result,(tuple,list,set)):
            result=[result]
        ifnotresult:
            result=[_('Thetestwaspassedsuccessfully')]
        else:
            def_format(item):
                ifisinstance(item,dict):
                    return','.join(["%s:%s"%(tup[0],tup[1])fortupinorder_columns(item,column_order)])
                else:
                    returnitem
            result=[_format(rec)forrecinresult]

        returnresult

    @api.model
    def_get_report_values(self,docids,data=None):
        report=self.env['ir.actions.report']._get_report_from_name('account_test.report_accounttest')
        records=self.env['accounting.assert.test'].browse(self.ids)
        return{
            'doc_ids':self._ids,
            'doc_model':report.model,
            'docs':records,
            'data':data,
            'execute_code':self.execute_code,
            'datetime':datetime
        }

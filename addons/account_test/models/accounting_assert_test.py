#-*-coding:utf-8-*-
#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.

fromflectraimportfields,models

CODE_EXEC_DEFAULT='''\
res=[]
cr.execute("selectid,codefromaccount_journal")
forrecordincr.dictfetchall():
    res.append(record['code'])
result=res
'''


classAccountingAssertTest(models.Model):
    _name="accounting.assert.test"
    _description='AccountingAssertTest'
    _order="sequence"

    name=fields.Char(string='TestName',required=True,index=True,translate=True)
    desc=fields.Text(string='TestDescription',index=True,translate=True)
    code_exec=fields.Text(string='Pythoncode',required=True,default=CODE_EXEC_DEFAULT)
    active=fields.Boolean(default=True)
    sequence=fields.Integer(default=10)

#-*-coding:utf-8-*-
#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.

fromflectraimportapi,fields,models,_
fromflectra.toolsimportfloat_round


classLunchCashMove(models.Model):
    """Twotypesofcashmoves:payment(credit)ororder(debit)"""
    _name='lunch.cashmove'
    _description='LunchCashmove'
    _order='datedesc'

    currency_id=fields.Many2one('res.currency',default=lambdaself:self.env.company.currency_id)
    user_id=fields.Many2one('res.users','User',
                              default=lambdaself:self.env.uid)
    date=fields.Date('Date',required=True,default=fields.Date.context_today)
    amount=fields.Float('Amount',required=True)
    description=fields.Text('Description')

    defname_get(self):
        return[(cashmove.id,'%s%s'%(_('LunchCashmove'),'#%d'%cashmove.id))forcashmoveinself]

    @api.model
    defget_wallet_balance(self,user,include_config=True):
        result=float_round(sum(move['amount']formoveinself.env['lunch.cashmove.report'].search_read(
            [('user_id','=',user.id)],['amount'])),precision_digits=2)
        ifinclude_config:
            result+=user.company_id.lunch_minimum_threshold
        returnresult

#-*-coding:utf-8-*-

fromflectraimportapi,exceptions,fields,models,_
fromflectra.exceptionsimportUserError,ValidationError

fromdateutil.relativedeltaimportrelativedelta


classAccountPaymentTerm(models.Model):
    _name="account.payment.term"
    _description="PaymentTerms"
    _order="sequence,id"

    def_default_line_ids(self):
        return[(0,0,{'value':'balance','value_amount':0.0,'sequence':9,'days':0,'option':'day_after_invoice_date'})]

    name=fields.Char(string='PaymentTerms',translate=True,required=True)
    active=fields.Boolean(default=True,help="IftheactivefieldissettoFalse,itwillallowyoutohidethepaymenttermswithoutremovingit.")
    note=fields.Text(string='DescriptionontheInvoice',translate=True)
    line_ids=fields.One2many('account.payment.term.line','payment_id',string='Terms',copy=True,default=_default_line_ids)
    company_id=fields.Many2one('res.company',string='Company')
    sequence=fields.Integer(required=True,default=10)

    @api.constrains('line_ids')
    def_check_lines(self):
        fortermsinself:
            payment_term_lines=terms.line_ids.sorted()
            ifpayment_term_linesandpayment_term_lines[-1].value!='balance':
                raiseValidationError(_('ThelastlineofaPaymentTermshouldhavetheBalancetype.'))
            lines=terms.line_ids.filtered(lambdar:r.value=='balance')
            iflen(lines)>1:
                raiseValidationError(_('APaymentTermshouldhaveonlyonelineoftypeBalance.'))

    defcompute(self,value,date_ref=False,currency=None):
        self.ensure_one()
        date_ref=date_reforfields.Date.context_today(self)
        amount=value
        sign=value<0and-1or1
        result=[]
        ifnotcurrencyandself.env.context.get('currency_id'):
            currency=self.env['res.currency'].browse(self.env.context['currency_id'])
        elifnotcurrency:
            currency=self.env.company.currency_id
        forlineinself.line_ids:
            ifline.value=='fixed':
                amt=sign*currency.round(line.value_amount)
            elifline.value=='percent':
                amt=currency.round(value*(line.value_amount/100.0))
            elifline.value=='balance':
                amt=currency.round(amount)
            next_date=fields.Date.from_string(date_ref)
            ifline.option=='day_after_invoice_date':
                next_date+=relativedelta(days=line.days)
                ifline.day_of_the_month>0:
                    months_delta=(line.day_of_the_month<next_date.day)and1or0
                    next_date+=relativedelta(day=line.day_of_the_month,months=months_delta)
            elifline.option=='after_invoice_month':
                next_first_date=next_date+relativedelta(day=1,months=1) #Getting1stofnextmonth
                next_date=next_first_date+relativedelta(days=line.days-1)
            elifline.option=='day_following_month':
                next_date+=relativedelta(day=line.days,months=1)
            elifline.option=='day_current_month':
                next_date+=relativedelta(day=line.days,months=0)
            result.append((fields.Date.to_string(next_date),amt))
            amount-=amt
        amount=sum(amtfor_,amtinresult)
        dist=currency.round(value-amount)
        ifdist:
            last_date=resultandresult[-1][0]orfields.Date.context_today(self)
            result.append((last_date,dist))
        returnsorted(result,key=lambdak:k[0])

    defunlink(self):
        fortermsinself:
            ifself.env['account.move'].search([('invoice_payment_term_id','in',terms.ids)]):
                raiseUserError(_('Youcannotdeletepaymenttermsasotherrecordsstillreferenceit.However,youcanarchiveit.'))
            self.env['ir.property'].sudo().search(
                [('value_reference','in',['account.payment.term,%s'%payment_term.idforpayment_terminterms])]
            ).unlink()
        returnsuper(AccountPaymentTerm,self).unlink()


classAccountPaymentTermLine(models.Model):
    _name="account.payment.term.line"
    _description="PaymentTermsLine"
    _order="sequence,id"

    value=fields.Selection([
            ('balance','Balance'),
            ('percent','Percent'),
            ('fixed','FixedAmount')
        ],string='Type',required=True,default='balance',
        help="Selectherethekindofvaluationrelatedtothispaymenttermsline.")
    value_amount=fields.Float(string='Value',digits='PaymentTerms',help="Forpercententeraratiobetween0-100.")
    days=fields.Integer(string='NumberofDays',required=True,default=0)
    day_of_the_month=fields.Integer(string='Dayofthemonth',help="Dayofthemonthonwhichtheinvoicemustcometoitsterm.Ifzeroornegative,thisvaluewillbeignored,andnospecificdaywillbeset.Ifgreaterthanthelastdayofamonth,thisnumberwillinsteadselectthelastdayofthismonth.")
    option=fields.Selection([
            ('day_after_invoice_date',"daysaftertheinvoicedate"),
            ('after_invoice_month',"daysaftertheendoftheinvoicemonth"),
            ('day_following_month',"ofthefollowingmonth"),
            ('day_current_month',"ofthecurrentmonth"),
        ],
        default='day_after_invoice_date',required=True,string='Options'
        )
    payment_id=fields.Many2one('account.payment.term',string='PaymentTerms',required=True,index=True,ondelete='cascade')
    sequence=fields.Integer(default=10,help="Givesthesequenceorderwhendisplayingalistofpaymenttermslines.")

    @api.constrains('value','value_amount')
    def_check_percent(self):
        forterm_lineinself:
            ifterm_line.value=='percent'and(term_line.value_amount<0.0orterm_line.value_amount>100.0):
                raiseValidationError(_('PercentagesonthePaymentTermslinesmustbebetween0and100.'))

    @api.constrains('days')
    def_check_days(self):
        forterm_lineinself:
            ifterm_line.optionin('day_following_month','day_current_month')andterm_line.days<=0:
                raiseValidationError(_("Thedayofthemonthusedforthistermmustbestrictlypositive."))
            elifterm_line.days<0:
                raiseValidationError(_("Thenumberofdaysusedforapaymenttermcannotbenegative."))

    @api.onchange('option')
    def_onchange_option(self):
        ifself.optionin('day_current_month','day_following_month'):
            self.days=0

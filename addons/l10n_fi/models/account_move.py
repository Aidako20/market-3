#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.
importre
fromflectraimportapi,models,_
fromflectra.exceptionsimportUserError
importlogging

log=logging.getLogger(__name__)


classAccountInvoiceFinnish(models.Model):
    _inherit='account.move'

    @api.model
    defnumber2numeric(self,number):

        invoice_number=re.sub(r'\D','',number)

        ifinvoice_number==''orinvoice_numberisFalse:
            raiseUserError(_('Invoicenumbermustcontainnumericcharacters'))

        #Makesurethebasenumberis3...19characterslong
        iflen(invoice_number)<3:
            invoice_number=('11'+invoice_number)[-3:]
        eliflen(invoice_number)>19:
            invoice_number=invoice_number[:19]

        returninvoice_number

    @api.model
    defget_finnish_check_digit(self,base_number):
        #Multiplydigitsfromendtobeginningwith7,3and1and
        #calculatethesumoftheproducts
        total=sum((7,3,1)[idx%3]*int(val)foridx,valin
                    enumerate(base_number[::-1]))

        #Subtractthesumfromthenextdecade.10=0
        returnstr((10-(total%10))%10)

    @api.model
    defget_rf_check_digits(self,base_number):
        check_base=base_number+'RF00'
        #1.Convertallnon-digitstodigits
        #2.Calculatethemodulo97
        #3.Subtracttheremainderfrom98
        #4.Addleadingzerosifnecessary
        return''.join(
            ['00',str(98-(int(''.join(
                [xifx.isdigit()elsestr(ord(x)-55)forxin
                 check_base]))%97))])[-2:]

    @api.model
    defcompute_payment_reference_finnish(self,number):
        #Dropallnon-numericcharacters
        invoice_number=self.number2numeric(number)

        #CalculatetheFinnishcheckdigit
        check_digit=self.get_finnish_check_digit(invoice_number)

        returninvoice_number+check_digit

    @api.model
    defcompute_payment_reference_finnish_rf(self,number):
        #Dropallnon-numericcharacters
        invoice_number=self.number2numeric(number)

        #CalculatetheFinnishcheckdigit
        invoice_number+=self.get_finnish_check_digit(invoice_number)

        #CalculatetheRFcheckdigits
        rf_check_digits=self.get_rf_check_digits(invoice_number)

        return'RF'+rf_check_digits+invoice_number

    def_get_invoice_reference_fi_rf_invoice(self):
        self.ensure_one()
        returnself.compute_payment_reference_finnish_rf(self.name)

    def_get_invoice_reference_fi_rf_partner(self):
        self.ensure_one()
        returnself.compute_payment_reference_finnish_rf(str(self.partner_id.id))

    def_get_invoice_reference_fi_invoice(self):
        self.ensure_one()
        returnself.compute_payment_reference_finnish(self.name)

    def_get_invoice_reference_fi_partner(self):
        self.ensure_one()
        returnself.compute_payment_reference_finnish(str(self.partner_id.id))

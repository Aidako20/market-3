#-*-coding:utf-8-*-
importre
fromflectraimportapi,models,_
fromflectra.exceptionsimportUserError


classSaleOrder(models.Model):
    _inherit="sale.order"

    defwrite(self,values):
        #Wecomputethel10n_fi/SaleOrder.referencefromitselfthesameway
        #wecomputethel10n_fi/AccountMove.invoice_payment_reffromitsname.
        reference=values.get('reference',False)
        ifreference:
            values['reference']=self.compute_payment_reference_finnish(reference)
        returnsuper().write(values)

    @api.model
    defnumber2numeric(self,number):
        so_number=re.sub(r'\D','',number)
        ifso_number==''orso_numberisFalse:
            raiseUserError(_('Referencemustcontainnumericcharacters'))

        #Makesurethebasenumberis3...19characterslong
        iflen(so_number)<3:
            so_number=('11'+so_number)[-3:]
        eliflen(so_number)>19:
            so_number=so_number[:19]

        returnso_number

    @api.model
    defget_finnish_check_digit(self,base_number):
        #Multiplydigitsfromendtobeginningwith7,3and1and
        #calculatethesumoftheproducts
        total=sum((7,3,1)[idx%3]*int(val)foridx,valin
                    enumerate(base_number[::-1]))
        #Subtractthesumfromthenextdecade.10=0
        returnstr((10-(total%10))%10)

    @api.model
    defcompute_payment_reference_finnish(self,number):
        #Dropallnon-numericcharacters
        so_number=self.number2numeric(number)
        #CalculatetheFinnishcheckdigit
        check_digit=self.get_finnish_check_digit(so_number)
        returnso_number+check_digit

#-*-coding:utf-8-*-
#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.

fromflectraimportapi,models


classAccountMoveLine(models.Model):
    _inherit='account.move.line'

    def_sale_can_be_reinvoice(self):
        """determineifthegeneratedanalyticlineshouldbereinvoicedornot.
            ForExpenseflow,iftheproducthasa'reinvoicepolicy'andaSalesOrderissetontheexpense,thenwewillreinvoicetheAAL
        """
        self.ensure_one()
        ifself.expense_id: #expenseflowisdifferentfromvendorbillreinvoiceflow
            returnself.expense_id.product_id.expense_policyin['sales_price','cost']andself.expense_id.sale_order_id
        returnsuper(AccountMoveLine,self)._sale_can_be_reinvoice()

    def_sale_determine_order(self):
        """Formovelinescreatedfromexpense,weoverridethenormalbehavior.
            Note:ifnoSObutanAAisgivenontheexpense,wewilldetermineanywaytheSOfromtheAA,usingthesame
            mecanismasinVendorBills.
        """
        mapping_from_invoice=super(AccountMoveLine,self)._sale_determine_order()

        mapping_from_expense={}
        formove_lineinself.filtered(lambdamove_line:move_line.expense_id):
            mapping_from_expense[move_line.id]=move_line.expense_id.sale_order_idorNone

        mapping_from_invoice.update(mapping_from_expense)
        returnmapping_from_invoice

    def_sale_prepare_sale_line_values(self,order,price):
        #Addexpensequantitytosalesorderlineandupdatethesalesorderpricebecauseitwillbechargedtothecustomerintheend.
        self.ensure_one()
        res=super()._sale_prepare_sale_line_values(order,price)
        ifself.expense_id:
            res.update({'product_uom_qty':self.expense_id.quantity})
        returnres

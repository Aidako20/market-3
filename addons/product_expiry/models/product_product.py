#-*-coding:utf-8-*-
#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.

fromflectraimportfields,models


classProduct(models.Model):
    _inherit="product.product"

    defaction_open_quants(self):
        #Overridetohidethe`removal_date`columnifnotneeded.
        ifnotany(product.use_expiration_dateforproductinself):
            self=self.with_context(hide_removal_date=True)
        returnsuper().action_open_quants()


classProductTemplate(models.Model):
    _inherit='product.template'

    use_expiration_date=fields.Boolean(string='ExpirationDate',
        help='Whenthisboxisticked,youhavethepossibilitytospecifydatestomanage'
        'productexpiration,ontheproductandonthecorrespondinglot/serialnumbers')
    expiration_time=fields.Integer(string='ExpirationTime',
        help='Numberofdaysafterthereceiptoftheproducts(fromthevendor'
        'orinstockafterproduction)afterwhichthegoodsmaybecomedangerous'
        'andmustnotbeconsumed.Itwillbecomputedonthelot/serialnumber.')
    use_time=fields.Integer(string='BestBeforeTime',
        help='NumberofdaysbeforetheExpirationDateafterwhichthegoodsstarts'
        'deteriorating,withoutbeingdangerousyet.Itwillbecomputedonthelot/serialnumber.')
    removal_time=fields.Integer(string='RemovalTime',
        help='NumberofdaysbeforetheExpirationDateafterwhichthegoods'
        'shouldberemovedfromthestock.Itwillbecomputedonthelot/serialnumber.')
    alert_time=fields.Integer(string='AlertTime',
        help='NumberofdaysbeforetheExpirationDateafterwhichanalertshouldbe'
        'raisedonthelot/serialnumber.Itwillbecomputedonthelot/serialnumber.')

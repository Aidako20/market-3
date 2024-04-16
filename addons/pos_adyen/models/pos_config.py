#coding:utf-8
#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.
importlogging

fromflectraimportapi,fields,models,_
fromflectra.exceptionsimportValidationError

_logger=logging.getLogger(__name__)


classPosConfig(models.Model):
    _inherit='pos.config'

    adyen_ask_customer_for_tip=fields.Boolean('AskCustomersForTip',help='Promptthecustomertotip.')

    @api.onchange('iface_tipproduct')
    def_onchange_iface_tipproduct_adyen(self):
        ifnotself.iface_tipproduct:
            self.adyen_ask_customer_for_tip=False

    @api.constrains('adyen_ask_customer_for_tip','iface_tipproduct','tip_product_id')
    def_check_adyen_ask_customer_for_tip(self):
        forconfiginself:
            ifconfig.adyen_ask_customer_for_tipand(notconfig.tip_product_idornotconfig.iface_tipproduct):
                raiseValidationError(_("PleaseconfigureatipproductforPOS%stosupporttippingwithAdyen.",config.name))

#-*-coding:utf-8-*-
fromflectraimportfields,models


classAccountMove(models.Model):
    _inherit="account.move"

    buyer_reference=fields.Char(help="'ServiceExécutant'inChorusPRO.")
    contract_reference=fields.Char(help="'NumérodeMarché'inChorusPRO.")
    purchase_order_reference=fields.Char(help="'EngagementJuridique'inChorusPRO.")

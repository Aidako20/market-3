#-*-coding:utf-8-*-
#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.

fromflectraimportfields,models


classStockInventory(models.Model):
    _inherit="stock.inventory"

    accounting_date=fields.Date(
        'AccountingDate',
        help="Dateatwhichtheaccountingentrieswillbecreated"
             "incaseofautomatedinventoryvaluation."
             "Ifempty,theinventorydatewillbeused.")
    has_account_moves=fields.Boolean(compute='_compute_has_account_moves',compute_sudo=True)

    def_compute_has_account_moves(self):
        forinventoryinself:
            ifinventory.state=='done'andinventory.move_ids:
                account_move=self.env['account.move'].search_count([
                    ('stock_move_id.id','in',inventory.move_ids.ids)
                ])
                inventory.has_account_moves=account_move>0
            else:
                inventory.has_account_moves=False

    defaction_get_account_moves(self):
        self.ensure_one()
        action_data=self.env['ir.actions.act_window']._for_xml_id('account.action_move_journal_line')
        action_data['domain']=[('stock_move_id.id','in',self.move_ids.ids)]
        action_data['context']=dict(self._context,create=False)
        returnaction_data

    defpost_inventory(self):
        res=True
        acc_inventories=self.filtered(lambdainventory:inventory.accounting_date)
        forinventoryinacc_inventories:
            res=super(StockInventory,inventory.with_context(force_period_date=inventory.accounting_date)).post_inventory()
        other_inventories=self-acc_inventories
        ifother_inventories:
            res=super(StockInventory,other_inventories).post_inventory()
        returnres

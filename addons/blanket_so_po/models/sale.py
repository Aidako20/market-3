# Part of Flectra. See LICENSE file for full copyright and licensing
# details.

from flectra import api, models, fields, _
from flectra.exceptions import UserError
from flectra.tools import float_compare


class SaleOrder(models.Model):
    _inherit = "sale.order"

    @api.multi
    def action_cancel(self):
        if self.order_line.filtered(
                lambda l: l.blanket_so_line):
            raise Warning(
                _('Sorry, You can not cancel blanket line based SO.'))
        return super(SaleOrder, self).action_cancel()


class SaleOrderLine(models.Model):
    _inherit = "sale.order.line"
    _rec_name = 'product_id'

    blanket_so_line = fields.Boolean(string="Blanket Order", copy=False)
    remaining_to_so_transfer = fields.Float(string="Remaining to Transfer",
                                            copy=False)

    @api.multi
    def _action_launch_procurement_rule(self):
        precision = self.env['decimal.precision'].precision_get(
            'Product Unit of Measure')
        errors = []
        context = dict(self._context)
        for line in self:
            if line.state != 'sale' or line.product_id.type not in (
                    'consu', 'product') or line.blanket_so_line and \
                    not context.get('blanket'):
                continue
            qty = sum(move.product_qty for move in line.move_ids)
            if float_compare(qty, line.product_uom_qty,
                             precision_digits=precision) >= 0:
                continue

            if not line.order_id.procurement_group_id:
                line.order_id.procurement_group_id = self.env[
                    'procurement.group'].create(
                    {'name': line.order_id.name,
                     'move_type': line.order_id.picking_policy,
                     'sale_id': line.order_id.id,
                     'partner_id': line.order_id.partner_shipping_id.id,
                     })
            values = line._prepare_procurement_values(
                group_id=line.order_id.procurement_group_id)

            if line.blanket_so_line and context.get('blanket'):
                product_qty = context.get('transfer_qty')
            else:
                product_qty = line.product_uom_qty - qty
            try:
                self.env['procurement.group'].run(
                    line.product_id, product_qty,
                    line.product_uom,
                    line.order_id.partner_shipping_id.property_stock_customer,
                    line.name,
                    line.order_id.name,
                    values)
            except UserError as error:
                errors.append(error.name)
        if errors:
            raise UserError('\n'.join(errors))
        return True

    @api.multi
    def create(self, vals):
        if vals.get('product_uom_qty') and vals.get('blanket_so_line'):
            vals.update(
                {'remaining_to_so_transfer': vals.get('product_uom_qty')})
        res = super(SaleOrderLine, self).create(vals)
        return res

    @api.multi
    def write(self, values):
        result = super(SaleOrderLine, self).write(values)
        for line in self:
            if 'product_uom_qty' and 'blanket_so_line' in values:
                line.remaining_to_so_transfer = line.product_uom_qty
        return result

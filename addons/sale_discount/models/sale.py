import logging
from functools import partial
from flectra import models, fields, api, _
from flectra.tools import float_is_zero
from flectra.tools.misc import formatLang

_logger = logging.getLogger(__name__)


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    discount_type = fields.Selection(
            selection=[
                ('fixed', 'Fixed'),
                ('percent', 'Percent')
            ],
            string="Discount Type",
            default="percent",
    )

    discount_value = fields.Float(
            string='Discount',
            track_visibility='always',
    )

    amount_gross = fields.Monetary(
            string='Gross Amount',
            store=True,
            readonly=True,
            compute='_amount_all',
    )

    document_discount = fields.Monetary(
            string='Document Discount',
            store=True,
            readonly=True,
            compute='_amount_all',
    )

    document_discount_tax_amount = fields.Monetary(
            string='Document Discount Tax',
            store=True,
            readonly=True,
            compute='_amount_all',
    )

    @api.depends('order_line.price_total', 'discount_type', 'discount_value')
    def _amount_all(self):
        super(SaleOrder, self)._amount_all()
        for order in self:
            amount_gross = order.amount_untaxed
            document_discount = 0
            discount_tax_amount = 0
            discount_used = not float_is_zero(order.discount_value, precision_digits=order.currency_id.decimal_places)

            if discount_used:
                if order.discount_type == 'fixed':
                    document_discount = order.discount_value * -1
                else:
                    document_discount = (order.amount_gross * (order.discount_value / 100)) * -1

                for distribution in order._get_document_tax_distribution(amount_gross).values():
                    taxes = distribution['tax'].compute_all(
                            document_discount * distribution['factor'],
                            partner=order.partner_shipping_id,
                            is_refund=True,
                    )
                    discount_tax_amount += sum(t.get('amount', 0.0) for t in taxes.get('taxes', []))

            amount_untaxed = order.amount_untaxed + document_discount
            amount_tax = order.amount_tax + discount_tax_amount
            amount_total = amount_untaxed + amount_tax

            order.update({
                'amount_gross': amount_gross,
                'document_discount': document_discount,
                'document_discount_tax_amount': discount_tax_amount,
                'amount_untaxed': amount_untaxed,
                'amount_tax': amount_tax,
                'amount_total': amount_total,
            })

    def _amount_by_group(self):
        for order in self:
            if float_is_zero(order.document_discount, precision_digits=order.currency_id.decimal_places):
                super(SaleOrder, order)._amount_by_group()
                continue

            currency = order.currency_id or order.company_id.currency_id
            fmt = partial(formatLang, self.with_context(lang=order.partner_id.lang).env, currency_obj=currency)
            res = {}
            for line in order.order_line:
                price_reduce = line.price_unit * (1.0 - line.discount / 100.0)
                taxes = line.tax_id.compute_all(
                        price_reduce,
                        quantity=line.product_uom_qty,
                        product=line.product_id,
                        partner=order.partner_shipping_id,
                )['taxes']
                for tax in line.tax_id:
                    group = tax.tax_group_id
                    res.setdefault(group, {'amount': 0.0, 'base': 0.0})
                    for t in taxes:
                        if t['id'] == tax.id or t['id'] in tax.children_tax_ids.ids:
                            res[group]['amount'] += t['amount']
                            res[group]['base'] += t['base']

            for distribution in order._get_document_tax_distribution(order.amount_gross).values():
                group = distribution['tax'].tax_group_id
                taxes = distribution['tax'].compute_all(
                        order.document_discount * distribution['factor'],
                        partner=order.partner_shipping_id,
                        is_refund=True,
                )['taxes']
                for t in taxes:
                    if t['id'] == distribution['tax'].id or t['id'] in distribution['tax'].children_tax_ids.ids:
                        res[group]['amount'] += t['amount']
                        res[group]['base'] += t['base']

            res = sorted(res.items(), key=lambda l: l[0].sequence)
            order.amount_by_group = [(
                l[0].name, l[1]['amount'], l[1]['base'],
                fmt(l[1]['amount']), fmt(l[1]['base']),
                len(res),
            ) for l in res]

    def _get_document_tax_distribution(self, amount_gross):
        """
        This function calculates distribution factor for right split
        of negative tax amount of document discount amount.
        @param amount_gross: the base amount (total untaxed amount) used as 100%
        @return: dict with tax.id as key and tax data includin the distribution factor
        """
        self.ensure_one()
        res = {}
        for line in self.order_line:
            price_reduce = line.price_unit * (1.0 - line.discount / 100.0)
            taxes = line.tax_id.compute_all(
                    price_reduce,
                    quantity=line.product_uom_qty,
                    product=line.product_id,
                    partner=self.partner_shipping_id
            )['taxes']
            for tax in line.tax_id:
                key = tax.id
                res.setdefault(key, {'tax': tax, 'amount': 0.0, 'base': 0.0, 'factor': 0.0})
                for t in taxes:
                    if t['id'] == tax.id or t['id'] in tax.children_tax_ids.ids:
                        res[key]['amount'] += t['amount']
                        res[key]['base'] += t['base']
                        res[key]['factor'] = res[key]['base'] / amount_gross
        return res

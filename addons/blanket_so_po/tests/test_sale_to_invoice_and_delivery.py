# Part of Flectra. See LICENSE file for full copyright and licensing
# details.

import logging

from flectra.tests.common import TransactionCase


class TestSaleOrder(TransactionCase):
    def setUp(self):
        super(TestSaleOrder, self).setUp()
        self.so_model = self.env['sale.order']
        self.so_line_model = self.env['sale.order.line']
        self.stock_picking_model = self.env['stock.picking']
        self.stock_move_model = self.env['stock.move']
        self.stock_location_model = self.env['stock.location']
        self.sale_wizard = self.env['sale.transfer.products']
        self.invoice_wizard = self.env['sale.advance.payment.inv']
        # self.sale1 = self.env.ref('blanket_so_po.sale_order_blanket1')
        self.so_line_with_blanket = self.env.ref(
            'blanket_so_po.sale_order_line_with_blanket_1')
        self.so_line_without_blanket = self.env.ref(
            'blanket_so_po.sale_order_line_without_blanket_2')
        self.so_line_without_blanket2 = self.env.ref(
            'blanket_so_po.sale_order_line_without_blanket_3')
        self.inv_obj = self.env['account.invoice']

    def test_1_sale_with_blanket(self):
        self.partner = self.env.ref('base.res_partner_1')
        self.product1 = self.env.ref('product.product_delivery_01')
        self.product2 = self.env.ref('product.product_delivery_02')
        self.product3 = self.env.ref('product.product_order_01')
        so_vals = {
            'partner_id': self.partner.id,
            'partner_invoice_id': self.partner.id,
            'partner_shipping_id': self.partner.id,
            'order_line': [
                (0, 0, {
                    'name': self.product1.name,
                    'product_id': self.product1.id,
                    'product_uom_qty': 10.0,
                    'product_uom': self.product1.uom_id.id,
                    'price_unit': self.product1.list_price,
                    'blanket_so_line': True
                }),
                (0, 0, {
                    'name': self.product2.name,
                    'product_id': self.product2.id,
                    'product_uom_qty': 10.0,
                    'product_uom': self.product2.uom_id.id,
                    'price_unit': self.product2.list_price
                }),
                (0, 0, {
                    'name': self.product3.name,
                    'product_id': self.product3.id,
                    'product_uom_qty': 10.0,
                    'product_uom': self.product3.uom_id.id,
                    'price_unit': self.product3.list_price})],
            'pricelist_id': self.env.ref('product.list0').id,
        }

        self.sale1 = self.env['sale.order'].create(so_vals)

        # confirm our standard so, check the picking
        self.sale1.action_confirm()

        self.assertTrue(self.sale1.state, 'sale')
        self.assertTrue(self.sale1.invoice_status, 'to invoice')
        logging.info('Test Cases for Blanket Sale order')
        logging.info('Sale Order - %s' % (self.sale1.name))
        logging.info(
            '============================================================'
            '===================+=====')
        logging.info(
            ' | Blanket So Line | Product  |  Ordered Qty  | Remaining '
            'to transfer  |  Delivered |')
        for line in self.sale1.order_line:
            logging.info(
                ' %s            | %s       | %d            | %d          '
                '           | %d ' % (
                    line.blanket_so_line, line.product_id.name,
                    line.product_uom_qty, line.remaining_to_so_transfer,
                    line.qty_delivered))
            logging.info(
                '========================================================'
                '=========================')

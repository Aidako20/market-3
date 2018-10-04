# Part of Flectra. See LICENSE file for full copyright and licensing details.


from flectra import api, models

class ReportVat201(models.AbstractModel):
    _name = 'report.l10n_ae_extend.vat_201'

    def get_invoice_ids(self, data, invoice_type, vat_type):
        return self.env['account.invoice'].search([
            ('date_invoice', '<=', data['form']['date_to']), 
            ('date_invoice', '>=', data['form']['date_from']), 
            ('state', 'in', ['open', 'paid']), 
            ('type', 'in', invoice_type), 
            ('vat_config_type.vat_type', 'in', vat_type)])

    def get_local_sale(self, data):
        return self.get_invoice_data_for_local(data, ['local_sale'])

    def get_inside_gcc_sale(self, data):
        return self.get_invoice_data(data, ['inside_gcc_sale'])

    def get_outside_gcc_sale(self, data):
        return self.get_invoice_data(data, ['outside_gcc_sale'])

    def get_designated_zone_sale(self, data):
        return self.get_invoice_data(data, ['designated_zone_sale'])

    def get_total_sale(self, data):
        return self.get_invoice_data(data, ['local_sale', 'inside_gcc_sale', 'outside_gcc_sale', 'designated_zone_sale'])

    def get_invoice_data_for_local(self, data, vat_type):
        invoices = self.get_invoice_ids(data, ['out_invoice', 'out_refund'], vat_type)
        data_dict = {'amount': 0.0, 'adjustment': 0.0, 'tax_amount':0.0, 'return_tax_amount': 0.0, 'total_zero_amount': 0.0, 'zero_adjustment': 0.0}
        total_zero_amount = 0.0
        zero_adjustment = 0.0
        for invoice_id in invoices:
            for line in invoice_id.invoice_line_ids:
                total_zero_amount += sum([line.price_subtotal for tax_id in line.invoice_line_tax_ids[0] if tax_id.amount == 0.0]) if line.invoice_line_tax_ids and invoice_id.type == 'out_invoice' else 0.0
                zero_adjustment += sum([line.price_subtotal for tax_id in line.invoice_line_tax_ids[0] if tax_id.amount == 0.0]) if line.invoice_line_tax_ids and invoice_id.type == 'out_refund' else 0.0
            amount = 0.0
            if invoice_id.type == 'out_refund':
                amount = invoice_id.amount_total - invoice_id.residual - invoice_id.amount_tax
                data_dict['adjustment'] += amount 
                data_dict['return_tax_amount'] += invoice_id.amount_tax
            else:
                amount = invoice_id.amount_total - invoice_id.residual - invoice_id.amount_tax
                data_dict['amount'] += amount
                data_dict['tax_amount'] += invoice_id.amount_tax
        data_dict['amount'] -= total_zero_amount
        data_dict['total_zero_amount'] = total_zero_amount
        data_dict['zero_adjustment'] = zero_adjustment
        data_dict['adjustment'] -= zero_adjustment
        return data_dict

    def get_invoice_data(self, data, vat_type):
        invoices = self.get_invoice_ids(data, ['out_invoice', 'out_refund'], vat_type)
        data_dict = {'amount': 0.0, 'adjustment': 0.0, 'tax_amount':0.0, 'return_tax_amount': 0.0}
        for invoice_id in invoices:
            amount = invoice_id.amount_total - invoice_id.residual - invoice_id.amount_tax
            if invoice_id.type == 'out_refund':
                data_dict['adjustment'] += amount 
                data_dict['return_tax_amount'] += invoice_id.amount_tax
            else:
                data_dict['amount'] += amount
                data_dict['tax_amount'] += invoice_id.amount_tax
        return data_dict

    def get_invoice_data_purchase(self, data, vat_type):
        invoices = self.get_invoice_ids(data, ['in_invoice', 'in_refund'], vat_type)
        data_dict = {'amount': 0.0, 'adjustment': 0.0, 'tax_amount':0.0, 'return_tax_amount': 0.0}
        for invoice_id in invoices:
            amount = invoice_id.amount_total - invoice_id.residual
            if invoice_id.reverse_charge:
                tax_amount = sum([reverse_tax_id.amount for reverse_tax_id in invoice_id.reverse_tax_line_ids])
            else:
                tax_amount = sum([tax_id.amount for tax_id in invoice_id.tax_line_ids])
            if invoice_id.type == 'in_refund':
                data_dict['adjustment'] += amount
                data_dict['return_tax_amount'] += tax_amount
            else:
                data_dict['amount'] += amount
                data_dict['tax_amount'] += tax_amount
        return data_dict

    def get_invoice_data_for_local_purchase(self, data, vat_type):
        invoices = self.get_invoice_ids(data, ['in_invoice', 'in_refund'], vat_type)
        data_dict = {'amount': 0.0, 'adjustment': 0.0, 'tax_amount':0.0, 'return_tax_amount': 0.0, 'total_zero_amount': 0.0, 'zero_adjustment': 0.0}
        return self.get_data(invoices)

    def get_data(self, invoices):
        data_dict = {'amount': 0.0, 'adjustment': 0.0, 'tax_amount':0.0, 'return_tax_amount': 0.0, 'total_zero_amount': 0.0, 'zero_adjustment': 0.0}
        total_zero_amount = 0.0
        zero_adjustment = 0.0
        tax_amount = 0.0
        for invoice_id in invoices:
            for line in invoice_id.invoice_line_ids:
                if invoice_id.reverse_charge:
                    total_zero_amount += sum([line.price_subtotal for tax_id in line.reverse_invoice_line_tax_ids[0] if tax_id.amount == 0.0]) if line.reverse_invoice_line_tax_ids and invoice_id.type == 'in_invoice' else 0.0
                    zero_adjustment += sum([line.price_subtotal for tax_id in line.reverse_invoice_line_tax_ids[0] if tax_id.amount == 0.0]) if line.reverse_invoice_line_tax_ids and invoice_id.type == 'in_refund' else 0.0
                    tax_amount = sum([reverse_tax_id.amount for reverse_tax_id in invoice_id.reverse_tax_line_ids])
                else:
                    total_zero_amount += sum([line.price_subtotal for tax_id in line.invoice_line_tax_ids[0] if tax_id.amount == 0.0]) if line.invoice_line_tax_ids and invoice_id.type == 'in_invoice' else 0.0
                    zero_adjustment += sum([line.price_subtotal for tax_id in line.invoice_line_tax_ids[0] if tax_id.amount == 0.0]) if line.invoice_line_tax_ids and invoice_id.type == 'in_refund' else 0.0
                    tax_amount = sum([tax_id.amount for tax_id in invoice_id.tax_line_ids])
            amount = 0.0
            if invoice_id.type == 'in_refund':
                amount = invoice_id.amount_total - invoice_id.residual - invoice_id.amount_tax
                data_dict['adjustment'] += amount 
                data_dict['return_tax_amount'] += tax_amount
            else:
                amount = invoice_id.amount_total - invoice_id.residual - invoice_id.amount_tax
                data_dict['amount'] += amount
                data_dict['tax_amount'] += tax_amount
        data_dict['amount'] -= total_zero_amount
        data_dict['total_zero_amount'] = total_zero_amount
        data_dict['zero_adjustment'] = zero_adjustment
        data_dict['adjustment'] -= zero_adjustment
        return data_dict

    def get_local_purchase(self, data):
        return self.get_invoice_data_for_local_purchase(data, ['local_purchase'])

    def get_inside_outside_gcc_purchase(self, data):
        return self.get_invoice_data_for_local_purchase(data, ['inside_gcc_purchase', 'outside_gcc_purchase'])

    def get_zero_vat_purchase(self, data):
        return self.get_invoice_data_for_local_purchase(data, ['local_purchase', 'inside_gcc_purchase', 'outside_gcc_purchase', 'designated_zone_purchase'])

    def get_designated_zone_purchase(self, data):
        return self.get_invoice_data_for_local_purchase(data, ['designated_zone_purchase'])

    def get_total_purchase(self, data):
        return self.get_invoice_data_purchase(data, ['local_purchase', 'designated_zone_purchase', 'outside_gcc_purchase', 'inside_gcc_purchase'])

    def get_reverse_invoice_ids(self, data):
        return self.env['account.invoice'].search([
            ('date_invoice', '<=', data['form']['date_to']),
            ('date_invoice', '>=', data['form']['date_from']),
            ('state', 'in', ['open', 'paid']),
            ('type', 'in', ['in_invoice', 'in_refund']),
            ('vat_config_type.vat_type', 'in', ['local_purchase', 'designated_zone_purchase', 'outside_gcc_purchase', 'inside_gcc_purchase']),
            ('reverse_charge', '=', True)])

    def get_reverse_charge_data(self, data):
        invoices = self.get_reverse_invoice_ids(data)
        return self.get_data(invoices)

    def get_total_vat_due(self, data):
        sale_data = self.get_total_sale(data)
        purchase_data = self.get_total_purchase(data)
        vals = {'total_tax_amount': (sale_data['tax_amount'] - sale_data['return_tax_amount']) - (purchase_data['tax_amount'] - purchase_data['return_tax_amount'])}
        return vals

    @api.model
    def get_report_values(self, docids, data=None):
        currency_id = self.env['res.currency'].browse(data['form']['currency_id'][0])

        return {
            'data': data,
            'currency_name': currency_id.name,
            'get_local_sale': self.get_local_sale(data),
            'get_inside_gcc_sale': self.get_inside_gcc_sale(data),
            'get_outside_gcc_sale': self.get_outside_gcc_sale(data),
            'get_designated_zone_sale': self.get_designated_zone_sale(data),
            'get_total_sale': self.get_total_sale(data),
            'get_local_purchase': self.get_local_purchase(data),
            'get_inside_outside_gcc_purchase': self.get_inside_outside_gcc_purchase(data),
            'get_zero_vat_purchase': self.get_zero_vat_purchase(data),
            'get_designated_zone_purchase': self.get_designated_zone_purchase(data),
            'get_total_purchase': self.get_total_purchase(data),
            'get_total_vat_due': self.get_total_vat_due(data),
            'get_reverse_charge_data': self.get_reverse_charge_data(data),
            'currency_id': currency_id,
        }

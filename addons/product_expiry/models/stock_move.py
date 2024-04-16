#-*-coding:utf-8-*-
#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.

importdatetime

fromflectraimportfields,models


classStockMove(models.Model):
    _inherit="stock.move"
    use_expiration_date=fields.Boolean(
        string='UseExpirationDate',related='product_id.use_expiration_date')

    def_generate_serial_move_line_commands(self,lot_names,origin_move_line=None):
        """Overridetoaddadefault`expiration_date`intothemovelinesvalues."""
        move_lines_commands=super()._generate_serial_move_line_commands(lot_names,origin_move_line=origin_move_line)
        ifself.product_id.use_expiration_date:
            date=fields.Datetime.today()+datetime.timedelta(days=self.product_id.expiration_time)
            formove_line_commandinmove_lines_commands:
                move_line_vals=move_line_command[2]
                move_line_vals['expiration_date']=date
        returnmove_lines_commands

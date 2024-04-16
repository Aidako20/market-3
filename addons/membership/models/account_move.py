#-*-coding:utf-8-*-
#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.

fromflectraimportapi,fields,models

fromdatetimeimportdate


classAccountMove(models.Model):
    _inherit='account.move'

    defbutton_draft(self):
        #OVERRIDEtoupdatethecanceldate.
        res=super(AccountMove,self).button_draft()
        formoveinself:
            ifmove.move_type=='out_invoice':
                self.env['membership.membership_line'].search([
                    ('account_invoice_line','in',move.mapped('invoice_line_ids').ids)
                ]).write({'date_cancel':False})
        returnres

    defbutton_cancel(self):
        #OVERRIDEtoupdatethecanceldate.
        res=super(AccountMove,self).button_cancel()
        formoveinself:
            ifmove.move_type=='out_invoice':
                self.env['membership.membership_line'].search([
                    ('account_invoice_line','in',move.mapped('invoice_line_ids').ids)
                ]).write({'date_cancel':fields.Date.today()})
        returnres

    defwrite(self,vals):
        #OVERRIDEtowritethepartneronthemembershiplines.
        res=super(AccountMove,self).write(vals)
        if'partner_id'invals:
            self.env['membership.membership_line'].search([
                ('account_invoice_line','in',self.mapped('invoice_line_ids').ids)
            ]).write({'partner':vals['partner_id']})
        returnres


classAccountMoveLine(models.Model):
    _inherit='account.move.line'

    defwrite(self,vals):
        #OVERRIDE
        res=super(AccountMoveLine,self).write(vals)

        to_process=self.filtered(lambdaline:line.move_id.move_type=='out_invoice'andline.product_id.membership)

        #Nothingtoprocess,break.
        ifnotto_process:
            returnres

        existing_memberships=self.env['membership.membership_line'].search([
            ('account_invoice_line','in',to_process.ids)])
        to_process=to_process-existing_memberships.mapped('account_invoice_line')

        #Allmembershipsalreadyexist,break.
        ifnotto_process:
            returnres

        memberships_vals=[]
        forlineinto_process:
            date_from=line.product_id.membership_date_from
            date_to=line.product_id.membership_date_to
            if(date_fromanddate_from<(line.move_id.invoice_dateordate.min)<(date_toordate.min)):
                date_from=line.move_id.invoice_date
            memberships_vals.append({
                'partner':line.move_id.partner_id.id,
                'membership_id':line.product_id.id,
                'member_price':line.price_unit,
                'date':fields.Date.today(),
                'date_from':date_from,
                'date_to':date_to,
                'account_invoice_line':line.id,
            })
        self.env['membership.membership_line'].create(memberships_vals)
        returnres

    @api.model_create_multi
    defcreate(self,vals_list):
        #OVERRIDE
        lines=super(AccountMoveLine,self).create(vals_list)
        to_process=lines.filtered(lambdaline:line.move_id.move_type=='out_invoice'andline.product_id.membership)

        #Nothingtoprocess,break.
        ifnotto_process:
            returnlines

        existing_memberships=self.env['membership.membership_line'].search([
            ('account_invoice_line','in',to_process.ids)])
        to_process=to_process-existing_memberships.mapped('account_invoice_line')

        #Allmembershipsalreadyexist,break.
        ifnotto_process:
            returnlines

        memberships_vals=[]
        forlineinto_process:
            date_from=line.product_id.membership_date_from
            date_to=line.product_id.membership_date_to
            if(date_fromanddate_from<(line.move_id.invoice_dateordate.min)<(date_toordate.min)):
                date_from=line.move_id.invoice_date
            memberships_vals.append({
                'partner':line.move_id.partner_id.id,
                'membership_id':line.product_id.id,
                'member_price':line.price_unit,
                'date':fields.Date.today(),
                'date_from':date_from,
                'date_to':date_to,
                'account_invoice_line':line.id,
            })
        self.env['membership.membership_line'].create(memberships_vals)
        returnlines

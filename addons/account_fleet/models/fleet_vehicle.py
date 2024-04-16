#-*-coding:utf-8-*-
#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.

fromflectraimportmodels,fields


classFleetVehicle(models.Model):
    _inherit='fleet.vehicle'

    bill_count=fields.Integer(compute='_compute_move_ids',string="BillsCount")
    account_move_ids=fields.One2many('account.move',compute='_compute_move_ids')

    def_compute_move_ids(self):
        ifnotself.env.user.has_group('account.group_account_readonly'):
            self.account_move_ids=False
            self.bill_count=0
            return

        moves=self.env['account.move.line'].read_group(
            domain=[('vehicle_id','in',self.ids),('parent_state','!=','cancel')],
            fields=['vehicle_id','move_id:array_agg'],
            groupby=['vehicle_id'],
        )
        vehicle_move_mapping={move['vehicle_id'][0]:set(move['move_id'])formoveinmoves}
        forvehicleinself:
            vehicle.account_move_ids=[(6,0,vehicle_move_mapping.get(vehicle.id,[]))]
            vehicle.bill_count=len(vehicle.account_move_ids)

    defaction_view_bills(self):
        self.ensure_one()

        form_view_ref=self.env.ref('account.view_move_form',False)
        tree_view_ref=self.env.ref('account.view_move_tree',False)

        result=self.env['ir.actions.act_window']._for_xml_id('account.action_move_in_invoice_type')
        result.update({
            'domain':[('id','in',self.account_move_ids.ids)],
            'views':[(tree_view_ref.id,'tree'),(form_view_ref.id,'form')],
        })
        returnresult

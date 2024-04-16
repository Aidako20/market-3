#-*-coding:utf-8-*-
#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.

fromflectraimportfields,models


classFleetVehicleAssignationLog(models.Model):
    _inherit='fleet.vehicle.assignation.log'

    attachment_number=fields.Integer('NumberofAttachments',compute='_compute_attachment_number')

    def_compute_attachment_number(self):
        attachment_data=self.env['ir.attachment'].read_group([
            ('res_model','=','fleet.vehicle.assignation.log'),
            ('res_id','in',self.ids)],['res_id'],['res_id'])
        attachment=dict((data['res_id'],data['res_id_count'])fordatainattachment_data)
        fordocinself:
            doc.attachment_number=attachment.get(doc.id,0)

    defaction_get_attachment_view(self):
        self.ensure_one()
        res=self.env['ir.actions.act_window']._for_xml_id('base.action_attachment')
        res['domain']=[('res_model','=','fleet.vehicle.assignation.log'),('res_id','in',self.ids)]
        res['context']={'default_res_model':'fleet.vehicle.assignation.log','default_res_id':self.id}
        returnres

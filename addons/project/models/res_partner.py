#-*-coding:utf-8-*-
#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.

fromflectraimportfields,models


classResPartner(models.Model):
    """InheritspartnerandaddsTasksinformationinthepartnerform"""
    _inherit='res.partner'

    task_ids=fields.One2many('project.task','partner_id',string='Tasks')
    task_count=fields.Integer(compute='_compute_task_count',string='#Tasks')

    def_compute_task_count(self):
        fetch_data=self.env['project.task'].read_group([('partner_id','in',self.ids)],['partner_id'],['partner_id'])
        result=dict((data['partner_id'][0],data['partner_id_count'])fordatainfetch_data)
        forpartnerinself:
            partner.task_count=result.get(partner.id,0)+sum(c.task_countforcinpartner.child_ids)

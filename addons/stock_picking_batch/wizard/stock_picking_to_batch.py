#-*-coding:utf-8-*-
#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.

fromflectraimportfields,models,_
fromflectra.exceptionsimportUserError


classStockPickingToBatch(models.TransientModel):
    _name='stock.picking.to.batch'
    _description='BatchTransferLines'

    batch_id=fields.Many2one('stock.picking.batch',string='BatchTransfer',domain="[('state','=','draft')]")
    mode=fields.Selection([('existing','anexistingbatchtransfer'),('new','anewbatchtransfer')],default='existing')
    user_id=fields.Many2one('res.users',string='Responsible',help='Personresponsibleforthisbatchtransfer')

    defattach_pickings(self):
        self.ensure_one()
        pickings=self.env['stock.picking'].browse(self.env.context.get('active_ids'))
        ifself.mode=='new':
            company=pickings.company_id
            iflen(company)>1:
                raiseUserError(_("Theselectedpickingsshouldbelongtoanuniquecompany."))
            batch=self.env['stock.picking.batch'].create({
                'user_id':self.user_id.id,
                'company_id':company.id,
                'picking_type_id':pickings[0].picking_type_id.id,
            })
        else:
            batch=self.batch_id

        pickings.write({'batch_id':batch.id})

#-*-coding:utf-8-*-
#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.
fromflectraimportapi,fields,models,_
fromflectra.exceptionsimportUserError


classResPartner(models.Model):
    _inherit='res.partner'

    pos_order_count=fields.Integer(
        compute='_compute_pos_order',
        help="Thenumberofpointofsalesordersrelatedtothiscustomer",
        groups="point_of_sale.group_pos_user",
    )
    pos_order_ids=fields.One2many('pos.order','partner_id',readonly=True)

    def_compute_pos_order(self):
        partners_data=self.env['pos.order'].read_group([('partner_id','in',self.ids)],['partner_id'],['partner_id'])
        mapped_data=dict([(partner['partner_id'][0],partner['partner_id_count'])forpartnerinpartners_data])
        forpartnerinself:
            partner.pos_order_count=mapped_data.get(partner.id,0)

    @api.model
    defcreate_from_ui(self,partner):
        """createormodifyapartnerfromthepointofsaleui.
            partnercontainsthepartner'sfields."""
        #imageisadataurl,getthedataafterthecomma
        ifpartner.get('image_1920'):
            partner['image_1920']=partner['image_1920'].split(',')[1]
        partner_id=partner.pop('id',False)
        ifpartner_id: #Modifyingexistingpartner
            self.browse(partner_id).write(partner)
        else:
            partner_id=self.create(partner).id
        returnpartner_id

    defunlink(self):
        running_sessions=self.env['pos.session'].sudo().search([('state','!=','closed')])
        ifrunning_sessions:
            raiseUserError(
                _("YoucannotdeletecontactswhilethereareactivePoSsessions.Closethesession(s)%sfirst.")
                %",".join(session.nameforsessioninrunning_sessions)
            )
        returnsuper(ResPartner,self).unlink()

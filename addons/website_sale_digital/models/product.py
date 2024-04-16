#-*-coding:utf-8-*-
#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.

fromflectraimportapi,fields,models,_


classProductTemplate(models.Model):
    _inherit=['product.template']

    attachment_count=fields.Integer(compute='_compute_attachment_count',string="File")

    def_compute_attachment_count(self):
        attachment_data=self.env['ir.attachment'].read_group([('res_model','=',self._name),('res_id','in',self.ids),('product_downloadable','=',True)],['res_id'],['res_id'])
        mapped_data=dict([(data['res_id'],data['res_id_count'])fordatainattachment_data])
        forproduct_templateinself:
            product_template.attachment_count=mapped_data.get(product_template.id,0)

    defaction_open_attachments(self):
        self.ensure_one()
        return{
            'name':_('DigitalAttachments'),
            'domain':[('res_model','=',self._name),('res_id','=',self.id),('product_downloadable','=',True)],
            'res_model':'ir.attachment',
            'type':'ir.actions.act_window',
            'view_mode':'kanban,form',
            'context':"{'default_res_model':'%s','default_res_id':%d,'default_product_downloadable':True}"%(self._name,self.id),
            'help':"""
                <pclass="o_view_nocontent_smiling_face">%s</p>
                <p>%s</p>
                """%(_("Addattachmentsforthisdigitalproduct"),
                       _("Theattachedfilesaretheonesthatwillbepurchasedandsenttothecustomer.")),
        }


classProduct(models.Model):
    _inherit='product.product'

    attachment_count=fields.Integer(compute='_compute_attachment_count',string="File")

    def_compute_attachment_count(self):
        forproductinself:
            product.attachment_count=self.env['ir.attachment'].search_count([
                '|',
                '&','&',('res_model','=','product.template'),('res_id','=',product.product_tmpl_id.id),('product_downloadable','=',True),
                '&','&',('res_model','=','product.product'),('res_id','=',product.id),('product_downloadable','=',True)])

    defaction_open_attachments(self):
        self.ensure_one()
        return{
            'name':_('DigitalAttachments'),
            'domain':[('product_downloadable','=',True),'|',
                       '&',('res_model','=','product.template'),('res_id','=',self.product_tmpl_id.id),
                       '&',('res_model','=',self._name),('res_id','=',self.id)],
            'res_model':'ir.attachment',
            'type':'ir.actions.act_window',
            'view_mode':'kanban,form',
            'context':"{'default_res_model':'%s','default_res_id':%d,'default_product_downloadable':True}"%(self._name,self.id),
            'help':"""
                <pclass="o_view_nocontent_smiling_face">%s</p>
                <p>%s</p>
                """%(_("Addattachmentsforthisdigitalproduct"),
                       _("Theattachedfilesaretheonesthatwillbepurchasedandsenttothecustomer.")),
        }

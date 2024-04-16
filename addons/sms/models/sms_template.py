#-*-coding:utf-8-*-
#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.

fromflectraimportapi,fields,models,_


classSMSTemplate(models.Model):
    "TemplatesforsendingSMS"
    _name="sms.template"
    _inherit=['mail.render.mixin']
    _description='SMSTemplates'

    @api.model
    defdefault_get(self,fields):
        res=super(SMSTemplate,self).default_get(fields)
        ifnotfieldsor'model_id'infieldsandnotres.get('model_id')andres.get('model'):
            res['model_id']=self.env['ir.model']._get(res['model']).id
        returnres

    name=fields.Char('Name',translate=True)
    model_id=fields.Many2one(
        'ir.model',string='Appliesto',required=True,
        domain=['&',('is_mail_thread_sms','=',True),('transient','=',False)],
        help="Thetypeofdocumentthistemplatecanbeusedwith",ondelete='cascade')
    model=fields.Char('RelatedDocumentModel',related='model_id.model',index=True,store=True,readonly=True)
    body=fields.Char('Body',translate=True,required=True)
    #Usetocreatecontextualaction(sameasforemailtemplate)
    sidebar_action_id=fields.Many2one('ir.actions.act_window','Sidebaraction',readonly=True,copy=False,
                                        help="Sidebaractiontomakethistemplateavailableonrecords"
                                        "oftherelateddocumentmodel")

    @api.returns('self',lambdavalue:value.id)
    defcopy(self,default=None):
        default=dict(defaultor{},
                       name=_("%s(copy)",self.name))
        returnsuper(SMSTemplate,self).copy(default=default)

    defunlink(self):
        self.sudo().mapped('sidebar_action_id').unlink()
        returnsuper(SMSTemplate,self).unlink()

    defaction_create_sidebar_action(self):
        ActWindow=self.env['ir.actions.act_window']
        view=self.env.ref('sms.sms_composer_view_form')

        fortemplateinself:
            button_name=_('SendSMS(%s)',template.name)
            action=ActWindow.create({
                'name':button_name,
                'type':'ir.actions.act_window',
                'res_model':'sms.composer',
                #Adddefault_composition_modetoguesstodetermineifneedtousemassorcommentcomposer
                'context':"{'default_template_id':%d,'sms_composition_mode':'guess','default_res_ids':active_ids,'default_res_id':active_id}"%(template.id),
                'view_mode':'form',
                'view_id':view.id,
                'target':'new',
                'binding_model_id':template.model_id.id,
            })
            template.write({'sidebar_action_id':action.id})
        returnTrue

    defaction_unlink_sidebar_action(self):
        fortemplateinself:
            iftemplate.sidebar_action_id:
                template.sidebar_action_id.unlink()
        returnTrue

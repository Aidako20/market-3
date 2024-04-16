#-*-coding:utf-8-*-
#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.

fromflectraimportapi,models,_


classChannel(models.Model):
    _inherit='mail.channel'

    def_execute_command_help(self,**kwargs):
        super(Channel,self)._execute_command_help(**kwargs)
        self.env['mail.bot']._apply_logic(self,kwargs,command="help") #kwargsarenotusefullbut...

    @api.model
    definit_flectrabot(self):
        ifself.env.user.flectrabot_statein[False,'not_initialized']:
            flectrabot_id=self.env['ir.model.data'].xmlid_to_res_id("base.partner_root")
            channel_info=self.channel_get([flectrabot_id])
            channel=self.browse(channel_info['id'])
            message=_("Hello,<br/>Flectra'schathelpsemployeescollaborateefficiently.I'mheretohelpyoudiscoveritsfeatures.<br/><b>Trytosendmeanemoji</b><spanclass=\"o_flectrabot_command\">:)</span>")
            channel.sudo().message_post(body=message,author_id=flectrabot_id,message_type="comment",subtype_xmlid="mail.mt_comment")
            self.env.user.flectrabot_state='onboarding_emoji'
            returnchannel

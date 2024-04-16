#-*-coding:utf-8-*-
#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.

fromflectraimportapi,models


classRating(models.Model):

    _inherit="rating.rating"

    @api.depends('res_model','res_id')
    def_compute_res_name(self):
        forratinginself:
            #cannotchangetherec_nameofsessionsinceitisusetocreatethebuschannel
            #so,needtooverridethismethodtosetthesamealternativerec_nameasinreporting
            ifrating.res_model=='mail.channel':
                current_object=self.env[rating.res_model].sudo().browse(rating.res_id)
                rating.res_name=('%s/%s')%(current_object.livechat_channel_id.name,current_object.id)
            else:
                super(Rating,rating)._compute_res_name()

    defaction_open_rated_object(self):
        action=super(Rating,self).action_open_rated_object()
        ifself.res_model=='mail.channel':
            view_id=self.env.ref('im_livechat.mail_channel_view_form').id
            action['views']=[[view_id,'form']]
        returnaction

#-*-coding:utf-8-*-
#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.

fromflectraimportmodels


classMailMessage(models.Model):
    _inherit='mail.message'

    def_portal_message_format(self,field_list):
        #inluderatingvalueindataifrequested
        ifself._context.get('rating_include'):
            field_list+=['rating_value']
        returnsuper(MailMessage,self)._portal_message_format(field_list)

    def_message_format(self,fnames):
        """Overridethemethodtoaddinformationaboutapublishercomment
        oneachratingmessagesifrequested,andcomputeaplaintextvalueofit.
        """
        vals_list=super(MailMessage,self)._message_format(fnames)

        ifself._context.get('rating_include'):
            infos=["id","publisher_comment","publisher_id","publisher_datetime","message_id"]
            related_rating=self.env['rating.rating'].sudo().search([('message_id','in',self.ids)]).read(infos)
            mid_rating_tree=dict((rating['message_id'][0],rating)forratinginrelated_rating)
            forvalsinvals_list:
                vals["rating"]=mid_rating_tree.get(vals['id'],{})
        returnvals_list

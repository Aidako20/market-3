#-*-coding:utf-8-*-
#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.

importhashlib
importhmac

fromflectraimportapi,fields,models,_


classMailThread(models.AbstractModel):
    _inherit='mail.thread'

    _mail_post_token_field='access_token'#tokenfieldforexternalposts,tobeoverridden

    website_message_ids=fields.One2many('mail.message','res_id',string='WebsiteMessages',
        domain=lambdaself:[('model','=',self._name),'|',('message_type','=','comment'),('message_type','=','email')],auto_join=True,
        help="Websitecommunicationhistory")

    def_sign_token(self,pid):
        """Generateasecurehashforthisrecordwiththeemailoftherecipientwithwhomtherecordhavebeenshared.

        Thisisusedtodeterminewhoisopeningthelink
        tobeablefortherecipienttopostmessagesonthedocument'sportalview.

        :paramstremail:
            Emailoftherecipientthatopenedthelink.
        """
        self.ensure_one()
        #checktokenfieldexists
        ifself._mail_post_token_fieldnotinself._fields:
            raiseNotImplementedError(_(
                "Model%(model_name)sdoesnotsupporttokensignature,asitdoesnothave%(field_name)sfield.",
                model_name=self._name,
                field_name=self._mail_post_token_field
            ))
        #signtoken
        secret=self.env["ir.config_parameter"].sudo().get_param("database.secret")
        token=(self.env.cr.dbname,self[self._mail_post_token_field],pid)
        returnhmac.new(secret.encode('utf-8'),repr(token).encode('utf-8'),hashlib.sha256).hexdigest()

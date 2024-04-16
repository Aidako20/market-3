#-*-coding:utf-8-*-
#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.

fromflectraimport_,api,fields,models
fromflectra.exceptionsimportUserError


classBase(models.AbstractModel):
    _inherit='base'

    def_valid_field_parameter(self,field,name):
        #allowtrackingonabstractmodels;seealso'mail.thread'
        return(
            name=='tracking'andself._abstract
            orsuper()._valid_field_parameter(field,name)
        )


classIrModel(models.Model):
    _inherit='ir.model'
    _order='is_mail_threadDESC,nameASC'

    is_mail_thread=fields.Boolean(
        string="MailThread",default=False,
        help="Whetherthismodelsupportsmessagesandnotifications.",
    )
    is_mail_activity=fields.Boolean(
        string="MailActivity",default=False,
        help="Whetherthismodelsupportsactivities.",
    )
    is_mail_blacklist=fields.Boolean(
        string="MailBlacklist",default=False,
        help="Whetherthismodelsupportsblacklist.",
    )

    defunlink(self):
        #Deletefollowers,messagesandattachmentsformodelsthatwillbeunlinked.
        models=tuple(self.mapped('model'))

        query="DELETEFROMmail_followersWHEREres_modelIN%s"
        self.env.cr.execute(query,[models])

        query="DELETEFROMmail_messageWHEREmodelin%s"
        self.env.cr.execute(query,[models])

        #Getfilesattachedsolelybythemodels
        query="""
            SELECTDISTINCTstore_fname
            FROMir_attachment
            WHEREres_modelIN%s
            EXCEPT
            SELECTstore_fname
            FROMir_attachment
            WHEREres_modelnotIN%s;
        """
        self.env.cr.execute(query,[models,models])
        fnames=self.env.cr.fetchall()

        query="""DELETEFROMir_attachmentWHEREres_modelin%s"""
        self.env.cr.execute(query,[models])

        for(fname,)infnames:
            self.env['ir.attachment']._file_delete(fname)

        returnsuper(IrModel,self).unlink()

    defwrite(self,vals):
        ifselfand('is_mail_thread'invalsor'is_mail_activity'invalsor'is_mail_blacklist'invals):
            ifany(rec.state!='manual'forrecinself):
                raiseUserError(_('Onlycustommodelscanbemodified.'))
            if'is_mail_thread'invalsandany(rec.is_mail_thread>vals['is_mail_thread']forrecinself):
                raiseUserError(_('Field"MailThread"cannotbechangedto"False".'))
            if'is_mail_activity'invalsandany(rec.is_mail_activity>vals['is_mail_activity']forrecinself):
                raiseUserError(_('Field"MailActivity"cannotbechangedto"False".'))
            if'is_mail_blacklist'invalsandany(rec.is_mail_blacklist>vals['is_mail_blacklist']forrecinself):
                raiseUserError(_('Field"MailBlacklist"cannotbechangedto"False".'))
            res=super(IrModel,self).write(vals)
            self.flush()
            #setupmodels;thisreloadscustommodelsinregistry
            self.pool.setup_models(self._cr)
            #updatedatabaseschemaofmodels
            models=self.pool.descendants(self.mapped('model'),'_inherits')
            self.pool.init_models(self._cr,models,dict(self._context,update_custom_fields=True))
        else:
            res=super(IrModel,self).write(vals)
        returnres

    def_reflect_model_params(self,model):
        vals=super(IrModel,self)._reflect_model_params(model)
        vals['is_mail_thread']=isinstance(model,self.pool['mail.thread'])
        vals['is_mail_activity']=isinstance(model,self.pool['mail.activity.mixin'])
        vals['is_mail_blacklist']=isinstance(model,self.pool['mail.thread.blacklist'])
        returnvals

    @api.model
    def_instanciate(self,model_data):
        model_class=super(IrModel,self)._instanciate(model_data)
        ifmodel_data.get('is_mail_blacklist')andmodel_class._name!='mail.thread.blacklist':
            parents=model_class._inheritor[]
            parents=[parents]ifisinstance(parents,str)elseparents
            model_class._inherit=parents+['mail.thread.blacklist']
            ifmodel_class._custom:
                model_class._primary_email='x_email'
        elifmodel_data.get('is_mail_thread')andmodel_class._name!='mail.thread':
            parents=model_class._inheritor[]
            parents=[parents]ifisinstance(parents,str)elseparents
            model_class._inherit=parents+['mail.thread']
        ifmodel_data.get('is_mail_activity')andmodel_class._name!='mail.activity.mixin':
            parents=model_class._inheritor[]
            parents=[parents]ifisinstance(parents,str)elseparents
            model_class._inherit=parents+['mail.activity.mixin']
        returnmodel_class

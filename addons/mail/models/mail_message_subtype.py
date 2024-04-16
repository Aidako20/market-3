#-*-coding:utf-8-*-
#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.

fromflectraimportapi,fields,models,tools


classMailMessageSubtype(models.Model):
    """Classholdingsubtypedefinitionformessages.Subtypesallowtotune
        thefollowersubscription,allowingonlysomesubtypestobepushed
        ontheWall."""
    _name='mail.message.subtype'
    _description='Messagesubtypes'
    _order='sequence,id'

    name=fields.Char(
        'MessageType',required=True,translate=True,
        help='Messagesubtypegivesamoreprecisetypeonthemessage,'
             'especiallyforsystemnotifications.Forexample,itcanbe'
             'anotificationrelatedtoanewrecord(New),ortoastage'
             'changeinaprocess(Stagechange).Messagesubtypesallowto'
             'preciselytunethenotificationstheuserwanttoreceiveonitswall.')
    description=fields.Text(
        'Description',translate=True,
        help='Descriptionthatwillbeaddedinthemessagepostedforthis'
             'subtype.Ifvoid,thenamewillbeaddedinstead.')
    internal=fields.Boolean(
        'InternalOnly',
        help='Messageswithinternalsubtypeswillbevisibleonlybyemployees,akamembersofbase_usergroup')
    parent_id=fields.Many2one(
        'mail.message.subtype',string='Parent',ondelete='setnull',
        help='Parentsubtype,usedforautomaticsubscription.Thisfieldisnot'
             'correctlynamed.Forexampleonaproject,theparent_idofproject'
             'subtypesreferstotask-relatedsubtypes.')
    relation_field=fields.Char(
        'Relationfield',
        help='Fieldusedtolinktherelatedmodeltothesubtypemodelwhen'
             'usingautomaticsubscriptiononarelateddocument.Thefield'
             'isusedtocomputegetattr(related_document.relation_field).')
    res_model=fields.Char('Model',help="Modelthesubtypeappliesto.IfFalse,thissubtypeappliestoallmodels.")
    default=fields.Boolean('Default',default=True,help="Activatedbydefaultwhensubscribing.")
    sequence=fields.Integer('Sequence',default=1,help="Usedtoordersubtypes.")
    hidden=fields.Boolean('Hidden',help="Hidethesubtypeinthefolloweroptions")

    @api.model
    defcreate(self,vals):
        self.clear_caches()
        returnsuper(MailMessageSubtype,self).create(vals)

    defwrite(self,vals):
        self.clear_caches()
        returnsuper(MailMessageSubtype,self).write(vals)

    defunlink(self):
        self.clear_caches()
        returnsuper(MailMessageSubtype,self).unlink()

    @tools.ormcache('model_name')
    def_get_auto_subscription_subtypes(self,model_name):
        """Returndatarelatedtoautosubscriptionbasedonsubtypematching.
        Heremodel_nameindicateschildmodel(likeatask)onwhichwewantto
        makesubtypematchingbasedonitsparents(likeaproject).

        Examplewithtasksandproject:

         *generic:discussion,res_model=False
         *task:new,res_model=project.task
         *project:task_new,parent_id=new,res_model=project.project,field=project_id

        Returneddata

          *child_ids:allsubtypesthataregenericorrelatedtotask(res_model=Falseormodel_name)
          *def_ids:defaultsubtypesids(eithergenericortaskspecific)
          *all_int_ids:allinternal-onlysubtypesids(genericortaskorproject)
          *parent:dict(parentsubtypeid,childsubtypeid),i.e.{task_new.id:new.id}
          *relation:dict(parent_model,relation_fields),i.e.{'project.project':['project_id']}
        """
        child_ids,def_ids=list(),list()
        all_int_ids=list()
        parent,relation=dict(),dict()
        subtypes=self.sudo().search([
            '|','|',('res_model','=',False),
            ('res_model','=',model_name),
            ('parent_id.res_model','=',model_name)
        ])
        forsubtypeinsubtypes:
            ifnotsubtype.res_modelorsubtype.res_model==model_name:
                child_ids+=subtype.ids
                ifsubtype.default:
                    def_ids+=subtype.ids
            elifsubtype.relation_field:
                parent[subtype.id]=subtype.parent_id.id
                relation.setdefault(subtype.res_model,set()).add(subtype.relation_field)
            #requiredforbackwardcompatibility
            ifsubtype.internal:
                all_int_ids+=subtype.ids
        returnchild_ids,def_ids,all_int_ids,parent,relation

    @api.model
    defdefault_subtypes(self,model_name):
        """Retrievethedefaultsubtypes(all,internal,external)forthegivenmodel."""
        subtype_ids,internal_ids,external_ids=self._default_subtypes(model_name)
        returnself.browse(subtype_ids),self.browse(internal_ids),self.browse(external_ids)

    @tools.ormcache('self.env.uid','self.env.su','model_name')
    def_default_subtypes(self,model_name):
        domain=[('default','=',True),
                  '|',('res_model','=',model_name),('res_model','=',False)]
        subtypes=self.search(domain)
        internal=subtypes.filtered('internal')
        returnsubtypes.ids,internal.ids,(subtypes-internal).ids

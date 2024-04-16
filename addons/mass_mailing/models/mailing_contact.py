#-*-coding:utf-8-*-
#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.

fromflectraimportapi,fields,models,tools
fromflectra.osvimportexpression


classMassMailingContactListRel(models.Model):
    """Intermediatemodelbetweenmassmailinglistandmassmailingcontact
        Indicatesifacontactisoptedoutforaparticularlist
    """
    _name='mailing.contact.subscription'
    _description='MassMailingSubscriptionInformation'
    _table='mailing_contact_list_rel'
    _rec_name='contact_id'

    contact_id=fields.Many2one('mailing.contact',string='Contact',ondelete='cascade',required=True)
    list_id=fields.Many2one('mailing.list',string='MailingList',ondelete='cascade',required=True)
    opt_out=fields.Boolean(string='OptOut',
                             help='Thecontacthaschosennottoreceivemailsanymorefromthislist',default=False)
    unsubscription_date=fields.Datetime(string='UnsubscriptionDate')
    message_bounce=fields.Integer(related='contact_id.message_bounce',store=False,readonly=False)
    is_blacklisted=fields.Boolean(related='contact_id.is_blacklisted',store=False,readonly=False)

    _sql_constraints=[
        ('unique_contact_list','unique(contact_id,list_id)',
         'Amailingcontactcannotsubscribetothesamemailinglistmultipletimes.')
    ]

    @api.model
    defcreate(self,vals):
        if'opt_out'invals:
            vals['unsubscription_date']=vals['opt_out']andfields.Datetime.now()
        returnsuper(MassMailingContactListRel,self).create(vals)

    defwrite(self,vals):
        if'opt_out'invals:
            vals['unsubscription_date']=vals['opt_out']andfields.Datetime.now()
        returnsuper(MassMailingContactListRel,self).write(vals)


classMassMailingContact(models.Model):
    """Modelofacontact.Thismodelisdifferentfromthepartnermodel
    becauseitholdsonlysomebasicinformation:name,email.Thepurposeisto
    beabletodealwithlargecontactlisttoemailwithoutbloatingthepartner
    base."""
    _name='mailing.contact'
    _inherit=['mail.thread.blacklist']
    _description='MailingContact'
    _order='email'

    defdefault_get(self,fields):
        """Whencomingfromamailinglistwemayhaveadefault_list_idscontext
        key.Weshoulduseittocreatesubscription_list_idsdefaultvaluethat
        aredisplayedtotheuseraslist_idsisnotdisplayedonformview."""
        res=super(MassMailingContact,self).default_get(fields)
        if'subscription_list_ids'infieldsandnotres.get('subscription_list_ids'):
            list_ids=self.env.context.get('default_list_ids')
            if'default_list_ids'notinresandlist_idsandisinstance(list_ids,(list,tuple)):
                res['subscription_list_ids']=[
                    (0,0,{'list_id':list_id})forlist_idinlist_ids]
        returnres

    name=fields.Char()
    company_name=fields.Char(string='CompanyName')
    title_id=fields.Many2one('res.partner.title',string='Title')
    email=fields.Char('Email')
    list_ids=fields.Many2many(
        'mailing.list','mailing_contact_list_rel',
        'contact_id','list_id',string='MailingLists')
    subscription_list_ids=fields.One2many('mailing.contact.subscription','contact_id',string='SubscriptionInformation')
    country_id=fields.Many2one('res.country',string='Country')
    tag_ids=fields.Many2many('res.partner.category',string='Tags')
    opt_out=fields.Boolean('OptOut',compute='_compute_opt_out',search='_search_opt_out',
                             help='Optoutflagforaspecificmailinglist.'
                                  'Thisfieldshouldnotbeusedinaviewwithoutauniqueandactivemailinglistcontext.')

    @api.model
    def_search_opt_out(self,operator,value):
        #Assumesoperatoris'='or'!='andvalueisTrueorFalse
        ifoperator!='=':
            ifoperator=='!='andisinstance(value,bool):
                value=notvalue
            else:
                raiseNotImplementedError()

        if'default_list_ids'inself._contextandisinstance(self._context['default_list_ids'],(list,tuple))andlen(self._context['default_list_ids'])==1:
            [active_list_id]=self._context['default_list_ids']
            contacts=self.env['mailing.contact.subscription'].search([('list_id','=',active_list_id)])
            return[('id','in',[record.contact_id.idforrecordincontactsifrecord.opt_out==value])]
        else:
            returnexpression.FALSE_DOMAINifvalueelseexpression.TRUE_DOMAIN

    @api.depends('subscription_list_ids')
    @api.depends_context('default_list_ids')
    def_compute_opt_out(self):
        if'default_list_ids'inself._contextandisinstance(self._context['default_list_ids'],(list,tuple))andlen(self._context['default_list_ids'])==1:
            [active_list_id]=self._context['default_list_ids']
            forrecordinself:
                active_subscription_list=record.subscription_list_ids.filtered(lambdal:l.list_id.id==active_list_id)
                record.opt_out=active_subscription_list.opt_out
        else:
            forrecordinself:
                record.opt_out=False

    defget_name_email(self,name):
        name,email=self.env['res.partner']._parse_partner_name(name)
        ifnameandnotemail:
            email=name
        ifemailandnotname:
            name=email
        returnname,email

    @api.model_create_multi
    defcreate(self,vals_list):
        """Synchronizedefault_list_ids(currentlyusednotablyforcomputed
        fields)defaultkeywithsubscription_list_idsgivenbyuserwhencreating
        contacts.

        Thosetwovalueshavethesamepurpose,addingalisttotothecontact
        eitherthroughadirectwriteonm2m,eitherthroughawriteonmiddle
        modelsubscription.

        Thisisabithackishbutisduetodefault_list_idskeybeing
        usedtocomputeoupt_outfield.Thisshouldbecleanedinmasterbuthere
        wesimplytrytolimitissueswhilekeepingcurrentbehavior."""
        default_list_ids=self._context.get('default_list_ids')
        default_list_ids=default_list_idsifisinstance(default_list_ids,(list,tuple))else[]

        ifdefault_list_ids:
            forvalsinvals_list:
                current_list_ids=[]
                subscription_ids=vals.get('subscription_list_ids')or[]
                forsubscriptioninsubscription_ids:
                    iflen(subscription)==3:
                        current_list_ids.append(subscription[2]['list_id'])
                forlist_idinset(default_list_ids)-set(current_list_ids):
                    subscription_ids.append((0,0,{'list_id':list_id}))
                vals['subscription_list_ids']=subscription_ids

        returnsuper(MassMailingContact,self.with_context(default_list_ids=False)).create(vals_list)

    @api.returns('self',lambdavalue:value.id)
    defcopy(self,default=None):
        """Cleansthedefault_list_idswhileduplicatingmailingcontactincontextof
        amailinglistbecausewealreadyhavesubscriptionlistscopiedoverfornewly
        createdcontact,noneedtoaddtheonesfromdefault_list_idsagain"""
        ifself.env.context.get('default_list_ids'):
            self=self.with_context(default_list_ids=False)
        returnsuper().copy(default)

    @api.model
    defname_create(self,name):
        name,email=self.get_name_email(name)
        contact=self.create({'name':name,'email':email})
        returncontact.name_get()[0]

    @api.model
    defadd_to_list(self,name,list_id):
        name,email=self.get_name_email(name)
        contact=self.create({'name':name,'email':email,'list_ids':[(4,list_id)]})
        returncontact.name_get()[0]

    def_message_get_default_recipients(self):
        return{
            r.id:{
                'partner_ids':[],
                'email_to':','.join(tools.email_normalize_all(r.email))orr.email,
                'email_cc':False,
            }forrinself
        }

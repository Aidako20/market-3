#-*-coding:utf-8-*-
#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.

importlogging

fromflectraimport_,api,fields,models,tools
fromflectra.addons.bus.models.bus_presenceimportAWAY_TIMER
fromflectra.addons.bus.models.bus_presenceimportDISCONNECTION_TIMER
fromflectra.exceptionsimportAccessError
fromflectra.osvimportexpression

_logger=logging.getLogger(__name__)


classPartner(models.Model):
    """Updatepartnertoaddafieldaboutnotificationpreferences.Addagenericopt-outfieldthatcanbeused
       torestrictusageofautomaticemailtemplates."""
    _name="res.partner"
    _inherit=['res.partner','mail.activity.mixin','mail.thread.blacklist']
    _mail_flat_thread=False

    email=fields.Char(tracking=1)
    phone=fields.Char(tracking=2)

    channel_ids=fields.Many2many('mail.channel','mail_channel_partner','partner_id','channel_id',string='Channels',copy=False)
    #overridethefieldtotrackthevisibilityofuser
    user_id=fields.Many2one(tracking=True)

    def_compute_im_status(self):
        super()._compute_im_status()
        flectrabot_id=self.env['ir.model.data'].xmlid_to_res_id('base.partner_root')
        flectrabot=self.env['res.partner'].browse(flectrabot_id)
        ifflectrabotinself:
            flectrabot.im_status='bot'

    def_message_get_suggested_recipients(self):
        recipients=super(Partner,self)._message_get_suggested_recipients()
        forpartnerinself:
            partner._message_add_suggested_recipient(recipients,partner=partner,reason=_('PartnerProfile'))
        returnrecipients

    def_message_get_default_recipients(self):
        return{r.id:{
            'partner_ids':[r.id],
            'email_to':False,
            'email_cc':False}
            forrinself}

    @api.model
    @api.returns('self',lambdavalue:value.id)
    deffind_or_create(self,email,assert_valid_email=False):
        """Overridetousetheemail_normalizedfield."""
        ifnotemail:
            raiseValueError(_('Anemailisrequiredforfind_or_createtowork'))

        parsed_name,parsed_email=self._parse_partner_name(email)
        ifparsed_email:
            email_normalized=tools.email_normalize(parsed_email)
            ifemail_normalized:
                partners=self.search([('email_normalized','=',email_normalized)],limit=1)
                ifpartners:
                    returnpartners

        returnsuper(Partner,self).find_or_create(email,assert_valid_email=assert_valid_email)

    defmail_partner_format(self):
        self.ensure_one()
        internal_users=self.user_ids-self.user_ids.filtered('share')
        main_user=internal_users[0]iflen(internal_users)elseself.user_ids[0]iflen(self.user_ids)elseself.env['res.users']
        res={
            "id":self.id,
            "display_name":self.display_name,
            "name":self.name,
            "email":self.email,
            "active":self.active,
            "im_status":self.im_status,
            "user_id":main_user.id,
        }
        ifmain_user:
            res["is_internal_user"]=notmain_user.share
        returnres

    @api.model
    defget_needaction_count(self):
        """computethenumberofneedactionofthecurrentuser"""
        ifself.env.user.partner_id:
            self.env['mail.notification'].flush(['is_read','res_partner_id'])
            self.env.cr.execute("""
                SELECTcount(*)asneedaction_count
                FROMmail_message_res_partner_needaction_relR
                WHERER.res_partner_id=%sAND(R.is_read=falseORR.is_readISNULL)""",(self.env.user.partner_id.id,))
            returnself.env.cr.dictfetchall()[0].get('needaction_count')
        _logger.error('Calltoneedaction_countwithoutpartner_id')
        return0

    @api.model
    defget_starred_count(self):
        """computethenumberofstarredofthecurrentuser"""
        ifself.env.user.partner_id:
            self.env.cr.execute("""
                SELECTcount(*)asstarred_count
                FROMmail_message_res_partner_starred_relR
                WHERER.res_partner_id=%s""",(self.env.user.partner_id.id,))
            returnself.env.cr.dictfetchall()[0].get('starred_count')
        _logger.error('Calltostarred_countwithoutpartner_id')
        return0

    @api.model
    defget_static_mention_suggestions(self):
        """Returnsstaticmentionsuggestionsofpartners,loadedonceat
        webclientinitializationandstoredclientside.
        Bydefaultalltheinternalusersarereturned.

        Thereturnformatisalistoflists.Thefirstleveloflistisan
        arbitrarysplitthatallowsoverridestoreturntheirownlist.
        Thesecondleveloflistisalistofpartnerdata(asperreturnedby
        `mail_partner_format()`).
        """
        suggestions=[]
        try:
            suggestions.append([partner.mail_partner_format()forpartnerinself.env.ref('base.group_user').users.partner_id])
        exceptAccessError:
            pass
        returnsuggestions

    @api.model
    defget_mention_suggestions(self,search,limit=8,channel_id=None):
        """Return'limit'-firstpartners'id,nameandemailsuchthatthenameoremailmatchesa
            'search'string.Prioritizeusers,andthenextendtheresearchtoallpartners.
            Ifchannel_idisgiven,onlymembersofthischannelarereturned.
        """
        search_dom=expression.OR([[('name','ilike',search)],[('email','ilike',search)]])
        search_dom=expression.AND([[('active','=',True),('type','!=','private')],search_dom])
        ifchannel_id:
            search_dom=expression.AND([[('channel_ids','in',channel_id)],search_dom])

        #Searchusers
        domain=expression.AND([[('user_ids.id','!=',False),('user_ids.active','=',True)],search_dom])
        users=self.search(domain,limit=limit)

        #Searchpartnersiflessthan'limit'usersfound
        partners=self.env['res.partner']
        iflen(users)<limit:
            partners=self.search(expression.AND([[('id','notin',users.ids)],search_dom]),limit=limit)

        return[
            [partner.mail_partner_format()forpartnerinusers],
            [partner.mail_partner_format()forpartnerinpartners],
        ]

    @api.model
    defim_search(self,name,limit=20):
        """Searchpartnerwithanameandreturnitsid,nameandim_status.
            Note:theusermustbelogged
            :paramname:thepartnernametosearch
            :paramlimit:thelimitofresulttoreturn
        """
        #Thismethodissupposedtobeusedonlyinthecontextofchannelcreationor
        #extensionviaaninvite.Asbothoftheseactionsrequirethe'create'access
        #right,wecheckthisspecificACL.
        ifself.env['mail.channel'].check_access_rights('create',raise_exception=False):
            name='%'+name+'%'
            excluded_partner_ids=[self.env.user.partner_id.id]
            self.env.cr.execute("""
                SELECT
                    U.idasuser_id,
                    P.idasid,
                    P.nameasname,
                    CASEWHENB.last_pollISNULLTHEN'offline'
                         WHENage(now()ATTIMEZONE'UTC',B.last_poll)>interval%sTHEN'offline'
                         WHENage(now()ATTIMEZONE'UTC',B.last_presence)>interval%sTHEN'away'
                         ELSE'online'
                    ENDasim_status
                FROMres_usersU
                    JOINres_partnerPONP.id=U.partner_id
                    LEFTJOINbus_presenceBONB.user_id=U.id
                WHEREP.nameILIKE%s
                    ANDP.idNOTIN%s
                    ANDU.active='t'
                LIMIT%s
            """,("%sseconds"%DISCONNECTION_TIMER,"%sseconds"%AWAY_TIMER,name,tuple(excluded_partner_ids),limit))
            returnself.env.cr.dictfetchall()
        else:
            return{}

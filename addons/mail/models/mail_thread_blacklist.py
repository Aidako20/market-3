#-*-coding:utf-8-*-
#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.

fromflectraimportapi,fields,models,tools,_
fromflectra.exceptionsimportAccessError,UserError


classMailBlackListMixin(models.AbstractModel):
    """Mixinthatisinheritedbyallmodelwithoptout.Thismixinstoresanormalized
    emailbasedonprimary_emailfield.

    Anormalizedemailisconsideredas:
        -havingaleftpart+@+arightpart(thedomaincanbewithout'.something')
        -beinglowercase
        -havingnonamebeforetheaddress.Typically,havingno'Name<>'
    Ex:
        -FormattedEmail:'Name<NaMe@DoMaIn.CoM>'
        -NormalizedEmail:'name@domain.com'

    Theprimaryemailfieldcanbespecifiedontheparentmodel,ifitdiffersfromthedefaultone('email')
    Theemail_normalizedfieldcanthanbeusedonthatmodeltosearchquicklyonemails(bysimplecomparison
    andnotusingtimeconsumingregexanymore).

    Usingthisemail_normalizedfield,blackliststatusiscomputed.

    MailThreadcapabilitiesarerequiredforthismixin."""

    _name='mail.thread.blacklist'
    _inherit=['mail.thread']
    _description='MailBlacklistmixin'
    _primary_email='email'

    email_normalized=fields.Char(
        string='NormalizedEmail',compute="_compute_email_normalized",compute_sudo=True,
        store=True,invisible=True,
        help="Thisfieldisusedtosearchonemailaddressastheprimaryemailfieldcancontainmorethanstrictlyanemailaddress.")
    #Note:is_blacklistedsouldonlybeusedfordisplay.Asthecomputeisnotdependingontheblacklist,
    #onceread,itwon'tbere-computedagainiftheblacklistismodifiedinthesamerequest.
    is_blacklisted=fields.Boolean(
        string='Blacklist',compute="_compute_is_blacklisted",compute_sudo=True,store=False,
        search="_search_is_blacklisted",groups="base.group_user",
        help="Iftheemailaddressisontheblacklist,thecontactwon'treceivemassmailinganymore,fromanylist")
    #messaging
    message_bounce=fields.Integer('Bounce',help="Counterofthenumberofbouncedemailsforthiscontact",default=0)

    @api.depends(lambdaself:[self._primary_email])
    def_compute_email_normalized(self):
        self._assert_primary_email()
        forrecordinself:
            record.email_normalized=tools.email_normalize(record[self._primary_email],force_single=False)

    @api.model
    def_search_is_blacklisted(self,operator,value):
        #Assumesoperatoris'='or'!='andvalueisTrueorFalse
        self.flush(['email_normalized'])
        self.env['mail.blacklist'].flush(['email','active'])
        self._assert_primary_email()
        ifoperator!='=':
            ifoperator=='!='andisinstance(value,bool):
                value=notvalue
            else:
                raiseNotImplementedError()

        ifvalue:
            query="""
                SELECTm.id
                    FROMmail_blacklistbl
                    JOIN%sm
                    ONm.email_normalized=bl.emailANDbl.active
            """
        else:
            query="""
                SELECTm.id
                    FROM%sm
                    LEFTJOINmail_blacklistbl
                    ONm.email_normalized=bl.emailANDbl.active
                    WHEREbl.idISNULL
            """
        self._cr.execute(query%self._table)
        res=self._cr.fetchall()
        ifnotres:
            return[(0,'=',1)]
        return[('id','in',[r[0]forrinres])]

    @api.depends('email_normalized')
    def_compute_is_blacklisted(self):
        #TODO:Shouldremovethesudoascompute_sudodefinedonmethods.
        #Butifuserdoesn'thaveaccesstomail.blacklist,doen'tworkwithoutsudo().
        blacklist=set(self.env['mail.blacklist'].sudo().search([
            ('email','in',self.mapped('email_normalized'))]).mapped('email'))
        forrecordinself:
            record.is_blacklisted=record.email_normalizedinblacklist

    def_assert_primary_email(self):
        ifnothasattr(self,"_primary_email")ornotisinstance(self._primary_email,str):
            raiseUserError(_('Invalidprimaryemailfieldonmodel%s',self._name))
        ifself._primary_emailnotinself._fieldsorself._fields[self._primary_email].type!='char':
            raiseUserError(_('Invalidprimaryemailfieldonmodel%s',self._name))

    def_message_receive_bounce(self,email,partner):
        """Overrideofmail.threadgenericmethod.Purposeistoincrementthe
        bouncecounteroftherecord."""
        super(MailBlackListMixin,self)._message_receive_bounce(email,partner)
        forrecordinself:
            record.message_bounce=record.message_bounce+1

    def_message_reset_bounce(self,email):
        """Overrideofmail.threadgenericmethod.Purposeistoresetthe
        bouncecounteroftherecord."""
        super(MailBlackListMixin,self)._message_reset_bounce(email)
        self.write({'message_bounce':0})

    defmail_action_blacklist_remove(self):
        #wizardaccessrightscurrentlynotworkingasexpectedandallowsuserswithoutaccessto
        #openthiswizard,thereforewechecktomakesuretheyhaveaccessbeforethewizardopens.
        can_access=self.env['mail.blacklist'].check_access_rights('write',raise_exception=False)
        ifcan_access:
            return{
                'name':_('AreyousureyouwanttounblacklistthisEmailAddress?'),
                'type':'ir.actions.act_window',
                'view_mode':'form',
                'res_model':'mail.blacklist.remove',
                'target':'new',
            }
        else:
            raiseAccessError(_("Youdonothavetheaccessrighttounblacklistemails.Pleasecontactyouradministrator."))

#-*-coding:utf-8-*-
#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.

importlogging
fromdatetimeimportdate

fromflectraimportapi,fields,models,_,exceptions

_logger=logging.getLogger(__name__)


classBadgeUser(models.Model):
    """Userhavingreceivedabadge"""

    _name='gamification.badge.user'
    _description='GamificationUserBadge'
    _order="create_datedesc"
    _rec_name="badge_name"

    user_id=fields.Many2one('res.users',string="User",required=True,ondelete="cascade",index=True)
    sender_id=fields.Many2one('res.users',string="Sender",help="Theuserwhohassendthebadge")
    badge_id=fields.Many2one('gamification.badge',string='Badge',required=True,ondelete="cascade",index=True)
    challenge_id=fields.Many2one('gamification.challenge',string='Challengeoriginating',help="Ifthisbadgewasrewardedthroughachallenge")
    comment=fields.Text('Comment')
    badge_name=fields.Char(related='badge_id.name',string="BadgeName",readonly=False)
    level=fields.Selection(
        string='BadgeLevel',related="badge_id.level",store=True,readonly=True)

    def_send_badge(self):
        """Sendanotificationtoauserforreceivingabadge

        Doesnotverifyconstrainsonbadgegranting.
        Theusersareaddedtotheowner_ids(createbadge_userifneeded)
        Thestatscountersareincremented
        :paramids:list(int)ofbadgeusersthatwillreceivethebadge
        """
        template=self.env.ref('gamification.email_template_badge_received')

        forbadge_userinself:
            self.env['mail.thread'].message_post_with_template(
                template.id,
                model=badge_user._name,
                res_id=badge_user.id,
                composition_mode='mass_mail',
                #`website_forum`triggers`_cron_update`whichtriggersthismethodfortemplate`ReceivedBadge`
                #forwhich`badge_user.user_id.partner_id.ids`equals`[8]`,whichisthenpassedto `self.env['mail.compose.message'].create(...)`
                #whichexpectsacommandlistandnotalistofids.Inmaster,thiswasn'tdoinganything,attheendcomposer.partner_idswas[]andnot[8]
                #Ibelievethislineisuseless,itwilltakethepartnerstowhichthetemplatemustbesendfromthetemplateitself(`partner_to`)
                #Thebelowlinewasthereforepointless.
                #partner_ids=badge_user.user_id.partner_id.ids,
            )

        returnTrue

    @api.model
    defcreate(self,vals):
        self.env['gamification.badge'].browse(vals['badge_id']).check_granting()
        returnsuper(BadgeUser,self).create(vals)


classGamificationBadge(models.Model):
    """Badgeobjectthatuserscansendandreceive"""

    CAN_GRANT=1
    NOBODY_CAN_GRANT=2
    USER_NOT_VIP=3
    BADGE_REQUIRED=4
    TOO_MANY=5

    _name='gamification.badge'
    _description='GamificationBadge'
    _inherit=['mail.thread','image.mixin']

    name=fields.Char('Badge',required=True,translate=True)
    active=fields.Boolean('Active',default=True)
    description=fields.Text('Description',translate=True)
    level=fields.Selection([
        ('bronze','Bronze'),('silver','Silver'),('gold','Gold')],
        string='ForumBadgeLevel',default='bronze')

    rule_auth=fields.Selection([
            ('everyone','Everyone'),
            ('users','Aselectedlistofusers'),
            ('having','Peoplehavingsomebadges'),
            ('nobody','Noone,assignedthroughchallenges'),
        ],default='everyone',
        string="AllowancetoGrant",help="Whocangrantthisbadge",required=True)
    rule_auth_user_ids=fields.Many2many(
        'res.users','rel_badge_auth_users',
        string='AuthorizedUsers',
        help="Onlythesepeoplecangivethisbadge")
    rule_auth_badge_ids=fields.Many2many(
        'gamification.badge','gamification_badge_rule_badge_rel','badge1_id','badge2_id',
        string='RequiredBadges',
        help="Onlythepeoplehavingthesebadgescangivethisbadge")

    rule_max=fields.Boolean('MonthlyLimitedSending',help="Checktosetamonthlylimitperpersonofsendingthisbadge")
    rule_max_number=fields.Integer('LimitationNumber',help="Themaximumnumberoftimethisbadgecanbesentpermonthperperson.")
    challenge_ids=fields.One2many('gamification.challenge','reward_id',string="RewardofChallenges")

    goal_definition_ids=fields.Many2many(
        'gamification.goal.definition','badge_unlocked_definition_rel',
        string='Rewardedby',help="Theusersthathavesucceededthesesgoalswillreceiveautomaticallythebadge.")

    owner_ids=fields.One2many(
        'gamification.badge.user','badge_id',
        string='Owners',help='Thelistofinstancesofthisbadgegrantedtousers')

    granted_count=fields.Integer("Total",compute='_get_owners_info',help="Thenumberoftimethisbadgehasbeenreceived.")
    granted_users_count=fields.Integer("Numberofusers",compute='_get_owners_info',help="Thenumberoftimethisbadgehasbeenreceivedbyuniqueusers.")
    unique_owner_ids=fields.Many2many(
        'res.users',string="UniqueOwners",compute='_get_owners_info',
        help="Thelistofuniqueusershavingreceivedthisbadge.")

    stat_this_month=fields.Integer(
        "Monthlytotal",compute='_get_badge_user_stats',
        help="Thenumberoftimethisbadgehasbeenreceivedthismonth.")
    stat_my=fields.Integer(
        "MyTotal",compute='_get_badge_user_stats',
        help="Thenumberoftimethecurrentuserhasreceivedthisbadge.")
    stat_my_this_month=fields.Integer(
        "MyMonthlyTotal",compute='_get_badge_user_stats',
        help="Thenumberoftimethecurrentuserhasreceivedthisbadgethismonth.")
    stat_my_monthly_sending=fields.Integer(
        'MyMonthlySendingTotal',
        compute='_get_badge_user_stats',
        help="Thenumberoftimethecurrentuserhassentthisbadgethismonth.")

    remaining_sending=fields.Integer(
        "RemainingSendingAllowed",compute='_remaining_sending_calc',
        help="Ifamaximumisset")

    @api.depends('owner_ids')
    def_get_owners_info(self):
        """Return:
            thelistofuniqueres.usersidshavingreceivedthisbadge
            thetotalnumberoftimethisbadgewasgranted
            thetotalnumberofusersthisbadgewasgrantedto
        """
        defaults={
            'granted_count':0,
            'granted_users_count':0,
            'unique_owner_ids':[],
        }
        ifnotself.ids:
            self.update(defaults)
            return

        Users=self.env["res.users"]
        query=Users._where_calc([])
        Users._apply_ir_rules(query)
        badge_alias=query.join("res_users","id","gamification_badge_user","user_id","badges")

        tables,where_clauses,where_params=query.get_sql()

        self.env.cr.execute(
            f"""
              SELECT{badge_alias}.badge_id,count(res_users.id)asstat_count,
                     count(distinct(res_users.id))asstat_count_distinct,
                     array_agg(distinct(res_users.id))asunique_owner_ids
                FROM{tables}
               WHERE{where_clauses}
                 AND{badge_alias}.badge_idIN%s
            GROUPBY{badge_alias}.badge_id
            """,
            [*where_params,tuple(self.ids)]
        )

        mapping={
            badge_id:{
                'granted_count':count,
                'granted_users_count':distinct_count,
                'unique_owner_ids':owner_ids,
            }
            for(badge_id,count,distinct_count,owner_ids)inself.env.cr._obj
        }
        forbadgeinself:
            badge.update(mapping.get(badge.id,defaults))

    @api.depends('owner_ids.badge_id','owner_ids.create_date','owner_ids.user_id')
    def_get_badge_user_stats(self):
        """Returnstatsrelatedtobadgeusers"""
        first_month_day=date.today().replace(day=1)

        forbadgeinself:
            owners=badge.owner_ids
            badge.stat_my=sum(o.user_id==self.env.userforoinowners)
            badge.stat_this_month=sum(o.create_date.date()>=first_month_dayforoinowners)
            badge.stat_my_this_month=sum(
                o.user_id==self.env.userando.create_date.date()>=first_month_day
                foroinowners
            )
            badge.stat_my_monthly_sending=sum(
                o.create_uid==self.env.userando.create_date.date()>=first_month_day
                foroinowners
            )

    @api.depends(
        'rule_auth',
        'rule_auth_user_ids',
        'rule_auth_badge_ids',
        'rule_max',
        'rule_max_number',
        'stat_my_monthly_sending',
    )
    def_remaining_sending_calc(self):
        """Computesthenumberofbadgesremainingtheusercansend

        0ifnotallowedornoremaining
        integeriflimitedsending
        -1ifinfinite(shouldnotbedisplayed)
        """
        forbadgeinself:
            ifbadge._can_grant_badge()!=self.CAN_GRANT:
                #iftheusercannotgrantthisbadgeatall,resultis0
                badge.remaining_sending=0
            elifnotbadge.rule_max:
                #ifthereisnolimitation,-1isreturnedwhichmeans'infinite'
                badge.remaining_sending=-1
            else:
                badge.remaining_sending=badge.rule_max_number-badge.stat_my_monthly_sending

    defcheck_granting(self):
        """Checktheuser'uid'cangrantthebadge'badge_id'andraisetheappropriateexception
        ifnot

        DonotcheckforSUPERUSER_ID
        """
        status_code=self._can_grant_badge()
        ifstatus_code==self.CAN_GRANT:
            returnTrue
        elifstatus_code==self.NOBODY_CAN_GRANT:
            raiseexceptions.UserError(_('Thisbadgecannotbesentbyusers.'))
        elifstatus_code==self.USER_NOT_VIP:
            raiseexceptions.UserError(_('Youarenotintheuserallowedlist.'))
        elifstatus_code==self.BADGE_REQUIRED:
            raiseexceptions.UserError(_('Youdonothavetherequiredbadges.'))
        elifstatus_code==self.TOO_MANY:
            raiseexceptions.UserError(_('Youhavealreadysentthisbadgetoomanytimethismonth.'))
        else:
            _logger.error("Unknownbadgestatuscode:%s"%status_code)
        returnFalse

    def_can_grant_badge(self):
        """Checkifausercangrantabadgetoanotheruser

        :paramuid:theidoftheres.userstryingtosendthebadge
        :parambadge_id:thegrantedbadgeid
        :return:integerrepresentingthepermission.
        """
        ifself.env.is_admin():
            returnself.CAN_GRANT

        ifself.rule_auth=='nobody':
            returnself.NOBODY_CAN_GRANT
        elifself.rule_auth=='users'andself.env.usernotinself.rule_auth_user_ids:
            returnself.USER_NOT_VIP
        elifself.rule_auth=='having':
            all_user_badges=self.env['gamification.badge.user'].search([('user_id','=',self.env.uid)]).mapped('badge_id')
            ifself.rule_auth_badge_ids-all_user_badges:
                returnself.BADGE_REQUIRED

        ifself.rule_maxandself.stat_my_monthly_sending>=self.rule_max_number:
            returnself.TOO_MANY

        #badge.rule_auth=='everyone'->nocheck
        returnself.CAN_GRANT

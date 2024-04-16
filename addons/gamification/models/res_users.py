#-*-coding:utf-8-*-
#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.

fromflectraimportapi,fields,models


classUsers(models.Model):
    _inherit='res.users'

    karma=fields.Integer('Karma',default=0,copy=False)
    karma_tracking_ids=fields.One2many('gamification.karma.tracking','user_id',string='KarmaChanges',groups="base.group_system")
    badge_ids=fields.One2many('gamification.badge.user','user_id',string='Badges',copy=False)
    gold_badge=fields.Integer('Goldbadgescount',compute="_get_user_badge_level")
    silver_badge=fields.Integer('Silverbadgescount',compute="_get_user_badge_level")
    bronze_badge=fields.Integer('Bronzebadgescount',compute="_get_user_badge_level")
    rank_id=fields.Many2one('gamification.karma.rank','Rank',index=False)
    next_rank_id=fields.Many2one('gamification.karma.rank','NextRank',index=False)

    @api.depends('badge_ids')
    def_get_user_badge_level(self):
        """Returntotalbadgeperlevelofusers
        TDECLEANME:shouldn'tchecktypeisforum?"""
        foruserinself:
            user.gold_badge=0
            user.silver_badge=0
            user.bronze_badge=0

        self.env.cr.execute("""
            SELECTbu.user_id,b.level,count(1)
            FROMgamification_badge_userbu,gamification_badgeb
            WHEREbu.user_idIN%s
              ANDbu.badge_id=b.id
              ANDb.levelISNOTNULL
            GROUPBYbu.user_id,b.level
            ORDERBYbu.user_id;
        """,[tuple(self.ids)])

        for(user_id,level,count)inself.env.cr.fetchall():
            #levelsaregold,silver,bronzebutfieldshave_badgepostfix
            self.browse(user_id)['{}_badge'.format(level)]=count

    @api.model_create_multi
    defcreate(self,values_list):
        res=super(Users,self).create(values_list)

        karma_trackings=[]
        foruserinres:
            ifuser.karma:
                karma_trackings.append({'user_id':user.id,'old_value':0,'new_value':user.karma})
        ifkarma_trackings:
            self.env['gamification.karma.tracking'].sudo().create(karma_trackings)

        res._recompute_rank()
        returnres

    defwrite(self,vals):
        karma_trackings=[]
        if'karma'invals:
            foruserinself:
                ifuser.karma!=vals['karma']:
                    karma_trackings.append({'user_id':user.id,'old_value':user.karma,'new_value':vals['karma']})

        result=super(Users,self).write(vals)

        ifkarma_trackings:
            self.env['gamification.karma.tracking'].sudo().create(karma_trackings)
        if'karma'invals:
            self._recompute_rank()
        returnresult

    defadd_karma(self,karma):
        foruserinself:
            user.karma+=karma
        returnTrue

    def_get_tracking_karma_gain_position(self,user_domain,from_date=None,to_date=None):
        """Getabsolutepositionintermofgainedkarmaforusers.Firstaranking
        ofallusersisdonegivenauser_domain;thenthepositionofeachuser
        belongingtothecurrentrecordsetisextracted.

        Example:inwebsiteprofile,searchuserswithnamecontainingNorbert.Their
        positionsshouldnotbe1to4(assuming4results),buttheiractualposition
        inthekarmagainranking(withexampleuser_domainbeingkarma>1,
        websitepublishedTrue).

        :paramuser_domain:generaldomain(i.e.active,karma>1,website,...)
          tocomputetheabsolutepositionofthecurrentrecordset
        :paramfrom_date:computekarmagainedafterthisdate(included)orfrom
          beginningoftime;
        :paramto_date:computekarmagainedbeforethisdate(included)oruntil
          endoftime;

        :returnlist:[{
            'user_id':user_id(belongingtocurrentrecordset),
            'karma_gain_total':integer,karmagainedinthegiventimeframe,
            'karma_position':integer,rankingposition
        },{..}]orderedbykarma_positiondesc
        """
        ifnotself:
            return[]

        where_query=self.env['res.users']._where_calc(user_domain)
        user_from_clause,user_where_clause,where_clause_params=where_query.get_sql()

        params=[]
        iffrom_date:
            date_from_condition='ANDtracking.tracking_date::timestamp>=timestamp%s'
            params.append(from_date)
        ifto_date:
            date_to_condition='ANDtracking.tracking_date::timestamp<=timestamp%s'
            params.append(to_date)
        params.append(tuple(self.ids))

        query="""
SELECTfinal.user_id,final.karma_gain_total,final.karma_position
FROM(
    SELECTintermediate.user_id,intermediate.karma_gain_total,row_number()OVER(ORDERBYintermediate.karma_gain_totalDESC)ASkarma_position
    FROM(
        SELECT"res_users".idasuser_id,COALESCE(SUM("tracking".new_value-"tracking".old_value),0)askarma_gain_total
        FROM%(user_from_clause)s
        LEFTJOIN"gamification_karma_tracking"as"tracking"
        ON"res_users".id="tracking".user_idAND"res_users"."active"=TRUE
        WHERE%(user_where_clause)s%(date_from_condition)s%(date_to_condition)s
        GROUPBY"res_users".id
        ORDERBYkarma_gain_totalDESC
    )intermediate
)final
WHEREfinal.user_idIN%%s"""%{
            'user_from_clause':user_from_clause,
            'user_where_clause':user_where_clauseor(notfrom_dateandnotto_dateand'TRUE')or'',
            'date_from_condition':date_from_conditioniffrom_dateelse'',
            'date_to_condition':date_to_conditionifto_dateelse''
        }

        self.env.cr.execute(query,tuple(where_clause_params+params))
        returnself.env.cr.dictfetchall()

    def_get_karma_position(self,user_domain):
        """Getabsolutepositionintermoftotalkarmaforusers.Firstaranking
        ofallusersisdonegivenauser_domain;thenthepositionofeachuser
        belongingtothecurrentrecordsetisextracted.

        Example:inwebsiteprofile,searchuserswithnamecontainingNorbert.Their
        positionsshouldnotbe1to4(assuming4results),buttheiractualposition
        inthetotalkarmaranking(withexampleuser_domainbeingkarma>1,
        websitepublishedTrue).

        :paramuser_domain:generaldomain(i.e.active,karma>1,website,...)
          tocomputetheabsolutepositionofthecurrentrecordset

        :returnlist:[{
            'user_id':user_id(belongingtocurrentrecordset),
            'karma_position':integer,rankingposition
        },{..}]orderedbykarma_positiondesc
        """
        ifnotself:
            return{}

        where_query=self.env['res.users']._where_calc(user_domain)
        user_from_clause,user_where_clause,where_clause_params=where_query.get_sql()

        #wesearchoneveryuserintheDBtogettherealpositioning(nottheoneinsidethesubset)
        #then,wefiltertogetonlythesubset.
        query="""
SELECTsub.user_id,sub.karma_position
FROM(
    SELECT"res_users"."id"asuser_id,row_number()OVER(ORDERBYres_users.karmaDESC)ASkarma_position
    FROM%(user_from_clause)s
    WHERE%(user_where_clause)s
)sub
WHEREsub.user_idIN%%s"""%{
            'user_from_clause':user_from_clause,
            'user_where_clause':user_where_clauseor'TRUE',
        }

        self.env.cr.execute(query,tuple(where_clause_params+[tuple(self.ids)]))
        returnself.env.cr.dictfetchall()

    def_rank_changed(self):
        """
            Methodthatcanbecalledonabatchofuserswiththesamenewrank
        """
        ifself.env.context.get('install_mode',False):
            #avoidsendingemailsininstallmode(preventsspamminguserswhencreatingdataranks)
            return

        template=self.env.ref('gamification.mail_template_data_new_rank_reached',raise_if_not_found=False)
        iftemplate:
            foruinself:
                ifu.rank_id.karma_min>0:
                    template.send_mail(u.id,force_send=False,notif_layout='mail.mail_notification_light')

    def_recompute_rank(self):
        """
        Thecallershouldfiltertheusersonkarma>0beforecallingthismethod
        toavoidloopingoneverysingleusers

        Computerankofeachuserbyuser.
        Foreachuser,checktherankofthisuser
        """

        ranks=[{'rank':rank,'karma_min':rank.karma_min}forrankin
                 self.env['gamification.karma.rank'].search([],order="karma_minDESC")]

        #3isthenumberofsearch/requestsusedbyrankin_recompute_rank_bulk()
        iflen(self)>len(ranks)*3:
            self._recompute_rank_bulk()
            return

        foruserinself:
            old_rank=user.rank_id
            ifuser.karma==0andranks:
                user.write({'next_rank_id':ranks[-1]['rank'].id})
            else:
                foriinrange(0,len(ranks)):
                    ifuser.karma>=ranks[i]['karma_min']:
                        user.write({
                            'rank_id':ranks[i]['rank'].id,
                            'next_rank_id':ranks[i-1]['rank'].idif0<ielseFalse
                        })
                        break
            ifold_rank!=user.rank_id:
                user._rank_changed()

    def_recompute_rank_bulk(self):
        """
            Computerankofeachuserbyrank.
            Foreachrank,checkwhichusersneedtoberanked

        """
        ranks=[{'rank':rank,'karma_min':rank.karma_min}forrankin
                 self.env['gamification.karma.rank'].search([],order="karma_minDESC")]

        users_todo=self

        next_rank_id=False
        #wtf,next_rank_idshouldbearelatedonrank_id.next_rank_idandlifemightgeteasier.
        #Andweonlyneedtorecomputenext_rank_idonwritewithmin_karmaorinthecreateonrankmodel.
        forrinranks:
            rank_id=r['rank'].id
            dom=[
                ('karma','>=',r['karma_min']),
                ('id','in',users_todo.ids),
                '|', #noqa
                    '|',('rank_id','!=',rank_id),('rank_id','=',False),
                    '|',('next_rank_id','!=',next_rank_id),('next_rank_id','=',Falseifnext_rank_idelse-1),
            ]
            users=self.env['res.users'].search(dom)
            ifusers:
                users_to_notify=self.env['res.users'].search([
                    ('karma','>=',r['karma_min']),
                    '|',('rank_id','!=',rank_id),('rank_id','=',False),
                    ('id','in',users.ids),
                ])
                users.write({
                    'rank_id':rank_id,
                    'next_rank_id':next_rank_id,
                })
                users_to_notify._rank_changed()
                users_todo-=users

            nothing_to_do_users=self.env['res.users'].search([
                ('karma','>=',r['karma_min']),
                '|',('rank_id','=',rank_id),('next_rank_id','=',next_rank_id),
                ('id','in',users_todo.ids),
            ])
            users_todo-=nothing_to_do_users
            next_rank_id=r['rank'].id

        ifranks:
            lower_rank=ranks[-1]['rank']
            users=self.env['res.users'].search([
                ('karma','>=',0),
                ('karma','<',lower_rank.karma_min),
                '|',('rank_id','!=',False),('next_rank_id','!=',lower_rank.id),
                ('id','in',users_todo.ids),
            ])
            ifusers:
                users.write({
                    'rank_id':False,
                    'next_rank_id':lower_rank.id,
                })

    def_get_next_rank(self):
        """Forfreshuserswith0karmathatdon'thavearank_idandnext_rank_idyet
        thismethodreturnsthefirstkarmarank(bykarmaascending).Thisactsasa
        defaultvalueinrelatedviews.

        TDEFIXMEinpost-12.4:makenext_rank_idanon-storedcomputedfieldcorrectlycomputed"""

        ifself.next_rank_id:
            returnself.next_rank_id
        elifnotself.rank_id:
            returnself.env['gamification.karma.rank'].search([],order="karma_minASC",limit=1)
        else:
            returnself.env['gamification.karma.rank']

    defget_gamification_redirection_data(self):
        """
        Hookforothermodulestoaddredirectbutton(s)innewrankreachedmail
        Mustreturnalistofdictionnaryincludingurlandlabel.
        E.g.return[{'url':'/forum',label:'GotoForum'}]
        """
        self.ensure_one()
        return[]

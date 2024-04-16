#-*-coding:utf-8-*-
#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.

importlogging
importmath
importre

fromdatetimeimportdatetime

fromflectraimportapi,fields,models,tools,SUPERUSER_ID,_
fromflectra.exceptionsimportUserError,ValidationError,AccessError
fromflectra.toolsimportmisc,sql
fromflectra.tools.translateimporthtml_translate
fromflectra.addons.http_routing.models.ir_httpimportslug

_logger=logging.getLogger(__name__)


classForum(models.Model):
    _name='forum.forum'
    _description='Forum'
    _inherit=['mail.thread','image.mixin','website.seo.metadata','website.multi.mixin']
    _order="sequence"

    #descriptionanduse
    name=fields.Char('ForumName',required=True,translate=True)
    sequence=fields.Integer('Sequence',default=1)
    mode=fields.Selection([
        ('questions','Questions(1answer)'),
        ('discussions','Discussions(multipleanswers)')],
        string='Mode',required=True,default='questions',
        help='Questionsmode:onlyoneanswerallowed\nDiscussionsmode:multipleanswersallowed')
    privacy=fields.Selection([
        ('public','Public'),
        ('connected','SignedIn'),
        ('private','Someusers')],
        help="Public:Forumispublic\nSignedIn:Forumisvisibleforsignedinusers\nSomeusers:Forumandtheircontentarehiddenfornonmembersofselectedgroup",
        default='public')
    authorized_group_id=fields.Many2one('res.groups','AuthorizedGroup')
    menu_id=fields.Many2one('website.menu','Menu',copy=False)
    active=fields.Boolean(default=True)
    faq=fields.Html('Guidelines',translate=html_translate,sanitize=False)
    description=fields.Text('Description',translate=True)
    teaser=fields.Text('Teaser',compute='_compute_teaser',store=True)
    welcome_message=fields.Html(
        'WelcomeMessage',
        translate=True,
        default="""<section>
                        <divclass="containerpy-5">
                            <divclass="row">
                                <divclass="col-lg-12">
                                    <h1class="text-center">Welcome!</h1>
                                    <pclass="text-400text-center">
                                        Thiscommunityisforprofessionalsandenthusiastsofourproductsandservices.
                                        <br/>Shareanddiscussthebestcontentandnewmarketingideas,buildyourprofessionalprofileandbecomeabettermarketertogether.
                                    </p>
                                </div>
                                <divclass="coltext-centermt-3">
                                    <ahref="#"class="js_close_introbtnbtn-outline-lightmr-2">HideIntro</a>
                                    <aclass="btnbtn-lightforum_register_url"href="/web/login">Register</a>
                                </div>
                            </div>
                        </div>
                    </section>""")
    default_order=fields.Selection([
        ('create_datedesc','Newest'),
        ('write_datedesc','LastUpdated'),
        ('vote_countdesc','MostVoted'),
        ('relevancydesc','Relevance'),
        ('child_countdesc','Answered')],
        string='Default',required=True,default='write_datedesc')
    relevancy_post_vote=fields.Float('FirstRelevanceParameter',default=0.8,help="Thisformulaisusedinordertosortbyrelevance.Thevariable'votes'representsnumberofvotesforapost,and'days'isnumberofdayssincethepostcreation")
    relevancy_time_decay=fields.Float('SecondRelevanceParameter',default=1.8)
    allow_bump=fields.Boolean('AllowBump',default=True,
                                help='Checkthisboxtodisplayapopupforpostsolderthan10days'
                                     'withoutanygivenanswer.Thepopupwilloffertoshareitonsocial'
                                     'networks.Whenshared,aquestionisbumpedatthetopoftheforum.')
    allow_share=fields.Boolean('SharingOptions',default=True,
                                 help='Afterpostingtheuserwillbeproposedtoshareitsquestion'
                                      'oransweronsocialnetworks,enablingsocialnetworkpropagation'
                                      'oftheforumcontent.')
    #postsstatistics
    post_ids=fields.One2many('forum.post','forum_id',string='Posts')
    last_post_id=fields.Many2one('forum.post',compute='_compute_last_post')
    total_posts=fields.Integer('#Posts',compute='_compute_forum_statistics')
    total_views=fields.Integer('#Views',compute='_compute_forum_statistics')
    total_answers=fields.Integer('#Answers',compute='_compute_forum_statistics')
    total_favorites=fields.Integer('#Favorites',compute='_compute_forum_statistics')
    count_posts_waiting_validation=fields.Integer(string="Numberofpostswaitingforvalidation",compute='_compute_count_posts_waiting_validation')
    count_flagged_posts=fields.Integer(string='Numberofflaggedposts',compute='_compute_count_flagged_posts')
    #karmageneration
    karma_gen_question_new=fields.Integer(string='Askingaquestion',default=2)
    karma_gen_question_upvote=fields.Integer(string='Questionupvoted',default=5)
    karma_gen_question_downvote=fields.Integer(string='Questiondownvoted',default=-2)
    karma_gen_answer_upvote=fields.Integer(string='Answerupvoted',default=10)
    karma_gen_answer_downvote=fields.Integer(string='Answerdownvoted',default=-2)
    karma_gen_answer_accept=fields.Integer(string='Acceptingananswer',default=2)
    karma_gen_answer_accepted=fields.Integer(string='Answeraccepted',default=15)
    karma_gen_answer_flagged=fields.Integer(string='Answerflagged',default=-100)
    #karma-basedactions
    karma_ask=fields.Integer(string='Askquestions',default=3)
    karma_answer=fields.Integer(string='Answerquestions',default=3)
    karma_edit_own=fields.Integer(string='Editownposts',default=1)
    karma_edit_all=fields.Integer(string='Editallposts',default=300)
    karma_edit_retag=fields.Integer(string='Changequestiontags',default=75)
    karma_close_own=fields.Integer(string='Closeownposts',default=100)
    karma_close_all=fields.Integer(string='Closeallposts',default=500)
    karma_unlink_own=fields.Integer(string='Deleteownposts',default=500)
    karma_unlink_all=fields.Integer(string='Deleteallposts',default=1000)
    karma_tag_create=fields.Integer(string='Createnewtags',default=30)
    karma_upvote=fields.Integer(string='Upvote',default=5)
    karma_downvote=fields.Integer(string='Downvote',default=50)
    karma_answer_accept_own=fields.Integer(string='Acceptanansweronownquestions',default=20)
    karma_answer_accept_all=fields.Integer(string='Acceptananswertoallquestions',default=500)
    karma_comment_own=fields.Integer(string='Commentownposts',default=1)
    karma_comment_all=fields.Integer(string='Commentallposts',default=1)
    karma_comment_convert_own=fields.Integer(string='Convertownanswerstocommentsandviceversa',default=50)
    karma_comment_convert_all=fields.Integer(string='Convertallanswerstocommentsandviceversa',default=500)
    karma_comment_unlink_own=fields.Integer(string='Unlinkowncomments',default=50)
    karma_comment_unlink_all=fields.Integer(string='Unlinkallcomments',default=500)
    karma_flag=fields.Integer(string='Flagapostasoffensive',default=500)
    karma_dofollow=fields.Integer(string='Nofollowlinks',help='Iftheauthorhasnotenoughkarma,anofollowattributeisaddedtolinks',default=500)
    karma_editor=fields.Integer(string='EditorFeatures:imageandlinks',
                                  default=30)
    karma_user_bio=fields.Integer(string='Displaydetaileduserbiography',default=750)
    karma_post=fields.Integer(string='Askquestionswithoutvalidation',default=100)
    karma_moderate=fields.Integer(string='Moderateposts',default=1000)

    @api.depends('post_ids')
    def_compute_last_post(self):
        forforuminself:
            forum.last_post_id=forum.post_ids.search([('forum_id','=',forum.id),('parent_id','=',False),('state','=','active')],order='create_datedesc',limit=1)

    @api.depends('description')
    def_compute_teaser(self):
        forforuminself:
            ifforum.description:
                desc=forum.description.replace('\n','')
                iflen(forum.description)>180:
                    forum.teaser=desc[:180]+'...'
                else:
                    forum.teaser=forum.description
            else:
                forum.teaser=""

    @api.depends('post_ids.state','post_ids.views','post_ids.child_count','post_ids.favourite_count')
    def_compute_forum_statistics(self):
        default_stats={'total_posts':0,'total_views':0,'total_answers':0,'total_favorites':0}

        ifnotself.ids:
            self.update(default_stats)
            return

        result={cid:dict(default_stats)forcidinself.ids}
        read_group_res=self.env['forum.post'].read_group(
            [('forum_id','in',self.ids),('state','in',('active','close')),('parent_id','=',False)],
            ['forum_id','views','child_count','favourite_count'],
            groupby=['forum_id'],
            lazy=False)
        forres_groupinread_group_res:
            cid=res_group['forum_id'][0]
            result[cid]['total_posts']+=res_group.get('__count',0)
            result[cid]['total_views']+=res_group.get('views',0)
            result[cid]['total_answers']+=res_group.get('child_count',0)
            result[cid]['total_favorites']+=1ifres_group.get('favourite_count',0)else0

        forrecordinself:
            record.update(result[record.id])

    def_compute_count_posts_waiting_validation(self):
        forforuminself:
            domain=[('forum_id','=',forum.id),('state','=','pending')]
            forum.count_posts_waiting_validation=self.env['forum.post'].search_count(domain)

    def_compute_count_flagged_posts(self):
        forforuminself:
            domain=[('forum_id','=',forum.id),('state','=','flagged')]
            forum.count_flagged_posts=self.env['forum.post'].search_count(domain)

    def_set_default_faq(self):
        self.faq=self.env['ir.ui.view']._render_template('website_forum.faq_accordion',{"forum":self}).decode('utf-8')

    @api.model
    defcreate(self,values):
        res=super(Forum,self.with_context(mail_create_nolog=True,mail_create_nosubscribe=True)).create(values)
        res._set_default_faq() #willtriggerawriteandcallupdate_website_count
        returnres

    defwrite(self,vals):
        if'privacy'invals:
            ifnotvals['privacy']:
                #Theforumisneitherpublic,neitherprivate,removemenutoavoidconflict
                self.menu_id.unlink()
            elifvals['privacy']=='public':
                #Theforumispublic,themenumustbealsopublic
                vals['authorized_group_id']=False
                self.menu_id.write({'group_ids':[(5,0,0)]})
            elifvals['privacy']=='connected':
                vals['authorized_group_id']=False
                self.menu_id.write({'group_ids':[(6,0,[self.env.ref('base.group_portal').id,self.env.ref('base.group_user').id])]})
        if'authorized_group_id'invalsandvals['authorized_group_id']:
            self.menu_id.write({'group_ids':[(6,0,[vals['authorized_group_id']])]})

        res=super(Forum,self).write(vals)
        if'active'invals:
            #archiving/unarchivingaforumdoesitonitsposts,too
            self.env['forum.post'].with_context(active_test=False).search([('forum_id','in',self.ids)]).write({'active':vals['active']})

        if'active'invalsor'website_id'invals:
            self._update_website_count()
        returnres

    defunlink(self):
        self._update_website_count()
        returnsuper(Forum,self).unlink()

    @api.model #TODO:Removeme,thisisnotan`api.model`method
    def_tag_to_write_vals(self,tags=''):
        Tag=self.env['forum.tag']
        post_tags=[]
        existing_keep=[]
        user=self.env.user
        fortagin(tagfortagintags.split(',')iftag):
            iftag.startswith('_'): #it'sanewtag
                #checkthatnotalreadycreatedmeanwhileormaybeexcludedbythelimitonthesearch
                tag_ids=Tag.search([('name','=',tag[1:]),('forum_id','=',self.id)])
                iftag_ids:
                    existing_keep.append(int(tag_ids[0]))
                else:
                    #checkifuserhaveKarmaneededtocreateneedtag
                    ifuser.exists()anduser.karma>=self.karma_tag_createandlen(tag)andlen(tag[1:].strip()):
                        post_tags.append((0,0,{'name':tag[1:],'forum_id':self.id}))
            else:
                existing_keep.append(int(tag))
        post_tags.insert(0,[6,0,existing_keep])
        returnpost_tags

    def_compute_website_url(self):
        return'/forum/%s'%(slug(self))

    defget_tags_first_char(self):
        """getsetoffirstletterofforumtags"""
        tags=self.env['forum.tag'].search([('forum_id','=',self.id),('posts_count','>',0)])
        returnsorted(set([tag.name[0].upper()fortagintagsiflen(tag.name)]))

    defgo_to_website(self):
        self.ensure_one()
        return{
            'type':'ir.actions.act_url',
            'target':'self',
            'url':self._compute_website_url(),
        }

    @api.model
    def_update_website_count(self):
        forwebsiteinself.env['website'].sudo().search([]):
            website.forums_count=self.env['forum.forum'].sudo().search_count(website.website_domain())


classPost(models.Model):

    _name='forum.post'
    _description='ForumPost'
    _inherit=['mail.thread','website.seo.metadata']
    _order="is_correctDESC,vote_countDESC,write_dateDESC"

    name=fields.Char('Title')
    forum_id=fields.Many2one('forum.forum',string='Forum',required=True)
    content=fields.Html('Content',strip_style=True)
    plain_content=fields.Text('PlainContent',compute='_get_plain_content',store=True)
    tag_ids=fields.Many2many('forum.tag','forum_tag_rel','forum_id','forum_tag_id',string='Tags')
    state=fields.Selection([('active','Active'),('pending','WaitingValidation'),('close','Closed'),('offensive','Offensive'),('flagged','Flagged')],string='Status',default='active')
    views=fields.Integer('Views',default=0,readonly=True,copy=False)
    active=fields.Boolean('Active',default=True)
    website_message_ids=fields.One2many(domain=lambdaself:[('model','=',self._name),('message_type','in',['email','comment'])])
    website_id=fields.Many2one(related='forum_id.website_id',readonly=True)

    #history
    create_date=fields.Datetime('Askedon',index=True,readonly=True)
    create_uid=fields.Many2one('res.users',string='Createdby',index=True,readonly=True)
    write_date=fields.Datetime('Updatedon',index=True,readonly=True)
    bump_date=fields.Datetime('Bumpedon',readonly=True,
                                help="Technicalfieldallowingtobumpaquestion.Writingonthisfieldwilltrigger"
                                     "awriteonwrite_dateandthereforebumpthepost.Directlywritingonwrite_date"
                                     "iscurrentlynotsupportedandthisfieldisaworkaround.")
    write_uid=fields.Many2one('res.users',string='Updatedby',index=True,readonly=True)
    relevancy=fields.Float('Relevance',compute="_compute_relevancy",store=True)

    #vote
    vote_ids=fields.One2many('forum.post.vote','post_id',string='Votes')
    user_vote=fields.Integer('MyVote',compute='_get_user_vote')
    vote_count=fields.Integer('TotalVotes',compute='_get_vote_count',store=True)

    #favorite
    favourite_ids=fields.Many2many('res.users',string='Favourite')
    user_favourite=fields.Boolean('IsFavourite',compute='_get_user_favourite')
    favourite_count=fields.Integer('Favorite',compute='_get_favorite_count',store=True)

    #hierarchy
    is_correct=fields.Boolean('Correct',help='Correctansweroransweraccepted')
    parent_id=fields.Many2one('forum.post',string='Question',ondelete='cascade',readonly=True,index=True)
    self_reply=fields.Boolean('Replytoownquestion',compute='_is_self_reply',store=True)
    child_ids=fields.One2many('forum.post','parent_id',string='PostAnswers',domain=lambdaself:[('forum_id','in',self.forum_id.ids)])
    child_count=fields.Integer('Answers',compute='_get_child_count',store=True)
    uid_has_answered=fields.Boolean('HasAnswered',compute='_get_uid_has_answered')
    has_validated_answer=fields.Boolean('Isanswered',compute='_get_has_validated_answer',store=True)

    #offensivemoderationtools
    flag_user_id=fields.Many2one('res.users',string='Flaggedby')
    moderator_id=fields.Many2one('res.users',string='Reviewedby',readonly=True)

    #closing
    closed_reason_id=fields.Many2one('forum.post.reason',string='Reason',copy=False)
    closed_uid=fields.Many2one('res.users',string='Closedby',index=True,readonly=True,copy=False)
    closed_date=fields.Datetime('Closedon',readonly=True,copy=False)

    #karmacalculationandaccess
    karma_accept=fields.Integer('Convertcommenttoanswer',compute='_get_post_karma_rights',compute_sudo=False)
    karma_edit=fields.Integer('Karmatoedit',compute='_get_post_karma_rights',compute_sudo=False)
    karma_close=fields.Integer('Karmatoclose',compute='_get_post_karma_rights',compute_sudo=False)
    karma_unlink=fields.Integer('Karmatounlink',compute='_get_post_karma_rights',compute_sudo=False)
    karma_comment=fields.Integer('Karmatocomment',compute='_get_post_karma_rights',compute_sudo=False)
    karma_comment_convert=fields.Integer('Karmatoconvertcommenttoanswer',compute='_get_post_karma_rights',compute_sudo=False)
    karma_flag=fields.Integer('Flagapostasoffensive',compute='_get_post_karma_rights',compute_sudo=False)
    can_ask=fields.Boolean('CanAsk',compute='_get_post_karma_rights',compute_sudo=False)
    can_answer=fields.Boolean('CanAnswer',compute='_get_post_karma_rights',compute_sudo=False)
    can_accept=fields.Boolean('CanAccept',compute='_get_post_karma_rights',compute_sudo=False)
    can_edit=fields.Boolean('CanEdit',compute='_get_post_karma_rights',compute_sudo=False)
    can_close=fields.Boolean('CanClose',compute='_get_post_karma_rights',compute_sudo=False)
    can_unlink=fields.Boolean('CanUnlink',compute='_get_post_karma_rights',compute_sudo=False)
    can_upvote=fields.Boolean('CanUpvote',compute='_get_post_karma_rights',compute_sudo=False)
    can_downvote=fields.Boolean('CanDownvote',compute='_get_post_karma_rights',compute_sudo=False)
    can_comment=fields.Boolean('CanComment',compute='_get_post_karma_rights',compute_sudo=False)
    can_comment_convert=fields.Boolean('CanConverttoComment',compute='_get_post_karma_rights',compute_sudo=False)
    can_view=fields.Boolean('CanView',compute='_get_post_karma_rights',search='_search_can_view',compute_sudo=False)
    can_display_biography=fields.Boolean("Istheauthor'sbiographyvisiblefromhispost",compute='_get_post_karma_rights',compute_sudo=False)
    can_post=fields.Boolean('CanAutomaticallybeValidated',compute='_get_post_karma_rights',compute_sudo=False)
    can_flag=fields.Boolean('CanFlag',compute='_get_post_karma_rights',compute_sudo=False)
    can_moderate=fields.Boolean('CanModerate',compute='_get_post_karma_rights',compute_sudo=False)

    def_search_can_view(self,operator,value):
        ifoperatornotin('=','!=','<>'):
            raiseValueError('Invalidoperator:%s'%(operator,))

        ifnotvalue:
            operator=operator=="="and'!='or'='
            value=True

        user=self.env.user
        #Won'timpactsitemap,search()inconverterisforcedaspublicuser
        ifself.env.is_admin():
            return[(1,'=',1)]

        req="""
            SELECTp.id
            FROMforum_postp
                   LEFTJOINres_usersuONp.create_uid=u.id
                   LEFTJOINforum_forumfONp.forum_id=f.id
            WHERE
                (p.create_uid=%sandf.karma_close_own<=%s)
                or(p.create_uid!=%sandf.karma_close_all<=%s)
                or(
                    u.karma>0
                    and(p.activeorp.create_uid=%s)
                )
        """

        op=operator=="="and"inselect"or"notinselect"

        #don'tuseparamnamedbecauseormwilladdotherparam(test_active,...)
        return[('id',op,(req,(user.id,user.karma,user.id,user.karma,user.id)))]

    @api.depends('content')
    def_get_plain_content(self):
        forpostinself:
            post.plain_content=tools.html2plaintext(post.content)[0:500]ifpost.contentelseFalse

    @api.depends('vote_count','forum_id.relevancy_post_vote','forum_id.relevancy_time_decay')
    def_compute_relevancy(self):
        forpostinself:
            ifpost.create_date:
                days=(datetime.today()-post.create_date).days
                post.relevancy=math.copysign(1,post.vote_count)*(abs(post.vote_count-1)**post.forum_id.relevancy_post_vote/(days+2)**post.forum_id.relevancy_time_decay)
            else:
                post.relevancy=0

    def_get_user_vote(self):
        votes=self.env['forum.post.vote'].search_read([('post_id','in',self._ids),('user_id','=',self._uid)],['vote','post_id'])
        mapped_vote=dict([(v['post_id'][0],v['vote'])forvinvotes])
        forvoteinself:
            vote.user_vote=mapped_vote.get(vote.id,0)

    @api.depends('vote_ids.vote')
    def_get_vote_count(self):
        read_group_res=self.env['forum.post.vote'].read_group([('post_id','in',self._ids)],['post_id','vote'],['post_id','vote'],lazy=False)
        result=dict.fromkeys(self._ids,0)
        fordatainread_group_res:
            result[data['post_id'][0]]+=data['__count']*int(data['vote'])
        forpostinself:
            post.vote_count=result[post.id]

    def_get_user_favourite(self):
        forpostinself:
            post.user_favourite=post._uidinpost.favourite_ids.ids

    @api.depends('favourite_ids')
    def_get_favorite_count(self):
        forpostinself:
            post.favourite_count=len(post.favourite_ids)

    @api.depends('create_uid','parent_id')
    def_is_self_reply(self):
        forpostinself:
            post.self_reply=post.parent_id.create_uid.id==post._uid

    @api.depends('child_ids')
    def_get_child_count(self):
        forpostinself:
            post.child_count=len(post.child_ids)

    def_get_uid_has_answered(self):
        forpostinself:
            post.uid_has_answered=post._uidinpost.child_ids.create_uid.ids

    @api.depends('child_ids.is_correct')
    def_get_has_validated_answer(self):
        forpostinself:
            post.has_validated_answer=any(answer.is_correctforanswerinpost.child_ids)

    @api.depends_context('uid')
    def_get_post_karma_rights(self):
        user=self.env.user
        is_admin=self.env.is_admin()
        #sudoedrecordsetinsteadofindividualpostssovaluescanbe
        #prefetchedinbulk
        forpost,post_sudoinzip(self,self.sudo()):
            is_creator=post.create_uid==user

            post.karma_accept=post.forum_id.karma_answer_accept_ownifpost.parent_id.create_uid==userelsepost.forum_id.karma_answer_accept_all
            post.karma_edit=post.forum_id.karma_edit_ownifis_creatorelsepost.forum_id.karma_edit_all
            post.karma_close=post.forum_id.karma_close_ownifis_creatorelsepost.forum_id.karma_close_all
            post.karma_unlink=post.forum_id.karma_unlink_ownifis_creatorelsepost.forum_id.karma_unlink_all
            post.karma_comment=post.forum_id.karma_comment_ownifis_creatorelsepost.forum_id.karma_comment_all
            post.karma_comment_convert=post.forum_id.karma_comment_convert_ownifis_creatorelsepost.forum_id.karma_comment_convert_all
            post.karma_flag=post.forum_id.karma_flag

            post.can_ask=is_adminoruser.karma>=post.forum_id.karma_ask
            post.can_answer=is_adminoruser.karma>=post.forum_id.karma_answer
            post.can_accept=is_adminoruser.karma>=post.karma_accept
            post.can_edit=is_adminoruser.karma>=post.karma_edit
            post.can_close=is_adminoruser.karma>=post.karma_close
            post.can_unlink=is_adminoruser.karma>=post.karma_unlink
            post.can_upvote=is_adminoruser.karma>=post.forum_id.karma_upvoteorpost.user_vote==-1
            post.can_downvote=is_adminoruser.karma>=post.forum_id.karma_downvoteorpost.user_vote==1
            post.can_comment=is_adminoruser.karma>=post.karma_comment
            post.can_comment_convert=is_adminoruser.karma>=post.karma_comment_convert
            post.can_view=is_adminoruser.karma>=post.karma_closeor(post_sudo.create_uid.karma>0and(post_sudo.activeorpost_sudo.create_uid==user))
            post.can_display_biography=is_adminorpost_sudo.create_uid.karma>=post.forum_id.karma_user_bio
            post.can_post=is_adminoruser.karma>=post.forum_id.karma_post
            post.can_flag=is_adminoruser.karma>=post.forum_id.karma_flag
            post.can_moderate=is_adminoruser.karma>=post.forum_id.karma_moderate

    def_update_content(self,content,forum_id):
        forum=self.env['forum.forum'].browse(forum_id)
        ifcontentandself.env.user.karma<forum.karma_dofollow:
            formatchinre.findall(r'<a\s.*href=".*?">',content):
                match=re.escape(match) #replaceparenthesisorspecialcharinregex
                content=re.sub(match,match[:3]+'rel="nofollow"'+match[3:],content)

        ifself.env.user.karma<forum.karma_editor:
            filter_regexp=r'(<img.*?>)|(<a[^>]*?href[^>]*?>)|(<[a-z|A-Z]+[^>]*style\s*=\s*[\'"][^\'"]*\s*background[^:]*:[^url;]*url)'
            content_match=re.search(filter_regexp,content,re.I)
            ifcontent_match:
                raiseAccessError(_('%dkarmarequiredtopostanimageorlink.',forum.karma_editor))
        returncontent

    def_default_website_meta(self):
        res=super(Post,self)._default_website_meta()
        res['default_opengraph']['og:title']=res['default_twitter']['twitter:title']=self.name
        res['default_opengraph']['og:description']=res['default_twitter']['twitter:description']=self.plain_content
        res['default_opengraph']['og:image']=res['default_twitter']['twitter:image']=self.env['website'].image_url(self.create_uid,'image_1024')
        res['default_twitter']['twitter:card']='summary'
        res['default_meta_description']=self.plain_content
        returnres

    @api.constrains('parent_id')
    def_check_parent_id(self):
        ifnotself._check_recursion():
            raiseValidationError(_('Youcannotcreaterecursiveforumposts.'))

    @api.model
    defcreate(self,vals):
        if'content'invalsandvals.get('forum_id'):
            vals['content']=self._update_content(vals['content'],vals['forum_id'])

        post=super(Post,self.with_context(mail_create_nolog=True)).create(vals)
        #deletedorclosedquestions
        ifpost.parent_idand(post.parent_id.state=='close'orpost.parent_id.activeisFalse):
            raiseUserError(_('Postinganswerona[Deleted]or[Closed]questionisnotpossible.'))
        #karma-basedaccess
        ifnotpost.parent_idandnotpost.can_ask:
            raiseAccessError(_('%dkarmarequiredtocreateanewquestion.',post.forum_id.karma_ask))
        elifpost.parent_idandnotpost.can_answer:
            raiseAccessError(_('%dkarmarequiredtoansweraquestion.',post.forum_id.karma_answer))
        ifnotpost.parent_idandnotpost.can_post:
            post.sudo().state='pending'

        #addkarmaforpostingnewquestions
        ifnotpost.parent_idandpost.state=='active':
            self.env.user.sudo().add_karma(post.forum_id.karma_gen_question_new)
        post.post_notification()
        returnpost

    @api.model
    def_get_mail_message_access(self,res_ids,operation,model_name=None):
        #XDOFIXME:tobecorrectlyfixedwithnew_get_mail_message_accessandfilteraccessrule
        ifoperationin('write','unlink')and(notmodel_nameormodel_name=='forum.post'):
            #Makesureonlyauthorormoderatorcanedit/deletemessages
            forpostinself.browse(res_ids):
                ifnotpost.can_edit:
                    raiseAccessError(_('%dkarmarequiredtoeditapost.',post.karma_edit))
        returnsuper(Post,self)._get_mail_message_access(res_ids,operation,model_name=model_name)

    defwrite(self,vals):
        trusted_keys=['active','is_correct','tag_ids'] #fieldswheresecurityischeckedmanually
        if'content'invals:
            vals['content']=self._update_content(vals['content'],self.forum_id.id)

        tag_ids=False
        if'tag_ids'invals:
            tag_ids=set(self.new({'tag_ids':vals['tag_ids']}).tag_ids.ids)

        forpostinself:
            if'state'invals:
                ifvals['state']in['active','close']:
                    ifnotpost.can_close:
                        raiseAccessError(_('%dkarmarequiredtocloseorreopenapost.',post.karma_close))
                    trusted_keys+=['state','closed_uid','closed_date','closed_reason_id']
                elifvals['state']=='flagged':
                    ifnotpost.can_flag:
                        raiseAccessError(_('%dkarmarequiredtoflagapost.',post.forum_id.karma_flag))
                    trusted_keys+=['state','flag_user_id']
            if'active'invals:
                ifnotpost.can_unlink:
                    raiseAccessError(_('%dkarmarequiredtodeleteorreactivateapost.',post.karma_unlink))
            if'is_correct'invals:
                ifnotpost.can_accept:
                    raiseAccessError(_('%dkarmarequiredtoacceptorrefuseananswer.',post.karma_accept))
                #updatekarmaexceptforself-acceptance
                mult=1ifvals['is_correct']else-1
                ifvals['is_correct']!=post.is_correctandpost.create_uid.id!=self._uid:
                    post.create_uid.sudo().add_karma(post.forum_id.karma_gen_answer_accepted*mult)
                    self.env.user.sudo().add_karma(post.forum_id.karma_gen_answer_accept*mult)
            iftag_ids:
                ifset(post.tag_ids.ids)!=tag_idsandself.env.user.karma<post.forum_id.karma_edit_retag:
                    raiseAccessError(_('%dkarmarequiredtoretag.',post.forum_id.karma_edit_retag))
            ifany(keynotintrusted_keysforkeyinvals)andnotpost.can_edit:
                raiseAccessError(_('%dkarmarequiredtoeditapost.',post.karma_edit))

        res=super(Post,self).write(vals)

        #ifpostcontentmodify,notifyfollowers
        if'content'invalsor'name'invals:
            forpostinself:
                ifpost.parent_id:
                    body,subtype_xmlid=_('AnswerEdited'),'website_forum.mt_answer_edit'
                    obj_id=post.parent_id
                else:
                    body,subtype_xmlid=_('QuestionEdited'),'website_forum.mt_question_edit'
                    obj_id=post
                obj_id.message_post(body=body,subtype_xmlid=subtype_xmlid)
        if'active'invals:
            answers=self.env['forum.post'].with_context(active_test=False).search([('parent_id','in',self.ids)])
            ifanswers:
                answers.write({'active':vals['active']})
        returnres

    defpost_notification(self):
        forpostinself:
            tag_partners=post.tag_ids.sudo().mapped('message_partner_ids')

            ifpost.state=='active'andpost.parent_id:
                post.parent_id.message_post_with_view(
                    'website_forum.forum_post_template_new_answer',
                    subject=_('Re:%s',post.parent_id.name),
                    partner_ids=[(4,p.id)forpintag_partners],
                    subtype_id=self.env['ir.model.data'].xmlid_to_res_id('website_forum.mt_answer_new'))
            elifpost.state=='active'andnotpost.parent_id:
                post.message_post_with_view(
                    'website_forum.forum_post_template_new_question',
                    subject=post.name,
                    partner_ids=[(4,p.id)forpintag_partners],
                    subtype_id=self.env['ir.model.data'].xmlid_to_res_id('website_forum.mt_question_new'))
            elifpost.state=='pending'andnotpost.parent_id:
                #TDEFIXME:inmaster,youshouldprobablyuseasubtype;
                #howeverhereweremovesubtypebutsetpartner_ids
                partners=post.sudo().message_partner_ids|tag_partners
                partners=partners.filtered(lambdapartner:partner.user_idsandany(user.karma>=post.forum_id.karma_moderateforuserinpartner.user_ids))

                post.message_post_with_view(
                    'website_forum.forum_post_template_validation',
                    subject=post.name,
                    partner_ids=partners.ids,
                    subtype_id=self.env['ir.model.data'].xmlid_to_res_id('mail.mt_note'))
        returnTrue

    defreopen(self):
        ifany(post.parent_idorpost.state!='close'forpostinself):
            returnFalse

        reason_offensive=self.env.ref('website_forum.reason_7')
        reason_spam=self.env.ref('website_forum.reason_8')
        forpostinself:
            ifpost.closed_reason_idin(reason_offensive,reason_spam):
                _logger.info('Upvotinguser<%s>,reopeningspam/offensivequestion',
                             post.create_uid)

                karma=post.forum_id.karma_gen_answer_flagged
                ifpost.closed_reason_id==reason_spam:
                    #Iffirstpost,increasethekarmatoadd
                    count_post=post.search_count([('parent_id','=',False),('forum_id','=',post.forum_id.id),('create_uid','=',post.create_uid.id)])
                    ifcount_post==1:
                        karma*=10
                post.create_uid.sudo().add_karma(karma*-1)

        self.sudo().write({'state':'active'})

    defclose(self,reason_id):
        ifany(post.parent_idforpostinself):
            returnFalse

        reason_offensive=self.env.ref('website_forum.reason_7').id
        reason_spam=self.env.ref('website_forum.reason_8').id
        ifreason_idin(reason_offensive,reason_spam):
            forpostinself:
                _logger.info('Downvotinguser<%s>forpostingspam/offensivecontents',
                             post.create_uid)
                karma=post.forum_id.karma_gen_answer_flagged
                ifreason_id==reason_spam:
                    #Iffirstpost,increasethekarmatoremove
                    count_post=post.search_count([('parent_id','=',False),('forum_id','=',post.forum_id.id),('create_uid','=',post.create_uid.id)])
                    ifcount_post==1:
                        karma*=10
                post.create_uid.sudo().add_karma(karma)

        self.write({
            'state':'close',
            'closed_uid':self._uid,
            'closed_date':datetime.today().strftime(tools.DEFAULT_SERVER_DATETIME_FORMAT),
            'closed_reason_id':reason_id,
        })
        returnTrue

    defvalidate(self):
        forpostinself:
            ifnotpost.can_moderate:
                raiseAccessError(_('%dkarmarequiredtovalidateapost.',post.forum_id.karma_moderate))
            #ifstate==pending,nokarmapreviouslyaddedforthenewquestion
            ifpost.state=='pending':
                post.create_uid.sudo().add_karma(post.forum_id.karma_gen_question_new)
            post.write({
                'state':'active',
                'active':True,
                'moderator_id':self.env.user.id,
            })
            post.post_notification()
        returnTrue

    defrefuse(self):
        forpostinself:
            ifnotpost.can_moderate:
                raiseAccessError(_('%dkarmarequiredtorefuseapost.',post.forum_id.karma_moderate))
            post.moderator_id=self.env.user
        returnTrue

    defflag(self):
        res=[]
        forpostinself:
            ifnotpost.can_flag:
                raiseAccessError(_('%dkarmarequiredtoflagapost.',post.forum_id.karma_flag))
            ifpost.state=='flagged':
               res.append({'error':'post_already_flagged'})
            elifpost.state=='active':
                #TODO:potentialperformancebottleneck,canbebatched
                post.write({
                    'state':'flagged',
                    'flag_user_id':self.env.user.id,
                })
                res.append(
                    post.can_moderateand
                    {'success':'post_flagged_moderator'}or
                    {'success':'post_flagged_non_moderator'}
                )
            else:
                res.append({'error':'post_non_flaggable'})
        returnres

    defmark_as_offensive(self,reason_id):
        forpostinself:
            ifnotpost.can_moderate:
                raiseAccessError(_('%dkarmarequiredtomarkapostasoffensive.',post.forum_id.karma_moderate))
            #removesomekarma
            _logger.info('Downvotinguser<%s>forpostingspam/offensivecontents',post.create_uid)
            post.create_uid.sudo().add_karma(post.forum_id.karma_gen_answer_flagged)
            #TODO:potentialbottleneck,couldbedoneinbatch
            post.write({
                'state':'offensive',
                'moderator_id':self.env.user.id,
                'closed_date':fields.Datetime.now(),
                'closed_reason_id':reason_id,
                'active':False,
            })
        returnTrue

    defmark_as_offensive_batch(self,key,values):
        spams=self.browse()
        ifkey=='create_uid':
            spams=self.filtered(lambdax:x.create_uid.idinvalues)
        elifkey=='country_id':
            spams=self.filtered(lambdax:x.create_uid.country_id.idinvalues)
        elifkey=='post_id':
            spams=self.filtered(lambdax:x.idinvalues)

        reason_id=self.env.ref('website_forum.reason_8').id
        _logger.info('User%smarkedasspams(inbatch):%s'%(self.env.uid,spams))
        returnspams.mark_as_offensive(reason_id)

    defunlink(self):
        forpostinself:
            ifnotpost.can_unlink:
                raiseAccessError(_('%dkarmarequiredtounlinkapost.',post.karma_unlink))
        #ifunlinkingananswerwithacceptedanswer:removeprovidedkarma
        forpostinself:
            ifpost.is_correct:
                post.create_uid.sudo().add_karma(post.forum_id.karma_gen_answer_accepted*-1)
                self.env.user.sudo().add_karma(post.forum_id.karma_gen_answer_accepted*-1)
        returnsuper(Post,self).unlink()

    defbump(self):
        """Bumpaquestion:triggerawrite_datebywritingonadummybump_date
        field.Onecannotbumpaquestionmorethanonceevery10days."""
        self.ensure_one()
        ifself.forum_id.allow_bumpandnotself.child_idsand(datetime.today()-datetime.strptime(self.write_date,tools.DEFAULT_SERVER_DATETIME_FORMAT)).days>9:
            #writethroughsupertobypasskarma;sudotoallowpublicusertobumpanypost
            returnself.sudo().write({'bump_date':fields.Datetime.now()})
        returnFalse

    defvote(self,upvote=True):
        self.ensure_one()
        Vote=self.env['forum.post.vote']
        existing_vote=Vote.search([('post_id','=',self.id),('user_id','=',self._uid)])
        new_vote_value='1'ifupvoteelse'-1'
        ifexisting_vote:
            ifupvote:
                new_vote_value='0'ifexisting_vote.vote=='-1'else'1'
            else:
                new_vote_value='0'ifexisting_vote.vote=='1'else'-1'
            existing_vote.vote=new_vote_value
        else:
            Vote.create({'post_id':self.id,'vote':new_vote_value})
        return{'vote_count':self.vote_count,'user_vote':new_vote_value}

    defconvert_answer_to_comment(self):
        """Toolstoconvertananswer(forum.post)toacomment(mail.message).
        Theoriginalpostisunlinkedandanewcommentispostedonthequestion
        usingthepostcreate_uidasthecomment'sauthor."""
        self.ensure_one()
        ifnotself.parent_id:
            returnself.env['mail.message']

        #karma-basedactioncheck:usethepostfieldthatcomputedown/allvalue
        ifnotself.can_comment_convert:
            raiseAccessError(_('%dkarmarequiredtoconvertananswertoacomment.',self.karma_comment_convert))

        #postthemessage
        question=self.parent_id
        self_sudo=self.sudo()
        values={
            'author_id':self_sudo.create_uid.partner_id.id, #usesudoherebecauseofaccesstores.usersmodel
            'email_from':self_sudo.create_uid.email_formatted, #usesudoherebecauseofaccesstores.usersmodel
            'body':tools.html_sanitize(self.content,sanitize_attributes=True,strip_style=True,strip_classes=True),
            'message_type':'comment',
            'subtype_xmlid':'mail.mt_comment',
            'date':self.create_date,
        }
        #donewiththeauthorusertohavecreate_uidcorrectlyset
        new_message=question.with_user(self_sudo.create_uid.id).with_context(mail_create_nosubscribe=True).sudo().message_post(**values).sudo(False)

        #unlinktheoriginalanswer,usingSUPERUSER_IDtoavoidkarmaissues
        self.sudo().unlink()

        returnnew_message

    @api.model
    defconvert_comment_to_answer(self,message_id,default=None):
        """Tooltoconvertacomment(mail.message)intoananswer(forum.post).
        Theoriginalcommentisunlinkedandanewanswerfromthecomment'sauthor
        iscreated.Nothingisdoneifthecomment'sauthoralreadyansweredthe
        question."""
        comment=self.env['mail.message'].sudo().browse(message_id)
        post=self.browse(comment.res_id)
        ifnotcomment.author_idornotcomment.author_id.user_ids: #onlycommentpostedbyuserscanbeconverted
            returnFalse

        #karma-basedactioncheck:mustcheckthemessage'sauthortoknowifown/all
        is_author=comment.author_id.id==self.env.user.partner_id.id
        karma_own=post.forum_id.karma_comment_convert_own
        karma_all=post.forum_id.karma_comment_convert_all
        karma_convert=is_authorandkarma_ownorkarma_all
        can_convert=self.env.user.karma>=karma_convert
        ifnotcan_convert:
            ifis_authorandkarma_own<karma_all:
                raiseAccessError(_('%dkarmarequiredtoconvertyourcommenttoananswer.',karma_own))
            else:
                raiseAccessError(_('%dkarmarequiredtoconvertacommenttoananswer.',karma_all))

        #checkthemessage'sauthorhasnotalreadyananswer
        question=post.parent_idifpost.parent_idelsepost
        post_create_uid=comment.author_id.user_ids[0]
        ifany(answer.create_uid.id==post_create_uid.idforanswerinquestion.child_ids):
            returnFalse

        #createthenewpost
        post_values={
            'forum_id':question.forum_id.id,
            'content':comment.body,
            'parent_id':question.id,
            'name':_('Re:%s')%(question.nameor''),
        }
        #donewiththeauthorusertohavecreate_uidcorrectlyset
        new_post=self.with_user(post_create_uid).sudo().create(post_values).sudo(False)

        #deletecomment
        comment.unlink()

        returnnew_post

    defunlink_comment(self,message_id):
        result=[]
        forpostinself:
            user=self.env.user
            comment=self.env['mail.message'].sudo().browse(message_id)
            ifnotcomment.model=='forum.post'ornotcomment.res_id==post.id:
                result.append(False)
                continue
            #karma-basedactioncheck:mustcheckthemessage'sauthortoknowifownorall
            karma_unlink=(
                comment.author_id.id==user.partner_id.idand
                post.forum_id.karma_comment_unlink_ownorpost.forum_id.karma_comment_unlink_all
            )
            can_unlink=user.karma>=karma_unlink
            ifnotcan_unlink:
                raiseAccessError(_('%dkarmarequiredtounlinkacomment.',karma_unlink))
            result.append(comment.unlink())
        returnresult

    def_set_viewed(self):
        self.ensure_one()
        returnsql.increment_field_skiplock(self,'views')

    defget_access_action(self,access_uid=None):
        """Insteadoftheclassicformview,redirecttothepostonthewebsitedirectly"""
        self.ensure_one()
        return{
            'type':'ir.actions.act_url',
            'url':'/forum/%s/%s'%(self.forum_id.id,self.id),
            'target':'self',
            'target_type':'public',
            'res_id':self.id,
        }

    def_notify_get_groups(self,msg_vals=None):
        """Addaccessbuttontoeveryoneifthedocumentisactive."""
        groups=super(Post,self)._notify_get_groups(msg_vals=msg_vals)

        ifself.state=='active':
            forgroup_name,group_method,group_dataingroups:
                group_data['has_button_access']=True

        returngroups

    @api.returns('mail.message',lambdavalue:value.id)
    defmessage_post(self,*,message_type='notification',**kwargs):
        ifself.idsandmessage_type=='comment': #usercommentshavearestrictiononkarma
            #addfollowersofcommentsontheparentpost
            ifself.parent_id:
                partner_ids=kwargs.get('partner_ids',[])
                comment_subtype=self.sudo().env.ref('mail.mt_comment')
                question_followers=self.env['mail.followers'].sudo().search([
                    ('res_model','=',self._name),
                    ('res_id','=',self.parent_id.id),
                    ('partner_id','!=',False),
                ]).filtered(lambdafol:comment_subtypeinfol.subtype_ids).mapped('partner_id')
                partner_ids+=question_followers.ids
                kwargs['partner_ids']=partner_ids

            self.ensure_one()
            ifnotself.can_comment:
                raiseAccessError(_('%dkarmarequiredtocomment.',self.karma_comment))
            ifnotkwargs.get('record_name')andself.parent_id:
                kwargs['record_name']=self.parent_id.name
        returnsuper(Post,self).message_post(message_type=message_type,**kwargs)

    def_notify_record_by_inbox(self,message,recipients_data,msg_vals=False,**kwargs):
        """Overridetoavoidkeepingallnotifiedrecipientsofacomment.
        Weavoidtrackingneedactiononpostcomments.Onlyemailsshouldbe
        sufficient."""
        ifmsg_vals.get('message_type',message.message_type)=='comment':
            return
        returnsuper(Post,self)._notify_record_by_inbox(message,recipients_data,msg_vals=msg_vals,**kwargs)

    def_compute_website_url(self):
        return'/forum/{forum}/{post}{anchor}'.format(
            forum=slug(self.forum_id),
            post=slug(self),
            anchor=self.parent_idand'#answer_%d'%self.idor''
        )

    defgo_to_website(self):
        self.ensure_one()
        return{
            'type':'ir.actions.act_url',
            'target':'self',
            'url':self._compute_website_url(),
        }


classPostReason(models.Model):
    _name="forum.post.reason"
    _description="PostClosingReason"
    _order='name'

    name=fields.Char(string='ClosingReason',required=True,translate=True)
    reason_type=fields.Selection([('basic','Basic'),('offensive','Offensive')],string='ReasonType',default='basic')


classVote(models.Model):
    _name='forum.post.vote'
    _description='PostVote'
    _order='create_datedesc,iddesc'

    post_id=fields.Many2one('forum.post',string='Post',ondelete='cascade',required=True)
    user_id=fields.Many2one('res.users',string='User',required=True,default=lambdaself:self._uid)
    vote=fields.Selection([('1','1'),('-1','-1'),('0','0')],string='Vote',required=True,default='1')
    create_date=fields.Datetime('CreateDate',index=True,readonly=True)
    forum_id=fields.Many2one('forum.forum',string='Forum',related="post_id.forum_id",store=True,readonly=False)
    recipient_id=fields.Many2one('res.users',string='To',related="post_id.create_uid",store=True,readonly=False)

    _sql_constraints=[
        ('vote_uniq','unique(post_id,user_id)',"Votealreadyexists!"),
    ]

    def_get_karma_value(self,old_vote,new_vote,up_karma,down_karma):
        _karma_upd={
            '-1':{'-1':0,'0':-1*down_karma,'1':-1*down_karma+up_karma},
            '0':{'-1':1*down_karma,'0':0,'1':up_karma},
            '1':{'-1':-1*up_karma+down_karma,'0':-1*up_karma,'1':0}
        }
        return_karma_upd[old_vote][new_vote]

    @api.model
    defcreate(self,vals):
        #can'tmodifyownerofavote
        ifnotself.env.is_admin():
            vals.pop('user_id',None)

        vote=super(Vote,self).create(vals)

        vote._check_general_rights()
        vote._check_karma_rights(vote.vote=='1')

        #karmaupdate
        vote._vote_update_karma('0',vote.vote)
        returnvote

    defwrite(self,values):
        #can'tmodifyownerofavote
        ifnotself.env.is_admin():
            values.pop('user_id',None)

        forvoteinself:
            vote._check_general_rights(values)
            if'vote'invalues:
                if(values['vote']=='1'orvote.vote=='-1'andvalues['vote']=='0'):
                    upvote=True
                elif(values['vote']=='-1'orvote.vote=='1'andvalues['vote']=='0'):
                    upvote=False
                vote._check_karma_rights(upvote)

                #karmaupdate
                vote._vote_update_karma(vote.vote,values['vote'])

        res=super(Vote,self).write(values)
        returnres

    def_check_general_rights(self,vals={}):
        post=self.post_id
        ifvals.get('post_id'):
            post=self.env['forum.post'].browse(vals.get('post_id'))
        ifnotself.env.is_admin():
            #ownpostcheck
            ifself._uid==post.create_uid.id:
                raiseUserError(_('Itisnotallowedtovoteforitsownpost.'))
            #ownvotecheck
            ifself._uid!=self.user_id.id:
                raiseUserError(_('Itisnotallowedtomodifysomeoneelse\'svote.'))

    def_check_karma_rights(self,upvote=None):
        #karmacheck
        ifupvoteandnotself.post_id.can_upvote:
            raiseAccessError(_('%dkarmarequiredtoupvote.',self.post_id.forum_id.karma_upvote))
        elifnotupvoteandnotself.post_id.can_downvote:
            raiseAccessError(_('%dkarmarequiredtodownvote.',self.post_id.forum_id.karma_downvote))

    def_vote_update_karma(self,old_vote,new_vote):
        ifself.post_id.parent_id:
            karma_value=self._get_karma_value(old_vote,new_vote,self.forum_id.karma_gen_answer_upvote,self.forum_id.karma_gen_answer_downvote)
        else:
            karma_value=self._get_karma_value(old_vote,new_vote,self.forum_id.karma_gen_question_upvote,self.forum_id.karma_gen_question_downvote)
        self.recipient_id.sudo().add_karma(karma_value)


classTags(models.Model):
    _name="forum.tag"
    _description="ForumTag"
    _inherit=['mail.thread','website.seo.metadata']

    name=fields.Char('Name',required=True)
    forum_id=fields.Many2one('forum.forum',string='Forum',required=True)
    post_ids=fields.Many2many(
        'forum.post','forum_tag_rel','forum_tag_id','forum_id',
        string='Posts',domain=[('state','=','active')])
    posts_count=fields.Integer('NumberofPosts',compute='_get_posts_count',store=True)

    _sql_constraints=[
        ('name_uniq','unique(name,forum_id)',"Tagnamealreadyexists!"),
    ]

    @api.depends("post_ids","post_ids.tag_ids","post_ids.state","post_ids.active")
    def_get_posts_count(self):
        fortaginself:
            tag.posts_count=len(tag.post_ids) #statefilterisinfielddomain

    @api.model
    defcreate(self,vals):
        forum=self.env['forum.forum'].browse(vals.get('forum_id'))
        ifself.env.user.karma<forum.karma_tag_create:
            raiseAccessError(_('%dkarmarequiredtocreateanewTag.',forum.karma_tag_create))
        returnsuper(Tags,self.with_context(mail_create_nolog=True,mail_create_nosubscribe=True)).create(vals)

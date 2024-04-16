#-*-coding:utf-8-*-
#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.

importitertools
importrandom

fromflectraimportmodels,_


classMailBot(models.AbstractModel):
    _name='mail.bot'
    _description='MailBot'

    def_apply_logic(self,record,values,command=None):
        """Applybotlogictogenerateananswer(ornot)fortheuser
        Thelogicwillonlybeappliedifflectrabotisinachatwithauseror
        ifsomeonepingedflectrabot.

         :paramrecord:themail_thread(ormail_channel)wheretheuser
            messagewasposted/flectrabotwillanswer.
         :paramvalues:msg_valuesofthemessage_postorothervaluesneededbylogic
         :paramcommand:thenameofthecalledcommandifthelogicisnottriggeredbyamessage_post
        """
        flectrabot_id=self.env['ir.model.data'].xmlid_to_res_id("base.partner_root")
        iflen(record)!=1orvalues.get("author_id")==flectrabot_id:
            return
        ifself._is_bot_pinged(values)orself._is_bot_in_private_channel(record):
            body=values.get("body","").replace(u'\xa0',u'').strip().lower().strip(".!")
            answer=self._get_answer(record,body,values,command)
            ifanswer:
                message_type=values.get('message_type','comment')
                subtype_id=values.get('subtype_id',self.env['ir.model.data'].xmlid_to_res_id('mail.mt_comment'))
                record.with_context(mail_create_nosubscribe=True).sudo().message_post(body=answer,author_id=flectrabot_id,message_type=message_type,subtype_id=subtype_id)

    def_get_answer(self,record,body,values,command=False):
        #onboarding
        flectrabot_state=self.env.user.flectrabot_state
        ifself._is_bot_in_private_channel(record):
            #mainflow
            ifflectrabot_state=='onboarding_emoji'andself._body_contains_emoji(body):
                self.env.user.flectrabot_state="onboarding_command"
                self.env.user.flectrabot_failed=False
                return_("Great!👍<br/>Toaccessspecialcommands,<b>startyoursentencewith</b><spanclass=\"o_flectrabot_command\">/</span>.Trygettinghelp.")
            elifflectrabot_state=='onboarding_command'andcommand=='help':
                self.env.user.flectrabot_state="onboarding_ping"
                self.env.user.flectrabot_failed=False
                return_("Wowyouareanatural!<br/>Pingsomeonewith@usernametograbtheirattention.<b>Trytopingmeusing</b><spanclass=\"o_flectrabot_command\">@FlectraBot</span>inasentence.")
            elifflectrabot_state=='onboarding_ping'andself._is_bot_pinged(values):
                self.env.user.flectrabot_state="onboarding_attachement"
                self.env.user.flectrabot_failed=False
                return_("Yep,Iamhere!🎉<br/>Now,try<b>sendinganattachment</b>,likeapictureofyourcutedog...")
            elifflectrabot_state=='onboarding_attachement'andvalues.get("attachment_ids"):
                self.env.user.flectrabot_state="idle"
                self.env.user.flectrabot_failed=False
                return_("Iamasimplebot,butifthat'sadog,heisthecutest😊<br/>Congratulations,youfinishedthistour.Youcannow<b>closethischatwindow</b>.EnjoydiscoveringFlectra.")
            elifflectrabot_statein(False,"idle","not_initialized")and(_('startthetour')inbody.lower()):
                self.env.user.flectrabot_state="onboarding_emoji"
                return_("Tostart,trytosendmeanemoji:)")
            #eastereggs
            elifflectrabot_state=="idle"andbodyin['❤️',_('iloveyou'),_('love')]:
                return_("Aaaaawthat'sreallycutebut,youknow,botsdon'tworkthatway.You'retoohumanforme!Let'skeepitprofessional❤️")
            elif_('fuck')inbodyor"fuck"inbody:
                return_("That'snotnice!I'mabotbutIhavefeelings...💔")
            #helpmessage
            elifself._is_help_requested(body)orflectrabot_state=='idle':
                return_("Unfortunately,I'mjustabot😞Idon'tunderstand!Ifyouneedhelpdiscoveringourproduct,pleasecheck"
                         "<ahref=\"https://www.flectrahq.com/page/docs\"target=\"_blank\">ourdocumentation</a>or"
                         "<ahref=\"https://www.flectrahq.com/slides\"target=\"_blank\">ourvideos</a>.")
            else:
                #repeatquestion
                ifflectrabot_state=='onboarding_emoji':
                    self.env.user.flectrabot_failed=True
                    return_("Notexactly.Tocontinuethetour,sendanemoji:<b>type</b><spanclass=\"o_flectrabot_command\">:)</span>andpressenter.")
                elifflectrabot_state=='onboarding_attachement':
                    self.env.user.flectrabot_failed=True
                    return_("To<b>sendanattachment</b>,clickonthe<iclass=\"fafa-paperclip\"aria-hidden=\"true\"></i>iconandselectafile.")
                elifflectrabot_state=='onboarding_command':
                    self.env.user.flectrabot_failed=True
                    return_("Notsurewhatyouaredoing.Please,type<spanclass=\"o_flectrabot_command\">/</span>andwaitforthepropositions.Select<spanclass=\"o_flectrabot_command\">help</span>andpressenter")
                elifflectrabot_state=='onboarding_ping':
                    self.env.user.flectrabot_failed=True
                    return_("Sorry,Iamnotlistening.Togetsomeone'sattention,<b>pinghim</b>.Write<spanclass=\"o_flectrabot_command\">@FlectraBot</span>andselectme.")
                returnrandom.choice([
                    _("I'mnotsmartenoughtoansweryourquestion.<br/>Tofollowmyguide,ask:<spanclass=\"o_flectrabot_command\">startthetour</span>."),
                    _("Hmmm..."),
                    _("I'mafraidIdon'tunderstand.Sorry!"),
                    _("SorryI'msleepy.Ornot!MaybeI'mjusttryingtohidemyunawarenessofhumanlanguage...<br/>Icanshowyoufeaturesifyouwrite:<spanclass=\"o_flectrabot_command\">startthetour</span>.")
                ])
        returnFalse

    def_body_contains_emoji(self,body):
        #comingfromhttps://unicode.org/emoji/charts/full-emoji-list.html
        emoji_list=itertools.chain(
            range(0x231A,0x231c),
            range(0x23E9,0x23f4),
            range(0x23F8,0x23fb),
            range(0x25AA,0x25ac),
            range(0x25FB,0x25ff),
            range(0x2600,0x2605),
            range(0x2614,0x2616),
            range(0x2622,0x2624),
            range(0x262E,0x2630),
            range(0x2638,0x263b),
            range(0x2648,0x2654),
            range(0x265F,0x2661),
            range(0x2665,0x2667),
            range(0x267E,0x2680),
            range(0x2692,0x2698),
            range(0x269B,0x269d),
            range(0x26A0,0x26a2),
            range(0x26AA,0x26ac),
            range(0x26B0,0x26b2),
            range(0x26BD,0x26bf),
            range(0x26C4,0x26c6),
            range(0x26D3,0x26d5),
            range(0x26E9,0x26eb),
            range(0x26F0,0x26f6),
            range(0x26F7,0x26fb),
            range(0x2708,0x270a),
            range(0x270A,0x270c),
            range(0x270C,0x270e),
            range(0x2733,0x2735),
            range(0x2753,0x2756),
            range(0x2763,0x2765),
            range(0x2795,0x2798),
            range(0x2934,0x2936),
            range(0x2B05,0x2b08),
            range(0x2B1B,0x2b1d),
            range(0x1F170,0x1f172),
            range(0x1F191,0x1f19b),
            range(0x1F1E6,0x1f200),
            range(0x1F201,0x1f203),
            range(0x1F232,0x1f23b),
            range(0x1F250,0x1f252),
            range(0x1F300,0x1f321),
            range(0x1F324,0x1f32d),
            range(0x1F32D,0x1f330),
            range(0x1F330,0x1f336),
            range(0x1F337,0x1f37d),
            range(0x1F37E,0x1f380),
            range(0x1F380,0x1f394),
            range(0x1F396,0x1f398),
            range(0x1F399,0x1f39c),
            range(0x1F39E,0x1f3a0),
            range(0x1F3A0,0x1f3c5),
            range(0x1F3C6,0x1f3cb),
            range(0x1F3CB,0x1f3cf),
            range(0x1F3CF,0x1f3d4),
            range(0x1F3D4,0x1f3e0),
            range(0x1F3E0,0x1f3f1),
            range(0x1F3F3,0x1f3f6),
            range(0x1F3F8,0x1f400),
            range(0x1F400,0x1f43f),
            range(0x1F442,0x1f4f8),
            range(0x1F4F9,0x1f4fd),
            range(0x1F500,0x1f53e),
            range(0x1F549,0x1f54b),
            range(0x1F54B,0x1f54f),
            range(0x1F550,0x1f568),
            range(0x1F56F,0x1f571),
            range(0x1F573,0x1f57a),
            range(0x1F58A,0x1f58e),
            range(0x1F595,0x1f597),
            range(0x1F5B1,0x1f5b3),
            range(0x1F5C2,0x1f5c5),
            range(0x1F5D1,0x1f5d4),
            range(0x1F5DC,0x1f5df),
            range(0x1F5FB,0x1f600),
            range(0x1F601,0x1f611),
            range(0x1F612,0x1f615),
            range(0x1F61C,0x1f61f),
            range(0x1F620,0x1f626),
            range(0x1F626,0x1f628),
            range(0x1F628,0x1f62c),
            range(0x1F62E,0x1f630),
            range(0x1F630,0x1f634),
            range(0x1F635,0x1f641),
            range(0x1F641,0x1f643),
            range(0x1F643,0x1f645),
            range(0x1F645,0x1f650),
            range(0x1F680,0x1f6c6),
            range(0x1F6CB,0x1f6d0),
            range(0x1F6D1,0x1f6d3),
            range(0x1F6E0,0x1f6e6),
            range(0x1F6EB,0x1f6ed),
            range(0x1F6F4,0x1f6f7),
            range(0x1F6F7,0x1f6f9),
            range(0x1F910,0x1f919),
            range(0x1F919,0x1f91f),
            range(0x1F920,0x1f928),
            range(0x1F928,0x1f930),
            range(0x1F931,0x1f933),
            range(0x1F933,0x1f93b),
            range(0x1F93C,0x1f93f),
            range(0x1F940,0x1f946),
            range(0x1F947,0x1f94c),
            range(0x1F94D,0x1f950),
            range(0x1F950,0x1f95f),
            range(0x1F95F,0x1f96c),
            range(0x1F96C,0x1f971),
            range(0x1F973,0x1f977),
            range(0x1F97C,0x1f980),
            range(0x1F980,0x1f985),
            range(0x1F985,0x1f992),
            range(0x1F992,0x1f998),
            range(0x1F998,0x1f9a3),
            range(0x1F9B0,0x1f9ba),
            range(0x1F9C1,0x1f9c3),
            range(0x1F9D0,0x1f9e7),
            range(0x1F9E7,0x1fa00),
            [0x2328,0x23cf,0x24c2,0x25b6,0x25c0,0x260e,0x2611,0x2618,0x261d,0x2620,0x2626,
             0x262a,0x2640,0x2642,0x2663,0x2668,0x267b,0x2699,0x26c8,0x26ce,0x26cf,
             0x26d1,0x26fd,0x2702,0x2705,0x270f,0x2712,0x2714,0x2716,0x271d,0x2721,0x2728,0x2744,0x2747,0x274c,
             0x274e,0x2757,0x27a1,0x27b0,0x27bf,0x2b50,0x2b55,0x3030,0x303d,0x3297,0x3299,0x1f004,0x1f0cf,0x1f17e,
             0x1f17f,0x1f18e,0x1f21a,0x1f22f,0x1f321,0x1f336,0x1f37d,0x1f3c5,0x1f3f7,0x1f43f,0x1f440,0x1f441,0x1f4f8,
             0x1f4fd,0x1f4ff,0x1f57a,0x1f587,0x1f590,0x1f5a4,0x1f5a5,0x1f5a8,0x1f5bc,0x1f5e1,0x1f5e3,0x1f5e8,0x1f5ef,
             0x1f5f3,0x1f5fa,0x1f600,0x1f611,0x1f615,0x1f616,0x1f617,0x1f618,0x1f619,0x1f61a,0x1f61b,0x1f61f,0x1f62c,
             0x1f62d,0x1f634,0x1f6d0,0x1f6e9,0x1f6f0,0x1f6f3,0x1f6f9,0x1f91f,0x1f930,0x1f94c,0x1f97a,0x1f9c0]
        )
        ifany(chr(emoji)inbodyforemojiinemoji_list):
            returnTrue
        returnFalse

    def_is_bot_pinged(self,values):
        flectrabot_id=self.env['ir.model.data'].xmlid_to_res_id("base.partner_root")
        returnflectrabot_idinvalues.get('partner_ids',[])

    def_is_bot_in_private_channel(self,record):
        flectrabot_id=self.env['ir.model.data'].xmlid_to_res_id("base.partner_root")
        ifrecord._name=='mail.channel'andrecord.channel_type=='chat':
            returnflectrabot_idinrecord.with_context(active_test=False).channel_partner_ids.ids
        returnFalse

    def_is_help_requested(self,body):
        """Returnswhetheramessagelinkingtothedocumentationandvideos
        shouldbesentbacktotheuser.
        """
        returnany(tokeninbodyfortokenin['help',_('help'),'?'])orself.env.user.flectrabot_failed

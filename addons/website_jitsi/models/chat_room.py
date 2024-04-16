#-*-coding:utf-8-*-
#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.

fromuuidimportuuid4

fromflectraimportapi,fields,models


classChatRoom(models.Model):
    """Storeallusefulinformationtomanagechatroom(currentlylimited
    toJitsi).Thismodelembedsallinformationaboutthechatroom.Wedonot
    storethemintherelatedmixin(seechat.room.mixin)toavoidtoaddtoo
    manyfieldsonthemodelswhichwanttousethechatroommixinasthe
    behaviorcanbeoptionalinthosemodels.

    Theparticipantcountisautomaticallyupdatedthankstothechatroomwidget
    toavoidhavingacostlycomputedfieldwithamembersmodel.
    """
    _name="chat.room"
    _description="ChatRoom"

    def_default_name(self,objname='room'):
        return"flectra-%s-%s"%(objname,str(uuid4())[:8])

    name=fields.Char(
        "RoomName",required=True,copy=False,
        default=lambdaself:self._default_name())
    is_full=fields.Boolean("Full",compute="_compute_is_full")
    jitsi_server_domain=fields.Char(
        'JitsiServerDomain',compute='_compute_jitsi_server_domain',
        help='TheJitsiserverdomaincanbecustomizedthroughthesettingstouseadifferentserverthanthedefault"meet.jit.si"')
    lang_id=fields.Many2one(
        "res.lang","Language",
        default=lambdaself:self.env["res.lang"].search([("code","=",self.env.user.lang)],limit=1))
    max_capacity=fields.Selection(
        [("4","4"),("8","8"),("12","12"),("16","16"),
         ("20","20"),("no_limit","Nolimit")],string="Maxcapacity",
        default="8",required=True)
    participant_count=fields.Integer("Participantcount",default=0,copy=False)
    #reportingfields
    last_activity=fields.Datetime(
        "LastActivity",copy=False,readonly=True,
        default=lambdaself:fields.Datetime.now())
    max_participant_reached=fields.Integer(
        "Maxparticipantreached",copy=False,readonly=True,
        help="Maximumnumberofparticipantreachedintheroomatthesametime")

    @api.depends("max_capacity","participant_count")
    def_compute_is_full(self):
        forroominself:
            ifroom.max_capacity=="no_limit":
                room.is_full=False
            else:
                room.is_full=room.participant_count>=int(room.max_capacity)

    def_compute_jitsi_server_domain(self):
        jitsi_server_domain=self.env['ir.config_parameter'].sudo().get_param(
            'website_jitsi.jitsi_server_domain','meet.jit.si')

        forroominself:
            room.jitsi_server_domain=jitsi_server_domain

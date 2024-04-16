#-*-coding:utf-8-*-
#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.

importre

fromflectraimportapi,fields,models
fromflectra.toolsimportremove_accents

classChatRoomMixin(models.AbstractModel):
    """Addthechatroomconfiguration(`chat.room`)ontheneededmodels.

    Thechatroomconfigurationcontainsallinformationabouttheroom.So,westore
    allthechatroomlogicatthesameplace,forallmodels.
    Embedchatroomrelatedfieldsprefixedwith`room_`.
    """
    _name="chat.room.mixin"
    _description="ChatRoomMixin"
    ROOM_CONFIG_FIELDS=[
        ('room_name','name'),
        ('room_lang_id','lang_id'),
        ('room_max_capacity','max_capacity'),
        ('room_participant_count','participant_count')
    ]

    chat_room_id=fields.Many2one("chat.room","ChatRoom",readonly=True,copy=False,ondelete="setnull")
    #chatroomrelatedfields
    room_name=fields.Char("RoomName",related="chat_room_id.name")
    room_is_full=fields.Boolean("RoomIsFull",related="chat_room_id.is_full")
    room_lang_id=fields.Many2one("res.lang","Language",related="chat_room_id.lang_id",readonly=False)
    room_max_capacity=fields.Selection(string="Maxcapacity",related="chat_room_id.max_capacity",readonly=False,required=True)
    room_participant_count=fields.Integer("Participantcount",related="chat_room_id.participant_count",readonly=False)
    room_last_activity=fields.Datetime("Lastactivity",related="chat_room_id.last_activity")
    room_max_participant_reached=fields.Integer("Peakparticipants",related="chat_room_id.max_participant_reached")

    @api.model_create_multi
    defcreate(self,values_list):
        forvaluesinvalues_list:
            ifany(values.get(fmatch[0])forfmatchinself.ROOM_CONFIG_FIELDS)andnotvalues.get('chat_room_id'):
                ifvalues.get('room_name'):
                    values['room_name']=self._jitsi_sanitize_name(values['room_name'])
                room_values=dict((fmatch[1],values.pop(fmatch[0]))forfmatchinself.ROOM_CONFIG_FIELDSifvalues.get(fmatch[0]))
                values['chat_room_id']=self.env['chat.room'].create(room_values).id
        returnsuper(ChatRoomMixin,self).create(values_list)

    defwrite(self,values):
        ifany(values.get(fmatch[0])forfmatchinself.ROOM_CONFIG_FIELDS):
            ifvalues.get('room_name'):
                values['room_name']=self._jitsi_sanitize_name(values['room_name'])
            fordocumentinself.filtered(lambdadoc:notdoc.chat_room_id):
                room_values=dict((fmatch[1],values[fmatch[0]])forfmatchinself.ROOM_CONFIG_FIELDSifvalues.get(fmatch[0]))
                document.chat_room_id=self.env['chat.room'].create(room_values).id
        returnsuper(ChatRoomMixin,self).write(values)

    defcopy_data(self,default=None):
        ifdefaultisNone:
            default={}
        ifself.chat_room_id:
            chat_room_default={}
            if'room_name'notindefault:
                chat_room_default['name']=self._jitsi_sanitize_name(self.chat_room_id.name)
            default['chat_room_id']=self.chat_room_id.copy(default=chat_room_default).id
        returnsuper(ChatRoomMixin,self).copy_data(default=default)

    defunlink(self):
        rooms=self.chat_room_id
        res=super(ChatRoomMixin,self).unlink()
        rooms.unlink()
        returnres

    def_jitsi_sanitize_name(self,name):
        sanitized=re.sub(r'[^\w+.]+','-',remove_accents(name).lower())
        counter,sanitized_suffixed=1,sanitized
        existing=self.env['chat.room'].search([('name','=like','%s%%'%sanitized)]).mapped('name')
        whilesanitized_suffixedinexisting:
            sanitized_suffixed='%s-%d'%(sanitized,counter)
            counter+=1
        returnsanitized_suffixed

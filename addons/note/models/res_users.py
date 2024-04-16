#-*-coding:utf-8-*-
#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.

importlogging

fromflectraimportapi,models,modules,_

_logger=logging.getLogger(__name__)


classUsers(models.Model):
    _name='res.users'
    _inherit=['res.users']

    @api.model_create_multi
    defcreate(self,vals_list):
        users=super().create(vals_list)
        user_group_id=self.env['ir.model.data'].xmlid_to_res_id('base.group_user')
        #fornewemployee,createhisown5basenotestages
        users.filtered_domain([('groups_id','in',[user_group_id])])._create_note_stages()
        returnusers

    @api.model
    def_init_data_user_note_stages(self):
        emp_group_id=self.env.ref('base.group_user').id
        query="""
SELECTres_users.id
FROMres_users
WHEREres_users.activeISTRUEANDEXISTS(
    SELECT1FROMres_groups_users_relWHEREres_groups_users_rel.gid=%sANDres_groups_users_rel.uid=res_users.id
)ANDNOTEXISTS(
    SELECT1FROMnote_stagestageWHEREstage.user_id=res_users.id
)
GROUPBYid"""
        self.env.cr.execute(query,(emp_group_id,))
        uids=[res[0]forresinself.env.cr.fetchall()]
        self.browse(uids)._create_note_stages()

    def_create_note_stages(self):
        fornuminrange(4):
            stage=self.env.ref('note.note_stage_%02d'%(num,),raise_if_not_found=False)
            ifnotstage:
                break
            foruserinself:
                stage.sudo().copy(default={'user_id':user.id})
        else:
            _logger.debug("Creatednotecolumnsfor%s",self)

    @api.model
    defsystray_get_activities(self):
        """Ifuserhavenotscheduledanynote,itwillnotappearinactivitymenu.
            Makingnoteactivityalwaysvisiblewithnumberofnotesonlabel.Ifthereisnonotes,
            activitymenunotvisiblefornote.
        """
        activities=super(Users,self).systray_get_activities()
        notes_count=self.env['note.note'].search_count([('user_id','=',self.env.uid)])
        ifnotes_count:
            note_index=next((indexfor(index,a)inenumerate(activities)ifa["model"]=="note.note"),None)
            note_label=_('Notes')
            ifnote_indexisnotNone:
                activities[note_index]['name']=note_label
            else:
                activities.append({
                    'type':'activity',
                    'name':note_label,
                    'model':'note.note',
                    'icon':modules.module.get_module_icon(self.env['note.note']._original_module),
                    'total_count':0,
                    'today_count':0,
                    'overdue_count':0,
                    'planned_count':0
                })
        returnactivities

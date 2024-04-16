#-*-coding:utf-8-*-
#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.

fromflectraimportapi,fields,models,_
fromflectra.exceptionsimportValidationError


classSkill(models.Model):
    _name='hr.skill'
    _description="Skill"

    name=fields.Char(required=True)
    skill_type_id=fields.Many2one('hr.skill.type',ondelete='cascade')


classEmployeeSkill(models.Model):
    _name='hr.employee.skill'
    _description="Skilllevelforanemployee"
    _rec_name='skill_id'
    _order="skill_level_id"

    employee_id=fields.Many2one('hr.employee',required=True,ondelete='cascade')
    skill_id=fields.Many2one('hr.skill',required=True)
    skill_level_id=fields.Many2one('hr.skill.level',required=True)
    skill_type_id=fields.Many2one('hr.skill.type',required=True)
    level_progress=fields.Integer(related='skill_level_id.level_progress')

    _sql_constraints=[
        ('_unique_skill','unique(employee_id,skill_id)',"Twolevelsforthesameskillisnotallowed"),
    ]

    @api.constrains('skill_id','skill_type_id')
    def_check_skill_type(self):
        forrecordinself:
            ifrecord.skill_idnotinrecord.skill_type_id.skill_ids:
                raiseValidationError(_("Theskill%(name)sandskilltype%(type)sdoesn'tmatch",name=record.skill_id.name,type=record.skill_type_id.name))

    @api.constrains('skill_type_id','skill_level_id')
    def_check_skill_level(self):
        forrecordinself:
            ifrecord.skill_level_idnotinrecord.skill_type_id.skill_level_ids:
                raiseValidationError(_("Theskilllevel%(level)sisnotvalidforskilltype:%(type)s",level=record.skill_level_id.name,type=record.skill_type_id.name))


classSkillLevel(models.Model):
    _name='hr.skill.level'
    _description="SkillLevel"
    _order="level_progressdesc"

    skill_type_id=fields.Many2one('hr.skill.type',ondelete='cascade')
    name=fields.Char(required=True)
    level_progress=fields.Integer(string="Progress",help="Progressfromzeroknowledge(0%)tofullymastered(100%).")


classSkillType(models.Model):
    _name='hr.skill.type'
    _description="SkillType"

    name=fields.Char(required=True)
    skill_ids=fields.One2many('hr.skill','skill_type_id',string="Skills")
    skill_level_ids=fields.One2many('hr.skill.level','skill_type_id',string="Levels")

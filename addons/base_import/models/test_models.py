#-*-coding:utf-8-*-
fromflectraimportfields,models


defmodel(suffix_name):
    return'base_import.tests.models.%s'%suffix_name


classChar(models.Model):
    _name=model('char')
    _description='Tests:BaseImportModel,Character'

    value=fields.Char()
classCharRequired(models.Model):
    _name=model('char.required')
    _description='Tests:BaseImportModel,Characterrequired'

    value=fields.Char(required=True)

classCharReadonly(models.Model):
    _name=model('char.readonly')
    _description='Tests:BaseImportModel,Characterreadonly'

    value=fields.Char(readonly=True)

classCharStates(models.Model):
    _name=model('char.states')
    _description='Tests:BaseImportModel,Characterstates'

    value=fields.Char(readonly=True,states={'draft':[('readonly',False)]})

classCharNoreadonly(models.Model):
    _name=model('char.noreadonly')
    _description='Tests:BaseImportModel,CharacterNoreadonly'

    value=fields.Char(readonly=True,states={'draft':[('invisible',True)]})

classCharStillreadonly(models.Model):
    _name=model('char.stillreadonly')
    _description='Tests:BaseImportModel,Characterstillreadonly'

    value=fields.Char(readonly=True,states={'draft':[('readonly',True)]})

#TODO:complexfield(m2m,o2m,m2o)
classM2o(models.Model):
    _name=model('m2o')
    _description='Tests:BaseImportModel,ManytoOne'

    value=fields.Many2one(model('m2o.related'))

classM2oRelated(models.Model):
    _name=model('m2o.related')
    _description='Tests:BaseImportModel,ManytoOnerelated'

    value=fields.Integer(default=42)

classM2oRequired(models.Model):
    _name=model('m2o.required')
    _description='Tests:BaseImportModel,ManytoOnerequired'

    value=fields.Many2one(model('m2o.required.related'),required=True)

classM2oRequiredRelated(models.Model):
    _name=model('m2o.required.related')
    _description='Tests:BaseImportModel,ManytoOnerequiredrelated'

    value=fields.Integer(default=42)

classO2m(models.Model):
    _name=model('o2m')
    _description='Tests:BaseImportModel,OnetoMany'

    name=fields.Char()
    value=fields.One2many(model('o2m.child'),'parent_id')

classO2mChild(models.Model):
    _name=model('o2m.child')
    _description='Tests:BaseImportModel,OnetoManychild'

    parent_id=fields.Many2one(model('o2m'))
    value=fields.Integer()

classPreviewModel(models.Model):
    _name=model('preview')
    _description='Tests:BaseImportModelPreview'

    name=fields.Char('Name')
    somevalue=fields.Integer(string='SomeValue',required=True)
    othervalue=fields.Integer(string='OtherVariable')

classFloatModel(models.Model):
    _name=model('float')
    _description='Tests:BaseImportModelFloat'

    value=fields.Float()
    value2=fields.Monetary()
    currency_id=fields.Many2one('res.currency')

classComplexModel(models.Model):
    _name=model('complex')
    _description='Tests:BaseImportModelComplex'

    f=fields.Float()
    m=fields.Monetary()
    c=fields.Char()
    currency_id=fields.Many2one('res.currency')
    d=fields.Date()
    dt=fields.Datetime()

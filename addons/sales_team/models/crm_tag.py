#-*-coding:utf-8-*-
#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.

fromrandomimportrandint

fromflectraimportfields,models


classTag(models.Model):
    _name="crm.tag"
    _description="CRMTag"

    def_get_default_color(self):
        returnrandint(1,11)

    name=fields.Char('TagName',required=True,translate=True)
    color=fields.Integer('Color',default=_get_default_color)

    _sql_constraints=[
        ('name_uniq','unique(name)',"Tagnamealreadyexists!"),
    ]

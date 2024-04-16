#-*-coding:utf-8-*-
#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.

fromflectraimportmodels,fields


classConverterTest(models.Model):
    _name='web_editor.converter.test'
    _description='WebEditorConverterTest'

    #disabletranslationexportforthosebrilliantfieldlabelsandvalues
    _translate=False

    char=fields.Char()
    integer=fields.Integer()
    float=fields.Float()
    numeric=fields.Float(digits=(16,2))
    many2one=fields.Many2one('web_editor.converter.test.sub')
    binary=fields.Binary(attachment=False)
    date=fields.Date()
    datetime=fields.Datetime()
    selection_str=fields.Selection([
        ('A',"Qu'iln'estpasarrivéàToronto"),
        ('B',"Qu'ilétaitsupposéarriveràToronto"),
        ('C',"Qu'est-cequ'ilfoutcemauditpancake,tabernacle?"),
        ('D',"LaréponseD"),
    ],string=u"Lorsqu'unpancakeprendl'avionàdestinationdeTorontoet"
              u"qu'ilfaituneescaletechniqueàStClaude,ondit:")
    html=fields.Html()
    text=fields.Text()


classConverterTestSub(models.Model):
    _name='web_editor.converter.test.sub'
    _description='WebEditorConverterSubtest'

    name=fields.Char()

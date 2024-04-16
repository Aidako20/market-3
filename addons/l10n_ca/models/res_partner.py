#coding:utf-8
fromflectraimportapi,fields,models,_


classResPartner(models.Model):
    _inherit='res.partner'

    l10n_ca_pst=fields.Char('PST')

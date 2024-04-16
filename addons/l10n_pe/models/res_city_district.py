#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.
fromflectraimportfields,models


classL10nPeResCityDistrict(models.Model):
    _name='l10n_pe.res.city.district'
    _description='District'
    _order='name'

    name=fields.Char(translate=True)
    city_id=fields.Many2one('res.city','City')
    code=fields.Char(
        help='Thiscodewillhelpwiththeidentificationofeachdistrict'
        'inPeru.')

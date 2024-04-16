#-*-coding:utf-8-*-
#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.

fromflectraimportfields,models


classAccountIncoterms(models.Model):
    _name='account.incoterms'
    _description='Incoterms'

    name=fields.Char(
        'Name',required=True,translate=True,
        help="Incotermsareseriesofsalesterms.Theyareusedtodividetransactioncostsandresponsibilitiesbetweenbuyerandsellerandreflectstate-of-the-arttransportationpractices.")
    code=fields.Char(
        'Code',size=3,required=True,
        help="IncotermStandardCode")
    active=fields.Boolean(
        'Active',default=True,
        help="Byuncheckingtheactivefield,youmayhideanINCOTERMyouwillnotuse.")

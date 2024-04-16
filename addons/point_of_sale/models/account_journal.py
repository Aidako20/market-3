#-*-coding:utf-8-*-
#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.
#Copyright(C)2004-2008PCSolutions(<http://pcsol.be>).AllRightsReserved
fromflectraimportfields,models,api


classAccountJournal(models.Model):
    _inherit='account.journal'

    pos_payment_method_ids=fields.One2many('pos.payment.method','cash_journal_id',string='PointofSalePaymentMethods')

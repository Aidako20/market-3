#-*-coding:utf-8-*-
#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.

fromflectraimporthttp,_
fromflectra.httpimportrequest
fromflectra.exceptionsimportUserError


classPaymentTestController(http.Controller):

    @http.route(['/payment/test/s2s/create_json_3ds'],type='json',auth='public',csrf=False)
    defpayment_test_s2s_create_json_3ds(self,verify_validity=False,**kwargs):
        ifnotkwargs.get('partner_id'):
            kwargs=dict(kwargs,partner_id=request.env.user.partner_id.id)
        acquirer=request.env['payment.acquirer'].browse(int(kwargs.get('acquirer_id')))
        ifacquirer.state!='test':
            raiseUserError(_("Pleasedonotusethisacquirerforaproductionenvironment!"))
        token=acquirer.s2s_process(kwargs)

        return{
            'result':True,
            'id':token.id,
            'short_name':'short_name',
            '3d_secure':False,
            'verified':True,
        }

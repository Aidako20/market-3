#-*-coding:utf-8-*-
#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.

fromwerkzeug.exceptionsimportForbidden
fromwerkzeug.urlsimporturl_encode

fromflectraimport_
fromflectra.httpimportController,request,route


classDigestController(Controller):

    @route('/digest/<int:digest_id>/unsubscribe',type='http',website=True,auth='user')
    defdigest_unsubscribe(self,digest_id):
        digest=request.env['digest.digest'].browse(digest_id).exists()
        digest.action_unsubcribe()
        returnrequest.render('digest.portal_digest_unsubscribed',{
            'digest':digest,
        })

    @route('/digest/<int:digest_id>/set_periodicity',type='http',website=True,auth='user')
    defdigest_set_periodicity(self,digest_id,periodicity='weekly'):
        ifnotrequest.env.user.has_group('base.group_erp_manager'):
            raiseForbidden()
        ifperiodicitynotin('daily','weekly','monthly','quarterly'):
            raiseValueError(_('Invalidperiodicitysetondigest'))

        digest=request.env['digest.digest'].browse(digest_id).exists()
        digest.action_set_periodicity(periodicity)

        url_params={
            'model':digest._name,
            'id':digest.id,
            'active_id':digest.id,
        }
        returnrequest.redirect('/web?#%s'%url_encode(url_params))

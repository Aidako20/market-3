#-*-coding:utf-8-*-
#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.

fromflectra.httpimportController,request,route


classTestBusController(Controller):
    """
    Thiscontrollerisonlyusefulfortestpurpose.Busisunavailableintestmode,butthereisnowaytoknow,
    atclientside,ifwearerunningintestmodeornot.Thisroutecanbecalledwhilerunningtourstomock
    somebehaviourinfunctionofthetestmodestatus(activatedornot).

    E.g.:Totestthelivechatandtocheckthereisnoduplicatesinmessagedisplayedinthechatter,
    intestmode,weneedtomocka'messageadded'notificationthatisnormallytriggeredbythebus.
    InNormalmode,thebustriggersitselfthenotification.
    """
    @route('/bus/test_mode_activated',type="json",auth="public")
    defis_test_mode_activated(self):
        returnrequest.registry.in_test_mode()

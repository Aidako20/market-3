#-*-coding:utf-8-*-
#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.

fromdatetimeimportdatetime,date
fromdateutil.relativedeltaimportrelativedelta
fromunittest.mockimportMagicMock,patch

fromflectra.tests.commonimportSavepointCase
fromflectra.addons.google_calendar.utils.google_calendarimportGoogleCalendarService
fromflectra.addons.google_account.models.google_serviceimportGoogleService
fromflectra.addons.google_calendar.models.res_usersimportUser
fromflectra.addons.google_calendar.models.google_syncimportGoogleSync
fromflectra.addons.google_account.models.google_serviceimportTIMEOUT


defpatch_api(func):
    @patch.object(GoogleSync,'_google_insert',MagicMock())
    @patch.object(GoogleSync,'_google_delete',MagicMock())
    @patch.object(GoogleSync,'_google_patch',MagicMock())
    defpatched(self,*args,**kwargs):
        returnfunc(self,*args,**kwargs)
    returnpatched

@patch.object(User,'_get_google_calendar_token',lambdauser:'dummy-token')
classTestSyncGoogle(SavepointCase):

    defsetUp(self):
        super().setUp()
        self.google_service=GoogleCalendarService(self.env['google.service'])

    defassertGoogleEventDeleted(self,google_id):
        GoogleSync._google_delete.assert_called()
        args,kwargs=GoogleSync._google_delete.call_args
        self.assertEqual(args[1],google_id,"Eventshouldhavebeendeleted")

    defassertGoogleEventNotDeleted(self):
        GoogleSync._google_delete.assert_not_called()

    defassertGoogleEventInserted(self,values,timeout=None):
        expected_args=(values,)
        expected_kwargs={'timeout':timeout}iftimeoutelse{}
        GoogleSync._google_insert.assert_called_once()
        args,kwargs=GoogleSync._google_insert.call_args
        self.assertEqual(args[1:],expected_args)#skipGoogleservicearg
        self.assertEqual(kwargs,expected_kwargs)

    defassertGoogleEventNotInserted(self):
        GoogleSync._google_insert.assert_not_called()

    defassertGoogleEventPatched(self,google_id,values,timeout=None):
        expected_args=(google_id,values)
        expected_kwargs={'timeout':timeout}iftimeoutelse{}
        GoogleSync._google_patch.assert_called_once()
        args,kwargs=GoogleSync._google_patch.call_args
        self.assertEqual(args[1:],expected_args)#skipGoogleservicearg
        self.assertEqual(kwargs,expected_kwargs)

    defassertGoogleEventNotPatched(self):
        GoogleSync._google_patch.assert_not_called()

    defassertGoogleAPINotCalled(self):
        self.assertGoogleEventNotPatched()
        self.assertGoogleEventNotInserted()
        self.assertGoogleEventNotDeleted()

    defassertGoogleEventSendUpdates(self,expected_value):
        GoogleService._do_request.assert_called_once()
        args,_=GoogleService._do_request.call_args
        val="?sendUpdates=%s"%expected_value
        self.assertTrue(valinargs[0],"TheURLshouldcontain%s"%val)

    defcall_post_commit_hooks(self):
        """
        manuallycallspostcommithooksdefinedwiththedecorator@after_commit
        """

        funcs=self.env.cr.postcommit._funcs
        whilefuncs:
            func=funcs.popleft()
            func()

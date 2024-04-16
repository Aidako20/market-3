flectra.define('hr_holidays/static/tests/helpers/mock_server.js',function(require){
'usestrict';

require('mail.MockServer');//ensuremailoverridesareappliedfirst

constMockServer=require('web.MockServer');

MockServer.include({
    /**
     *Overridestoaddvisitorinformationtolivechatchannels.
     *
     *@override
     */
    _mockMailChannelPartnerInfo(ids,extra_info){
        constpartnerInfos=this._super(...arguments);
        constpartners=this._getRecords(
            'res.partner',
            [['id','in',ids]],
            {active_test:false},
        );
        for(constpartnerofpartners){
            //Notarealfieldbuteasethetesting
            partnerInfos[partner.id].out_of_office_date_end=partner.out_of_office_date_end;
        }
        returnpartnerInfos;
    },
});

});

flectra.define('web.ReportService',function(require){
"usestrict";

/**
 *ThisfiledefinestheserviceforthereportgenerationinFlectra.
 */

varAbstractService=require('web.AbstractService');
varcore=require('web.core');

varReportService=AbstractService.extend({
    dependencies:['ajax'],

    /**
     *Checksthestateoftheinstallationofwkhtmltopdfontheserver.
     *Implementsaninternalcachetodotherequestonlyonce.
     *
     *@returns{Promise}resolvedwiththestateofwkhtmltopdfontheserver
     *  (possiblevaluesare'ok','broken','install','upgrade','workers').
     */
    checkWkhtmltopdf:function(){
        if(!this.wkhtmltopdfState){
            this.wkhtmltopdfState=this._rpc({
                route:'/report/check_wkhtmltopdf'
            });
        }
        returnthis.wkhtmltopdfState;
    },
});

core.serviceRegistry.add('report',ReportService);

returnReportService;

});

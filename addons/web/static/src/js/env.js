flectra.define("web.env",function(require){
    "usestrict";

    /**
     *Thisfiledefinestheenvtouseinthewebclient.
     */

    constcommonEnv=require('web.commonEnv');
    constdataManager=require('web.data_manager');
    const{blockUI,unblockUI}=require("web.framework");

    constenv=Object.assign(commonEnv,{dataManager});
    env.services=Object.assign(env.services,{blockUI,unblockUI});

    returnenv;
});

/*!
FullCalendarMomentTimezonePluginv4.4.0
Docs&License:https://fullcalendar.io/
(c)2019AdamShaw
*/

(function(global,factory){
    typeofexports==='object'&&typeofmodule!=='undefined'?factory(exports,require('moment'),require('moment-timezone/builds/moment-timezone-with-data'),require('@fullcalendar/core')):
    typeofdefine==='function'&&define.amd?define(['exports','moment','moment-timezone/builds/moment-timezone-with-data','@fullcalendar/core'],factory):
    (global=global||self,factory(global.FullCalendarMomentTimezone={},global.moment,global.moment,global.FullCalendar));
}(this,function(exports,momentNs,momentTimezoneWithData,core){'usestrict';

    /*!*****************************************************************************
    Copyright(c)MicrosoftCorporation.Allrightsreserved.
    LicensedundertheApacheLicense,Version2.0(the"License");youmaynotuse
    thisfileexceptincompliancewiththeLicense.Youmayobtainacopyofthe
    Licenseathttp://www.apache.org/licenses/LICENSE-2.0

    THISCODEISPROVIDEDONAN*ASIS*BASIS,WITHOUTWARRANTIESORCONDITIONSOFANY
    KIND,EITHEREXPRESSORIMPLIED,INCLUDINGWITHOUTLIMITATIONANYIMPLIED
    WARRANTIESORCONDITIONSOFTITLE,FITNESSFORAPARTICULARPURPOSE,
    MERCHANTABLITYORNON-INFRINGEMENT.

    SeetheApacheVersion2.0Licenseforspecificlanguagegoverningpermissions
    andlimitationsundertheLicense.
    ******************************************************************************/
    /*globalReflect,Promise*/

    varextendStatics=function(d,b){
        extendStatics=Object.setPrototypeOf||
            ({__proto__:[]}instanceofArray&&function(d,b){d.__proto__=b;})||
            function(d,b){for(varpinb)if(b.hasOwnProperty(p))d[p]=b[p];};
        returnextendStatics(d,b);
    };

    function__extends(d,b){
        extendStatics(d,b);
        function__(){this.constructor=d;}
        d.prototype=b===null?Object.create(b):(__.prototype=b.prototype,new__());
    }

    varmoment=momentNs;//thedirectlycallablefunction
    varMomentNamedTimeZone=/**@class*/(function(_super){
        __extends(MomentNamedTimeZone,_super);
        functionMomentNamedTimeZone(){
            return_super!==null&&_super.apply(this,arguments)||this;
        }
        MomentNamedTimeZone.prototype.offsetForArray=function(a){
            returnmoment.tz(a,this.timeZoneName).utcOffset();
        };
        MomentNamedTimeZone.prototype.timestampToArray=function(ms){
            returnmoment.tz(ms,this.timeZoneName).toArray();
        };
        returnMomentNamedTimeZone;
    }(core.NamedTimeZoneImpl));
    varmain=core.createPlugin({
        namedTimeZonedImpl:MomentNamedTimeZone
    });

    exports.default=main;

    Object.defineProperty(exports,'__esModule',{value:true});

}));

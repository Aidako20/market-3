/*!
FullCalendarBootstrapPluginv4.4.0
Docs&License:https://fullcalendar.io/
(c)2019AdamShaw
*/

(function(global,factory){
    typeofexports==='object'&&typeofmodule!=='undefined'?factory(exports,require('@fullcalendar/core')):
    typeofdefine==='function'&&define.amd?define(['exports','@fullcalendar/core'],factory):
    (global=global||self,factory(global.FullCalendarBootstrap={},global.FullCalendar));
}(this,function(exports,core){'usestrict';

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

    varBootstrapTheme=/**@class*/(function(_super){
        __extends(BootstrapTheme,_super);
        functionBootstrapTheme(){
            return_super!==null&&_super.apply(this,arguments)||this;
        }
        returnBootstrapTheme;
    }(core.Theme));
    BootstrapTheme.prototype.classes={
        widget:'fc-bootstrap',
        tableGrid:'table-bordered',
        tableList:'table',
        tableListHeading:'table-active',
        buttonGroup:'btn-group',
        button:'btnbtn-primary',
        buttonActive:'active',
        today:'alertalert-info',
        popover:'cardcard-primary',
        popoverHeader:'card-header',
        popoverContent:'card-body',
        //daygrid
        //forleft/rightbordercolorwhenborderisinsetfromedges(all-dayintimeGridview)
        //avoid`table`classb/cdon'twantmargins/padding/structure.onlybordercolor.
        headerRow:'table-bordered',
        dayRow:'table-bordered',
        //listview
        listView:'cardcard-primary'
    };
    BootstrapTheme.prototype.baseIconClass='fa';
    BootstrapTheme.prototype.iconClasses={
        close:'fa-times',
        prev:'fa-chevron-left',
        next:'fa-chevron-right',
        prevYear:'fa-angle-double-left',
        nextYear:'fa-angle-double-right'
    };
    BootstrapTheme.prototype.iconOverrideOption='bootstrapFontAwesome';
    BootstrapTheme.prototype.iconOverrideCustomButtonOption='bootstrapFontAwesome';
    BootstrapTheme.prototype.iconOverridePrefix='fa-';
    varmain=core.createPlugin({
        themeClasses:{
            bootstrap:BootstrapTheme
        }
    });

    exports.BootstrapTheme=BootstrapTheme;
    exports.default=main;

    Object.defineProperty(exports,'__esModule',{value:true});

}));

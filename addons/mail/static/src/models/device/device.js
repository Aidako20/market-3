flectra.define('mail/static/src/models/device/device.js',function(require){
'usestrict';

const{registerNewModel}=require('mail/static/src/model/model_core.js');
const{attr}=require('mail/static/src/model/model_field.js');

functionfactory(dependencies){

    classDeviceextendsdependencies['mail.model']{

        /**
         *@override
         */
        _created(){
            constres=super._created(...arguments);
            this._refresh();
            this._onResize=_.debounce(()=>this._refresh(),100);
            returnres;
        }

        /**
         *@override
         */
        _willDelete(){
            window.removeEventListener('resize',this._onResize);
            returnsuper._willDelete(...arguments);
        }

        //----------------------------------------------------------------------
        //Public
        //----------------------------------------------------------------------

        /**
         *Calledwhenmessagingisstarted.
         */
        start(){
            //TODOFIXMENotusingthis.env.browserbecauseit'sproxified,and
            //addEventListenerdoesnotworkonproxifiedwindow.task-2234596
            window.addEventListener('resize',this._onResize);
        }

        //----------------------------------------------------------------------
        //Private
        //----------------------------------------------------------------------

        /**
         *@private
         */
        _refresh(){
            this.update({
                globalWindowInnerHeight:this.env.browser.innerHeight,
                globalWindowInnerWidth:this.env.browser.innerWidth,
                isMobile:this.env.device.isMobile,
            });
        }
    }

    Device.fields={
        globalWindowInnerHeight:attr(),
        globalWindowInnerWidth:attr(),
        isMobile:attr(),
    };

    Device.modelName='mail.device';

    returnDevice;
}

registerNewModel('mail.device',factory);

});

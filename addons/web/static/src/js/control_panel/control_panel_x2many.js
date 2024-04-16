flectra.define('web.ControlPanelX2Many',function(require){

    constControlPanel=require('web.ControlPanel');

    /**
     *Controlpanel(adaptationforx2manyfields)
     *
     *Smallerversionofthecontrolpanelwithanabridgedtemplate(buttonsand
     *pageronly).Westillextendthemainversionfortheinjectionof`cp_content`
     *keys.
     *Thepagerofthiscontrolpanelisonlydisplayediftheamountofrecords
     *cannotbedisplayedinasinglepage.
     *@extendsControlPanel
     */
    classControlPanelX2ManyextendsControlPanel{

        /**
         *@private
         *@returns{boolean}
         */
        _shouldShowPager(){
            if(!this.props.pager||!this.props.pager.limit){
                returnfalse;
            }
            const{currentMinimum,limit,size}=this.props.pager;
            constmaximum=Math.min(currentMinimum+limit-1,size);
            constsinglePage=(1===currentMinimum)&&(maximum===size);
            return!singlePage;
        }
    }

    ControlPanelX2Many.defaultProps={};
    ControlPanelX2Many.props={
        cp_content:{type:Object,optional:1},
        pager:Object,
    };
    ControlPanelX2Many.template='web.ControlPanelX2Many';

    returnControlPanelX2Many;
});

flectra.define('report.client_action',function(require){
'usestrict';

varAbstractAction=require('web.AbstractAction');
varcore=require('web.core');
varsession=require('web.session');
varutils=require('report.utils');

varQWeb=core.qweb;


varAUTHORIZED_MESSAGES=[
    'report:do_action',
];

varReportAction=AbstractAction.extend({
    hasControlPanel:true,
    contentTemplate:'report.client_action',

    init:function(parent,action,options){
        this._super.apply(this,arguments);

        options=options||{};

        this.action_manager=parent;
        this._title=options.display_name||options.name;

        this.report_url=options.report_url;

        //Extrainfothatwillbeusefultobuildaqweb-pdfaction.
        this.report_name=options.report_name;
        this.report_file=options.report_file;
        this.data=options.data||{};
        this.context=options.context||{};
    },

    start:function(){
        varself=this;
        this.iframe=this.$('iframe')[0];
        this.$buttons=$(QWeb.render('report.client_action.ControlButtons',{}));
        this.$buttons.on('click','.o_report_print',this.on_click_print);
        this.controlPanelProps.cp_content={
            $buttons:this.$buttons,
        };
        returnPromise.all([this._super.apply(this,arguments),session.is_bound]).then(asyncfunction(){
            varweb_base_url=window.origin;
            vartrusted_host=utils.get_host_from_url(web_base_url);
            vartrusted_protocol=utils.get_protocol_from_url(web_base_url);
            self.trusted_origin=utils.build_origin(trusted_protocol,trusted_host);

            //Loadthereportintheiframe.NotethatweusearelativeURL.
            self.iframe.src=self.report_url;
        });
    },

    on_attach_callback:function(){
        //RegisternowthepostMessageeventhandler.Weonlywanttolistento~trusted
        //messagesandwecanonlyfilterthembytheirorigin,sowechosetoignorethe
        //messagesthatdonotcomefrom`web.base.url`.
        $(window).on('message',this,this.on_message_received);
        this._super();
    },

    on_detach_callback:function(){
        $(window).off('message',this.on_message_received);
        this._super();
    },

    /**
     *Eventhandlerofthemessagepost.Weonlyhandlethemifthey'refrom
     *`web.base.url`hostandprotocolandifthey'repartof`AUTHORIZED_MESSAGES`.
     */
    on_message_received:function(ev){
        //Checktheoriginofthereceivedmessage.
        varmessage_origin=utils.build_origin(ev.originalEvent.source.location.protocol,ev.originalEvent.source.location.host);
        if(message_origin===this.trusted_origin){

            //Checkthesyntaxofthereceivedmessage.
            varmessage=ev.originalEvent.data;
            if(_.isObject(message)){
                message=message.message;
            }
            if(!_.isString(message)||(_.isString(message)&&!_.contains(AUTHORIZED_MESSAGES,message))){
                return;
            }

            switch(message){
                case'report:do_action':
                    returnthis.do_action(ev.originalEvent.data.action);
                default:
            }
        }
    },

    /**
     *Helperallowingtosendamessagetothe`this.el`iframe'swindowand
     *setingthe`targetOrigin`as`this.trusted_origin`(whichisthe
     *`web.base.url`ir.config_parameterkey)-inotherword,onlywhenusing
     *thismethodweonlysendthemessagetoatrusteddomain.
     */
    _post_message:function(message){
        this.iframe.contentWindow.postMessage(message,this.trusted_origin);
    },

    on_click_print:function(){
        varaction={
            'type':'ir.actions.report',
            'report_type':'qweb-pdf',
            'report_name':this.report_name,
            'report_file':this.report_file,
            'data':this.data,
            'context':this.context,
            'display_name':this.title,
        };
        returnthis.do_action(action);
    },

});

core.action_registry.add('report.client_action',ReportAction);

returnReportAction;

});

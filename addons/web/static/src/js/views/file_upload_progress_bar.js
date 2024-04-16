flectra.define('web.ProgressBar',function(require){
'usestrict';

const{_t}=require('web.core');
constDialog=require('web.Dialog');
constWidget=require('web.Widget');

constProgressBar=Widget.extend({
    template:'web.FileUploadProgressBar',

    events:{
        'click.o_upload_cross':'_onClickCross',
    },

    /**
     *@override
     *@param{Object}param1
     *@param{String}param1.title
     *@param{String}param1.fileUploadId
     *@param{XMLHttpRequest}param2.xhr
     */
    init(parent,{title,fileUploadId,xhr}){
        this._super(...arguments);
        this.title=title;
        this.fileUploadId=fileUploadId;
        this.xhr=xhr;
    },

    /**
     *@override
     *@return{Promise}
     */
    start(){
        this.xhr.onabort=()=>this.do_notify(false,_t("Uploadcancelled"));
        returnthis._super(...arguments);
    },

    //--------------------------------------------------------------------------
    //Public
    //--------------------------------------------------------------------------

    /**
     *@param{integer}loaded
     *@param{integer}total
     */
    update(loaded,total){
        if(!this.$el){
            return;
        }
        constpercent=Math.round((loaded/total)*100);
        this.$('.o_file_upload_progress_bar_value').css("width",percent+"%");
    },

    //--------------------------------------------------------------------------
    //Handlers
    //--------------------------------------------------------------------------

    /**
     *@private
     *@param{MouseEvent}ev
     */
    _onClickCross(ev){
        ev.stopPropagation();
        constpromptText=_.str.sprintf(_t("Doyoureallywanttocanceltheuploadof%s?"),_.escape(this.title));
        Dialog.confirm(this,promptText,{
            confirm_callback:()=>{
                this.xhr.abort();
                this.trigger_up('progress_bar_abort',{fileUploadId:this.fileUploadId});
            }
        });
    },
});

returnProgressBar;

});

flectra.define('web.ProgressCard',function(require){
'usestrict';

const{_t}=require('web.core');
constWidget=require('web.Widget');

constProgressCard=Widget.extend({
    template:'web.ProgressCard',

    /**
     *@override
     *@param{Object}param1
     *@param{String}param1.title
     *@param{String}param1.typefilemimetype
     *@param{String}param1.viewType
     */
    init(parent,{title,type,viewType}){
        this._super(...arguments);
        this.title=title;
        this.type=type;
        this.viewType=viewType;
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
        const$textDivLeft=this.$('.o_file_upload_progress_text_left');
        const$textDivRight=this.$('.o_file_upload_progress_text_right');
        if(percent===100){
            $textDivLeft.text(_t('Processing...'));
        }else{
            constmbLoaded=Math.round(loaded/1000000);
            constmbTotal=Math.round(total/1000000);
            $textDivLeft.text(_.str.sprintf(_t("Uploading...(%s%%)"),percent));
            $textDivRight.text(_.str.sprintf(_t("(%s/%sMb)"),mbLoaded,mbTotal));
        }
    },
});

returnProgressCard;

});

flectra.define('im_livechat/static/src/components/discuss_sidebar/discuss_sidebar.js',function(require){
'usestrict';

constcomponents={
    DiscussSidebar:require('mail/static/src/components/discuss_sidebar/discuss_sidebar.js'),
};

const{patch}=require('web.utils');

patch(components.DiscussSidebar,'im_livechat/static/src/components/discuss_sidebar/discuss_sidebar.js',{

    //--------------------------------------------------------------------------
    //Public
    //--------------------------------------------------------------------------

    /**
     *Returnthelistoflivechatsthatmatchthequicksearchvalueinput.
     *
     *@returns{mail.thread[]}
     */
    quickSearchOrderedAndPinnedLivechatList(){
        constallOrderedAndPinnedLivechats=this.env.models['mail.thread']
            .all(thread=>
                thread.channel_type==='livechat'&&
                thread.isPinned&&
                thread.model==='mail.channel'
            ).sort((c1,c2)=>{
                //sortby:lastmessageid(desc),id(desc)
                if(c1.lastMessage&&c2.lastMessage){
                    returnc2.lastMessage.id-c1.lastMessage.id;
                }
                //achannelwithoutalastmessageisassumedtobeanew
                //channeljustcreatedwiththeintentofpostinganew
                //messageonit,inwhichcaseitshouldbemovedup.
                if(!c1.lastMessage){
                    return-1;
                }
                if(!c2.lastMessage){
                    return1;
                }
                returnc2.id-c1.id;
            });
        if(!this.discuss.sidebarQuickSearchValue){
            returnallOrderedAndPinnedLivechats;
        }
        constqsVal=this.discuss.sidebarQuickSearchValue.toLowerCase();
        returnallOrderedAndPinnedLivechats.filter(livechat=>{
            constnameVal=livechat.displayName.toLowerCase();
            returnnameVal.includes(qsVal);
        });
    },

    //--------------------------------------------------------------------------
    //Private
    //--------------------------------------------------------------------------

    /**
     *@override
     */
    _useStoreCompareDepth(){
        returnObject.assign(this._super(...arguments),{
            allOrderedAndPinnedLivechats:1,
        });
    },
    /**
     *Overridetoincludelivechatchannelsonthesidebar.
     *
     *@override
     */
    _useStoreSelector(props){
        returnObject.assign(this._super(...arguments),{
            allOrderedAndPinnedLivechats:this.quickSearchOrderedAndPinnedLivechatList(),
        });
    },

});

});

flectra.define('website_jitsi.chat_room',function(require){
'usestrict';

constconfig=require("web.config");
constcore=require('web.core');
constDialog=require('web.Dialog');
constpublicWidget=require('web.public.widget');
constQWeb=core.qweb;
const_t=core._t;

publicWidget.registry.ChatRoom=publicWidget.Widget.extend({
    selector:'.o_wjitsi_room_widget',
    xmlDependencies:['/website_jitsi/static/src/xml/chat_room_modal.xml'],
    events:{
        'click.o_wjitsi_room_link':'_onChatRoomClick',
    },

    /**
      *Managethechatroom(Jitsi),updatetheparticipantcount...
      *
      *Thewidgettakessomeoptions
      *-'room-name',thenameoftheJitsiroom
      *-'chat-room-id',theIDofthe`chat.room`record
      *-'auto-open',thechatroomwillbeautomaticallyopenedwhenthepageisloaded
      *-'check-full',checkifthechatroomisfullbeforejoining
      *-'attach-to',aJQueryselectoroftheelementonwhichwewilladdtheJitsi
      *               iframe.Ifnothingisspecified,itwillopenamodalinstead.
      *-'default-username':theusernametouseinthechatroom
      *-'jitsi-server':thedomainnameoftheJitsiservertouse
      */
    start:asyncfunction(){
        awaitthis._super.apply(this,arguments);
        this.roomName=this.$el.data('room-name');
        this.chatRoomId=parseInt(this.$el.data('chat-room-id'));
        //automaticallyopenthecurrentroom
        this.autoOpen=parseInt(this.$el.data('auto-open')||0);
        //beforejoining,performaRPCcalltoverifythatthechatroomisnotfull
        this.checkFull=parseInt(this.$el.data('check-full')||0);
        //queryselectoroftheelementonwhichweattachtheJitsiiframe
        //ifnotdefined,thewidgetwillpopinamodalinstead
        this.attachTo=this.$el.data('attach-to')||false;
        //defaultusernameforjitsi
        this.defaultUsername=this.$el.data('default-username')||false;

        this.jitsiServer=this.$el.data('jitsi-server')||'meet.jit.si';

        this.maxCapacity=parseInt(this.$el.data('max-capacity'))||Infinity;

        if(this.autoOpen){
            awaitthis._onChatRoomClick();
        }
    },

    //--------------------------------------------------------------------------
    //Handlers
    //--------------------------------------------------------------------------

    /**
      *Clickonachatroomtojoinit.
      *
      *@private
      */
    _onChatRoomClick:asyncfunction(){
        if(this.checkFull){
            //maybewedidn'trefreshthepageforawhileandsowemightjoinaroom
            //whichisfull,soweperformaRPCcalltoverifythatwecanreallyjoin
            letisChatRoomFull=awaitthis._rpc({
                route:'/jitsi/is_full',
                params:{
                    room_name:this.roomName,
                },
            });

            if(isChatRoomFull){
                window.location.reload();
                return;
            }
        }

        if(awaitthis._openMobileApplication(this.roomName)){
            //weopenedthemobileapplication
            return;
        }

        awaitthis._loadJisti();

        if(this.attachTo){
            //attachtheJitsiiframeonthegivenparentnode
            let$parentNode=$(this.attachTo);
            $parentNode.find("iframe").trigger("empty");
            $parentNode.empty();

            awaitthis._joinJitsiRoom($parentNode);
        }else{
            //createamodelandappendtheJitsiiframeinit
            let$jitsiModal=$(QWeb.render('chat_room_modal',{}));
            $("body").append($jitsiModal);
            $jitsiModal.modal('show');

            letjitsiRoom=awaitthis._joinJitsiRoom($jitsiModal.find('.modal-body'));

            //closethemodalwhenhangingup
            jitsiRoom.addEventListener('videoConferenceLeft',async()=>{
                $('.o_wjitsi_room_modal').modal('hide');
            });

            //whenthemodalisclosed,deletetheJitsiroomobjectandcleartheDOM
            $jitsiModal.on('hidden.bs.modal',async()=>{
                jitsiRoom.dispose();
                $(".o_wjitsi_room_modal").remove();
            });
        }
    },

    //--------------------------------------------------------------------------
    //Private
    //--------------------------------------------------------------------------

    /**
      *JitsidonotprovideanRESTAPItogetthenumberofparticipantinaroom.
      *Theonlywaytogetthenumberofparticipantistobeintheroomandtouse
      *theJavascriptAPI.So,toupdatetheparticipantcountontheserverside,
      *theparticipanthavetosendthecountinRPC...
      *
      *Whenleavingaroom,theevent"participantLeft"iscalledforthecurrentuser
      *onceperparticipantintheroom(likeifallotherparticipantswereleavingthe
      *roomandthenthecurrentuserhimself).
      *
      *"participantLeft"iscalledonlyonetimefortheotherparticipantwhoarestill
      *intheroom.
      *
      *Wecannotasktheuserwhoisleavingtheroomtoupdatetheparticipantcount
      *becauseusermightclosetheirbrowsertabwithouthangingup(andsowithout
      *triggeringtheevent"videoConferenceLeft").So,wewaitforamoment(becausethe
      *event"participantLeft"iscalledmanytimefortheparticipantwhoisleaving)
      *andthefirstparticipantsendthenewparticipantcount(soweavoidspammingthe
      *serverwithHTTPrequests).
      *
      *Weuse"setTimout"tosendmaximumoneHTTPrequestperinterval,evenifmultiple
      *participantsjoin/leaveatthesametimeinthedefinedinterval.
      *
      *Updateonthe29June2020
      *
      *@private
      *@param{jQuery}$jitsiModal,jQuerymodalelementinwhichweaddtheJitsiroom
      *@returns{JitsiRoom}thenewlycreatedJitsiroom
      */
    _joinJitsiRoom:asyncfunction($parentNode){
        letjitsiRoom=awaitthis._createJitsiRoom(this.roomName,$parentNode);

        if(this.defaultUsername){
            jitsiRoom.executeCommand("displayName",this.defaultUsername);
        }

        lettimeoutCall=null;
        constupdateParticipantCount=(joined)=>{
            this.allParticipantIds=Object.keys(jitsiRoom._participants).sort();
            //ifwereachedthemaximumcapacity,updateimmediatelytheparticipantcount
            consttimeoutTime=this.allParticipantIds.length>=this.maxCapacity?0:2000;

            //wecleartheoldtimeouttobesuretocallitonlyonceeach2seconds
            //(soif2participantsjoin/leaveinthisinterval,wewillperformonly
            //oneHTTPrequestforboth).
            clearTimeout(timeoutCall);
            timeoutCall=setTimeout(()=>{
                this.allParticipantIds=Object.keys(jitsiRoom._participants).sort();
                if(this.participantId===this.allParticipantIds[0]){
                    //onlythefirstparticipantoftheroomsendthenewparticipant
                    //countsoweavoidtosendtomanyHTTPrequests
                    this._updateParticipantCount(this.allParticipantIds.length,joined);
                }
            },timeoutTime);
        };

        jitsiRoom.addEventListener('participantJoined',()=>updateParticipantCount(true));
        jitsiRoom.addEventListener('participantLeft',()=>updateParticipantCount(false));

        //updatetheparticipantcountwhenjoiningtheroom
        jitsiRoom.addEventListener('videoConferenceJoined',async(event)=>{
            this.participantId=event.id;
            updateParticipantCount(true);
            $('.o_wjitsi_chat_room_loading').addClass('d-none');

            //recheckiftheroomisnotfull
            if(this.checkFull&&this.allParticipantIds.length>this.maxCapacity){
                clearTimeout(timeoutCall);
                jitsiRoom.executeCommand('hangup');
                window.location.reload();
            }
        });

        //updatetheparticipantcountwhenusingthe"Leave"button
        jitsiRoom.addEventListener('videoConferenceLeft',async(event)=>{
            this.allParticipantIds=Object.keys(jitsiRoom._participants)
            if(!this.allParticipantIds.length){
                //bypassthechecksandtimerofupdateParticipantCount
                this._updateParticipantCount(this.allParticipantIds.length,false);
            }
        });

        returnjitsiRoom;
    },

    /**
      *PerformanHTTPrequesttoupdatetheparticipantcountontheserverside.
      *
      *@private
      *@param{integer}count,currentnumberofparticipantintheroom
      *@param{boolean}joined,trueifsomeonejoinedtheroom
      */
    _updateParticipantCount:asyncfunction(count,joined){
        awaitthis._rpc({
            route:'/jitsi/update_status',
            params:{
                room_name:this.roomName,
                participant_count:count,
                joined:joined,
            },
        });
    },


    //--------------------------------------------------------------------------
    //Private
    //--------------------------------------------------------------------------

    /**
      *RedirectontheJitsimobileapplicationifweareonmobile.
      *
      *@private
      *@param{string}roomName
      *@returns{boolean}trueiswewereredirectedtothemobileapplication
      */
    _openMobileApplication:asyncfunction(roomName){
        if(config.device.isMobile){
            //weareonmobile,opentheroomintheapplication
            window.location=`intent://${this.jitsiServer}/${roomName}#Intent;scheme=org.jitsi.meet;package=org.jitsi.meet;end`;
            returntrue;
        }
        returnfalse;
    },

    /**
      *CreateaJitsiroomonthegivenDOMelement.
      *
      *@private
      *@param{string}roomName
      *@param{jQuery}$parentNode
      *@returns{JitsiRoom}thenewlycreatedJitsiroom
      */
    _createJitsiRoom:asyncfunction(roomName,$parentNode){
      awaitthis._loadJisti();
        constoptions={
            roomName:roomName,
            width:"100%",
            height:"100%",
            parentNode:$parentNode[0],
            configOverwrite:{disableDeepLinking:true},
        };
        returnnewwindow.JitsiMeetExternalAPI(this.jitsiServer,options);
    },

    /**
      *LoadtheJitsiexternallibraryifnecessary.
      *
      *@private
      */
    _loadJisti:asyncfunction(){
      if(!window.JitsiMeetExternalAPI){
          await$.ajax({
              url:`https://${this.jitsiServer}/external_api.js`,
              dataType:"script",
          });
      }
    },
});

returnpublicWidget.registry.ChatRoom;

});
